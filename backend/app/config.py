import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'prices.db')}"
    app_name: str = "Healthcare Price Transparency"


settings = Settings()
