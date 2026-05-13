from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field



class Settings(BaseSettings):
    llm_url:str = Field(default="http://127.0.0.1:8080",description="URL of the llamacpp LLM server")
    llm_model: str = Field(default="llama3.2:1b", description="Model to use")  
    timeout: float = Field(default=30.0, description="Request timeout in seconds")

    # Monitoring Configuration
    monitor_interval: int = Field(default=30, description="Seconds between health checks")
    test_prompt: str = Field(default="What is 2+2?", description="Prompt for health check")
    expected_answer: str = Field(default="4", description="Expected answer substring")  

    # Application Configuration
    app_name: str = Field(default="LLM Health Monitor", description="Application name")
    log_level: str = Field(default="INFO", description="Logging level")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }





settings: Settings = Settings()