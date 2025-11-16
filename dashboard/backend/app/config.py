from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://ics_user:ics_password@localhost:5432/ics_threat_detection"
    )
    DB_ECHO: bool = False

    # Redis (Context Buffer)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "ics_threat_detection"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"

    # FL Server
    FL_SERVER_URL: str = "http://localhost:8080"
    FL_MIN_CLIENTS: int = 3

    # Demo Mode
    DEMO_MODE: bool = True
    SEED_DATA_ON_STARTUP: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
