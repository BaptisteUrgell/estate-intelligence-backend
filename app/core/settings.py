from enum import StrEnum

from pydantic import BaseModel, Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    TEST = "test"
    DEV = "dev"


class AppSettings(BaseModel):
    environment: Environment = Environment.DEV
    log_level: str = "INFO"


class DatabaseSettings(BaseModel):
    postgres_server: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "immobilier"

    @computed_field
    @property
    def sqlalchemy_database_uri(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_server,
            port=self.postgres_port,
            path=self.postgres_db,
        )


class Settings(BaseSettings):
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    app: AppSettings = Field(default_factory=AppSettings)

    # Application parameters
    resolutions: list[int] = [25, 38, 50, 75, 100]
    default_resolution: int = 50

    # default map coordinates (toulouse)
    center_lat: float = 43.6047
    center_lon: float = 1.3900

    installed_domains: list[str] = ["market_data", "profiles", "searches", "map_configs"]

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
