from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    DB_URL: str
    TESTS_DB_URL: str
    
    # OAuth
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    AUTH0_DOMAIN: str
    AUTH0_REDIRECT_URI: str

    # API
    OPENAI_API_KEY: str
    IBM_SESSION_ID: str
    IBM_ASSISTANT_ID: str

settings = Settings()
