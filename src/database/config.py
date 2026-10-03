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
    # Se estiver usando Supabase, coloque a DATABASE_URL completa aqui
    # Exemplo: postgresql+psycopg2://postgres.zdjbqwaosayfqjihmzty:senha@aws-1-sa-east-1.pooler.supabase.com:6543/postgres
    SCHEME: str = "postgresql+psycopg2"
    HOST: str = "localhost"
    USER: str = "postgres"
    PORT: int = 5432
    DATABASE_NAME: str = "clinica_db"
    PASSWORD: str = "postgres"

    # AI Configuration
    AI_API_KEY: str = "mock-key"
    AI_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o-mini"

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8001/google/auth/callback"

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

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
        # Em prod, usa DATABASE_URL se estiver definida (melhor para Supabase)
        # Caso contrário, constrói a URI com os componentes
        if self.DATABASE_URL and not self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL
        return f"{self.SCHEME}://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE_NAME}"


settings = Settings()  # type: ignore
