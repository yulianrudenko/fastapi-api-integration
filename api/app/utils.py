from openai import AsyncOpenAI
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import NoAuthAuthenticator
import tensorflow as tf
import numpy as np
from PIL import Image
import requests
from io import BytesIO


from .config import settings


client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
authenticator = NoAuthAuthenticator()
assistant = AssistantV2(
    version="2020-04-01",
    authenticator=authenticator
)
tf_model = tf.keras.applications.InceptionV3(weights='imagenet', include_top=True)


async def process_text_openai(text: str) -> dict[str, str | None]:
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": text}
            ]
        )
        openai_response = response["choices"][0]["message"]["content"]
        response = openai_response
    except:
        response = None
    return {"provider": "openai", "response": response}


async def process_text_ibm(text: str) -> dict[str, str | None]:
    try:
        print(settings.IBM_ASSISTANT_ID)
        response = assistant.message(
            session_id=settings.IBM_SESSION_ID,
            assistant_id=settings.IBM_ASSISTANT_ID,
            input={"text": text}
        ).get_result()
        response = response["output"]["text"][0]
    except:
        response = None
    return {"provider": "ibm", "response": response}


def classify_image(image_url) -> dict:
    # Load image from URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((299, 299))  # Resize image to match model input size

    # Convert image to numpy array and preprocess for model input
    img_array = np.array(img)
    img_array = tf.keras.applications.inception_v3.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

    # Perform inference using the pre-trained model
    predictions = tf_model.predict(img_array)
    # Decode the predictions
    decoded_predictions = tf.keras.applications.inception_v3.decode_predictions(predictions, top=3)[0]
    result = list()
    for prediction in decoded_predictions:
        result.append({
            'type': prediction[1],
            'chance': prediction[2]
        })
    return result
