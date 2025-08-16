import openai
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, config):
        self.config = config
        self.client = openai.AsyncOpenAI(api_key=self.config.get('api_key'))
        self.model = config.model.name
        self.temperature = config.model.temperature
    
    async def _make_llm_request(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Make a request to the language model"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.config.model.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"LLM request failed: {e}")
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> Any:
        """Process the agent's task"""
        pass