import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from code import load_dotenv

class ModelConfig(BaseModel):
    provider: str = "google" #"openai"
    name: str = "google/gemma-3-4b-it:free" #"gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 30

class ResearchConfig(BaseModel):
    max_iterations: int = 3
    max_sources_per_query: int = 15
    min_source_reliability: float = 0.6
    search_engines: list = ["google", "arxiv", "wikipedia"]
    concurrent_requests: int = 5

class VisualizationConfig(BaseModel):
    chart_resolution: list = [1200, 800]
    style_template: str = "academic"
    color_palette: str = "viridis"
    max_charts_per_report: int = 10
    supported_formats: list = ["png", "svg", "pdf"]

class SystemConfig(BaseModel):
    """Main configuration class for the entire system"""
    model: ModelConfig = Field(default_factory=ModelConfig)
    research: ResearchConfig = Field(default_factory=ResearchConfig)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    
    @classmethod
    def from_yaml(cls, config_path: str) -> "SystemConfig":
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)

def load_config(config_path: str = "configs/base.yaml") -> SystemConfig:
    """Load system configuration and environment variables"""
    # Load environment variables
    load_dotenv()
    
    # Validate required environment variables
    required_env_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    # Load configuration
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    return SystemConfig.from_yaml(config_path)