from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GeneralSettings(BaseModel):
    project_name: str = "recipe"


class DatabaseSettings(BaseModel):
    user: str = "postgres"
    name: str = "recipe"
    host: str = "localhost"
    port: int = 5432
    password: str = "postgres"

    @property
    def user_pass(self) -> str:
        return f"{self.user}:{self.password}" if self.password else self.user

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user_pass}@{self.host}:{self.port}/{self.name}"
        )


model_config = SettingsConfigDict(
    env_file=(".env"), env_prefix="API__", env_nested_delimiter="__"
)


class Settings(BaseSettings):
    model_config = model_config
    debug: bool = True
    db: DatabaseSettings = Field(default_factory=lambda: DatabaseSettings())


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
