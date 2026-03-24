import json
from typing import List
from .base_agent import BaseAgent
from ..models import Finding, Severity, Category
from ..context_graph import ContextGraph
from ..prompts.syntax_prompt import build_syntax_user_prompt, SYNTAX_SYSTEM_PROMPT

class SyntaxAgent(BaseAgent):
    agent_id = 'SA-SYN'

    def review(self, graph: ContextGraph) -> List[Finding]:
        python_files = [fp for fp in graph.changed_files if graph.modules[fp].language == 'python']
        if not python_files:
            return []

        # Build prompt from graph
        user_prompt = build_syntax_user_prompt(graph)

        # Call Anthropic API
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=SYNTAX_SYSTEM_PROMPT,
            messages=[
                {'role': 'user', 'content': user_prompt}
            ]
        )

        # Parse JSON response
        if isinstance(resp, str):
            content = resp
        elif hasattr(resp, 'content') and isinstance(resp.content, list) and len(resp.content) > 0:
            # Use getattr to safely extract text, fallback to str representation
            content = getattr(resp.content[0], 'text', str(resp.content[0]))
        else:
            content = str(resp)

        # Strip ```json fences if present
        if content.strip().startswith('```'):
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            else:
                content = content.split('```')[1].split('```')[0].strip()

        try:
            data = json.loads(content.strip())
            findings = []
            for f in data.get('findings', []):
                findings.append(Finding(
                    agent_id=self.agent_id,
                    severity=Severity(f['severity']),
                    category=Category.SYNTAX,
                    file=f['file'],
                    line=f.get('line'),
                    title=f['title'],
                    description=f['description'],
                    suggestion=f['suggestion'],
                    evidence=f['evidence'],
                    confidence=float(f.get('confidence', 0.5))
                ))
            return findings
        except json.JSONDecodeError:
            print(f'[{self.agent_id}] JSON parse error')
            return []
