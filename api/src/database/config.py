import os

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)


print(env_path)


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    ENVIRONMENT: str = "dev"

    DOMAIN: str = "localhost"

    DATABASE_URL: str = "sqlite:///./clinica.db"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SECRET_KEY: str = "dev-secret-key-change-in-production"

    ALGORITHM: str = "HS256"

    # PostgreSQL for production (optional for dev)

    SCHEME: str = "postgresql+psycopg2"
    HOST: str = "localhost"
    USER: str = "postgres"
    PORT: int = 5432
    DATABASE_NAME: str = "clinica_db"
    PASSWORD: str = "postgres"

    # AI Configuration
    AI_API_KEY: str = ""
    AI_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o-mini"

    @computed_field
    @property
    def server_host(self) -> str:

        if self.ENVIRONMENT == "dev":

            return f"http://{self.DOMAIN}"

        return f"https://{self.DOMAIN}"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str | PostgresDsn:

        if self.ENVIRONMENT == "dev":

            return self.DATABASE_URL

        else:

            return f"{self.SCHEME}://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE_NAME}"


settings = Settings()  # type: ignore
