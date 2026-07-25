from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    

#Vector Database

    qdrant_host: str
    qdrant_port: int
    collection_name: str


#Embedding

    embedding_model: str


#LLM

    groq_api_key: str
    llm_model: str


#Retrieval

    search_mode: str = "semantic"
    top_k: int = 5


#Chunking

    chunk_size: int = 1000
    chunk_overlap: int = 200


#Logging
    
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()