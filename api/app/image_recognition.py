import tensorflow as tf
import numpy as np
from PIL import Image
import requests
from io import BytesIO

# Load pre-trained TensorFlow model (for example, InceptionV3)
model = tf.keras.applications.InceptionV3(weights='imagenet', include_top=True)

# Define a function to perform image classification
def classify_image(image_url):
    # Load image from URL
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img = img.resize((299, 299))  # Resize image to match model input size
    
    # Convert image to numpy array and preprocess for model input
    img_array = np.array(img)
    img_array = tf.keras.applications.inception_v3.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    
    # Perform inference using the pre-trained model
    predictions = model.predict(img_array)
    
    # Decode the predictions
    decoded_predictions = tf.keras.applications.inception_v3.decode_predictions(predictions, top=3)[0]
    return decoded_predictions
    # Format and return the results
    results = [{'label': label, 'description': description, 'probability': float(probability)} 
               for _, label, description, probability in decoded_predictions]
    return results

# Example usage
image_url = 'https://t0.gstatic.com/licensed-image?q=tbn:ANd9GcTZCSmCzmIPm0up8wmW566cK5w3sSTUChT5UnaU3VnFxrHwoRNSnks0xUBmj2r2oeJk'
results = classify_image(image_url)
print(results)