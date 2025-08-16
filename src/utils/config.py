import yaml
import os
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

class ModelConfig(BaseModel):
    provider: str = "openai"
    name: str = "google/gemma-3-4b-it:free" #"gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 8000
    timeout: int = 60

    @validator("provider")
    def validate_provider(cls, v):
        if v not in ["openai", "anthropic"]:
            raise ValueError("Provider must be 'openai' or 'anthropic'")
        return v

class ResearchConfig(BaseModel):
    max_iterations: int = 2
    max_sources_per_query: int = 10
    min_source_reliability: float = 0.7
    search_engines: list = ["google", "arxiv", "wikipedia"]
    concurrent_requests: int = 3

class VisualizationConfig(BaseModel):
    chart_resolution: list = [1600, 900]
    style_template: str = "academic"
    color_palette: str = "viridis"
    max_charts_per_report: int = 8
    supported_formats: list = ["png", "svg", "pdf", "html"]

class SecurityConfig(BaseModel):
    rate_limit_requests_per_minute: int = 30
    allowed_origins: list = ["http://localhost:8000"]

class SystemConfig(BaseModel):
    system: dict = Field(default_factory=dict)
    model: ModelConfig = Field(default_factory=ModelConfig)
    research: ResearchConfig = Field(default_factory=ResearchConfig)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    @classmethod
    def from_yaml(cls, config_path: str) -> "SystemConfig":
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)   # Load YAML into a Python dict
        return cls(**config_data)             # Pass dict keys as arguments to class


def load_config(config_path: str = "configs/base.yaml") -> SystemConfig:
    load_dotenv()
    required_env_vars = ["OPENAI_API_KEY", "JWT_SECRET_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    return SystemConfig.from_yaml(config_path)