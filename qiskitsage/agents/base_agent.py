from abc import ABC, abstractmethod
from typing import List
from ..context_graph import ContextGraph
from ..models import Finding

class BaseAgent(ABC):
    agent_id: str = 'BASE'

    def __init__(self):
        from openai import OpenAI
        from .. import config
        self.client = OpenAI(
            base_url=config.OLLAMA_BASE_URL,
            api_key="ollama",  # Ollama doesn't require a real key
        )
        self.model = config.OLLAMA_MODEL
        self.max_tokens = config.LLM_MAX_TOKENS
        self.temperature = config.LLM_TEMPERATURE

    def _llm_call(self, system: str, user_prompt: str) -> str:
        """
        Unified LLM call using OpenAI-compatible Ollama endpoint.
        Returns the raw text content of the response.
        """
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ]
        )
        return resp.choices[0].message.content or ""

    @abstractmethod
    def review(self, graph: ContextGraph) -> List[Finding]:
        ...

    def _safe_review(self, graph: ContextGraph) -> List[Finding]:
        """Safe wrapper that catches all exceptions."""
        try:
            return self.review(graph)
        except Exception as e:
            print(f'[{self.agent_id}] Error: {e}')
            return []
