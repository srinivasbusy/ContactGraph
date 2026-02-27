from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    google_client_id: str = ""
    firebase_project_id: str = ""
    secret_key: str = "change-this-secret-key-in-production"
    allowed_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
