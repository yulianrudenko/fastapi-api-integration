import jwt
import asyncio
import requests

from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    Body,
    Query,
    status
)
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode

from . import models
from . import schemas
from .db import get_db
from .auth import create_access_token, get_current_user
from .config import settings
from .utils import process_text_openai, process_text_ibm, classify_image

app = FastAPI()


@app.get("/authenticate", status_code=status.HTTP_200_OK)
def authenticate(
    code: str = Query(description="Authorization code retrieved from auth0"),
    db: Session = Depends(get_db)
) -> schemas.LoginCredentials:
    """
    Exchange authorization code for access and ID tokens, validate if both are valid.

    Using access token fetch user information from OAuth provider.
    If account with retrieved email does not exists create one.

    Finally return access token (JWT) and user data.
    """
    data = {
        "grant_type": "authorization_code",
        "client_id": settings.AUTH0_CLIENT_ID,
        "client_secret": settings.AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.AUTH0_REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(f"https://{settings.AUTH0_DOMAIN}/oauth/token", data=data, headers=headers)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        access_token_data = response.json()
        access_token = access_token_data["access_token"]
        id_token = access_token_data["id_token"]
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error fetching access token.")

    try:
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})
        # Verify issuer
        if decoded_token["iss"] != f"https://{settings.AUTH0_DOMAIN}/":
            raise ValueError("Invalid issuer")
        # Verify audience
        if decoded_token["aud"] != settings.AUTH0_CLIENT_ID:
            raise ValueError("Invalid audience")
    except (jwt.DecodeError, jwt.ExpiredSignatureError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")

    # Fetch user email and name from OAuth provider
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"https://{settings.AUTH0_DOMAIN}/userinfo", headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")
    json = response.json()
    user_email = json["email"]
    name = json["name"]

    # Check if user is registered, if not create an account
    user_obj = db.query(models.User).filter(models.User.email == user_email).first()
    if not user_obj:
        user_obj = models.User(email=user_email, name=name)
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)
    return {
        "user": user_obj.__dict__,
        "access_token": create_access_token(user_id=user_obj.id),
    }


@app.get("/auth0", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
def auth0():
    """
    Redirect to external OAuth authentication form.
    """
    return RedirectResponse(
        f"https://{settings.AUTH0_DOMAIN}/authorize?"
        + urlencode(
            {
                "audience": f"https://{settings.AUTH0_DOMAIN}/api/v2/",
                "client_id": settings.AUTH0_CLIENT_ID,
                "response_type": "code",
                "redirect_uri": settings.AUTH0_REDIRECT_URI,
                "scope": "openid profile email",
            }
        )
    )


@app.post("/process-text", status_code=status.HTTP_200_OK)
async def process_data(
    data_to_process: schemas.DataToProcess = Body(description="Data to process"),
    user_obj: models.User = Depends(get_current_user)
) -> list[schemas.TextResponse] | list[schemas.ImageResponse] | None:
    text = data_to_process.text
    if text is not None:
        tasks = []
        tasks.append(asyncio.create_task(process_text_openai(text=text)))
        tasks.append(asyncio.create_task(process_text_ibm(text=text)))
        results = await asyncio.gather(*tasks)
        return results
    if data_to_process.image_url is not None:
        return classify_image(image_url=data_to_process.image_url)
    return None
