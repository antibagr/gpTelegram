# mypy: disable-error-code="call-arg"
# pydantic_settings is not supported by mypy yet
# https://github.com/pydantic/pydantic/issues/5190

import pathlib

import pydantic
import pydantic_settings


class DatabaseSettings(pydantic_settings.BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: pydantic.SecretStr
    POSTGRES_NAME: str

    DB_TIMEOUT_SECONDS: int = 60

    @property
    def ASYNC_DATABASE_URI(self) -> pydantic.PostgresDsn:  # noqa: N802
        return pydantic.PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_NAME,
        )

    @property
    def DATABASE_URI(self) -> pydantic.PostgresDsn:  # noqa: N802
        return pydantic.PostgresDsn.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD.get_secret_value(),
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_NAME,
        )


class RedisSettings(pydantic_settings.BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: pydantic.SecretStr
    REDIS_HEALTH_CHECK_INTERVAL: int
    REDIS_STATE_TTL: int
    REDIS_DATA_TTL: int


class AppSettings(pydantic_settings.BaseSettings):
    ENVIRONMENT: str
    DEBUG: bool

    TELEGRAM_BOT_TOKEN: pydantic.SecretStr
    TELEGRAM_BOT_NAME: str

    LOCALES_DIR: pydantic.DirectoryPath = pathlib.Path("app", "api", "locales")
    I18N_DOMAIN: str = "messages"

    RATE_LIMIT: float = 0.5

    @property
    def is_production(self) -> bool:
        """Return True if the environment is production."""
        return self.ENVIRONMENT == "prod"


class Settings(
    AppSettings,
    DatabaseSettings,
    RedisSettings,
):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
