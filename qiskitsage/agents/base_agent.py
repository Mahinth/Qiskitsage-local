from abc import ABC, abstractmethod
from typing import List
from ..context_graph import ContextGraph
from ..models import Finding

class BaseAgent(ABC):
    agent_id: str = 'BASE'

    def __init__(self):
        from anthropic import Anthropic
        from .. import config
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.LLM_MODEL
        self.max_tokens = config.LLM_MAX_TOKENS
        self.temperature = config.LLM_TEMPERATURE

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
