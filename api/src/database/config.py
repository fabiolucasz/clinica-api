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
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SECRET_KEY: str
    ALGORITHM: str

    # PostgreSQL for production (optional for dev)
    SCHEME: str = "postgresql+psycopg2"
    HOST: str
    USER: str
    PORT: int
    DBNAME: str
    PASSWORD: str

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
            return f"{self.SCHEME}://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DBNAME}"


settings = Settings()  # type: ignore
