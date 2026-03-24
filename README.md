# QiskitSage 🤖🔬

An intelligent code review tool that uses Anthropic's Claude to analyze Qiskit (quantum computing framework) pull requests and identify potential issues.

## Overview

QiskitSage is a specialized PR review system designed specifically for the Qiskit ecosystem. It orchestrates multiple AI agents to perform comprehensive code analysis on GitHub pull requests, focusing on:

- **Semantic correctness** - Detects quantum algorithm regressions via fidelity testing
- **FFI safety** - Identifies unsafe Rust FFI patterns and panic risks
- **Performance** - Flags O(n³+) loops and scalability concerns
- **Syntax** - Enforces Google-style docstrings, type hints, and deprecation practices
- **Compliance** - Checks license headers and copyright
- **Historical analysis** - Analyzes commit history for regression patterns

The system builds a complete **Context Graph** of the PR, including all changed files, callers, dependencies, and historical context, then feeds this to specialized Claude-powered agents for deep analysis.

## Architecture

QiskitSage uses a 4-stage pipeline to build contextual understanding:

```
Stage 1: Skeleton from diff → Stage 2: AST parsing + history → Stage 3: Caller search → Stage 4: Caller content

Outputs: ContextGraph with 73 fields covering modules, functions, dependencies, and impact analysis
```

### Key Components

- **ContextBuilder** - Orchestrates all 4 stages of context graph construction
- **GitHubClient** - Fetches PR data, files, commit history, and caller relationships
- **PythonASTAnalyser** - Parses Python AST to extract function metadata and call graphs
- **RustAnalyser** - Parses Rust code (using tree-sitter or regex fallback)
- **SemanticChecker** - Runs quantum fidelity probes to detect algorithm regressions
- **Agents** - Specialized Claude-powered reviewers (SA-SYN, SA-PERF, SA-SEM, SA-FFI, SA-JUDGE)

## Installation

### Prerequisites

- Python 3.9+
- Anthropic API key (Claude access)
- GitHub personal access token

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd qiskit2.0
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.dist .env
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GITHUB_TOKEN=your_github_token_here
```

### Requirements

```
anthropic>=0.25.0       # Claude API client
PyGithub>=2.1.1         # GitHub API client
qiskit>=1.2.0           # Quantum computing framework
numpy>=1.26.0           # Numerical computing
tree-sitter>=0.21.0     # Rust AST parsing
tree-sitter-rust>=0.21.0
dotenv>=1.0.0          # Environment variable management
pytest>=7.4.0          # Testing framework
```

## Configuration

Key settings in `qiskitsage/config.py`:

```python
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']

LLM_MODEL = 'claude-sonnet-4-20250514'
LLM_MAX_TOKENS = 4096
LLM_TEMPERATURE = 0.1

MIN_CONFIDENCE = 0.70           # Minimum confidence threshold for findings
MAX_FINDINGS = 12              # Maximum findings per agent
FIDELITY_THRESHOLD = 0.9999    # Quantum fidelity regression threshold
MAX_CALLER_SEARCHES = 5        # Limit GitHub API calls
MAX_COMMIT_HISTORY = 10        # Commits per file for historical context
```

## Usage

### Basic Usage

```python
from qiskitsage.context_builder import ContextBuilder
from qiskitsage.agents.syntax_agent import SyntaxAgent
from qiskitsage.agents.semantic_agent import SemanticAgent
from qiskitsage.agents.performance_agent import PerformanceAgent
from qiskitsage.agents.ffi_agent import FFIAgent
from qiskitsage.agents.judge_agent import JudgeAgent

# Build context graph from PR URL
builder = ContextBuilder()
graph = builder.build("https://github.com/Qiskit/qiskit/pull/12345")

# Run specialized agents
syntax_findings = SyntaxAgent().review(graph)
semantic_findings = SemanticAgent().review(graph)
performance_findings = PerformanceAgent().review(graph)
ffi_findings = FFIAgent().review(graph)

# Generate final report
all_findings = syntax_findings + semantic_findings + performance_findings + ffi_findings
result = JudgeAgent().generate_report(graph, all_findings)

print(result.comment_markdown)
```

### Context Graph Anatomy

The built `ContextGraph` contains:

```python
{
  "pr_number": 12345,
  "pr_title": "PR title",
  "base_sha": "abc123",           # Base commit
  "head_sha": "def456",           # Head commit

  "modules": {                     # All module files
    "qiskit/transpiler/foo.py": {
      "file_path": "...",
      "language": "python",
      "full_content": "...",      # Complete file at base_sha
      "functions": ["Foo.bar", ...],
      "commit_history": [...],     # Last 10 commits
      "regression_count": 2,       # # of fix/regression commits
      "is_changed": True
    }
  }
}
```

## Error Fixes & Known Issues

### Critical: Missing __init__.py content

**Issue**: The `qiskitsage/__init__.py` file is empty, causing import errors.

**Fix**: Add package-level exports:

```python
# qiskitsage/__init__.py
"""QiskitSage - AI-powered PR review for Qiskit."""

from .context_builder import ContextBuilder
from . import config
from . import models
from . import context_graph

__version__ = "0.1.0"
__all__ = ["ContextBuilder", "config", "models", "context_graph"]
```

### Agent Pipeline Structure

**Issue**: No centralized orchestration of agents.

**Solution**: Create a main `ReviewOrchestrator`:

```python
# qiskitsage/orchestrator.py
class ReviewOrchestrator:
    def __init__(self):
        self.builder = ContextBuilder()
        self.agents = [
            SyntaxAgent(),
            PerformanceAgent(),
            SemanticAgent(),
            FFIAgent()
        ]
        self.judge = JudgeAgent()

    def review_pr(self, pr_url: str) -> ReviewResult:
        graph = self.builder.build(pr_url)
        findings = []
        for agent in self.agents:
            if self._should_run(agent, graph):
                findings.extend(agent.review(graph))
        return self.judge.generate_report(graph, findings)
```

### Rust AST Dependencies

**Issue**: Optional tree-sitter dependency may not be installed.

**Fix**: The code already handles this with graceful fallback to regex parsing in `RustAnalyser._analyse_with_fallback()`.

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Add test configuration as needed (test files are currently empty).

## Fidelity Probes

The SemanticAgent runs quantum circuits to detect algorithm regressions:

**Default Probes**:
- `bell_transpile` - Basic Bell state transpilation
- `controlled_subgate` - Controlled gate operations
- `unitary_synthesis` - Custom unitary synthesis
- `gate_control` - Gate control operations
- `qft_round_trip` - Quantum Fourier Transform

**Probe Selection Logic**:
```python
probes = ['bell_transpile']  # Always
if graph.has_transpiler_changes:
    probes += ['controlled_subgate', 'qft_round_trip']
if graph.has_synthesis_changes:
    probes += ['unitary_synthesis', 'gate_control']
```

## GitHub Integration

### Rate Limiting

The system respects GitHub API limits:
- `MAX_CALLER_SEARCHES = 5` - Limits code search API calls
- Uses `concurrent.futures.ThreadPoolExecutor` for parallel operations
- Each file fetch/history retrieval runs in parallel

### Permissions Required

Your `GITHUB_TOKEN` needs:
- `repo` scope - Read repository contents
- `pull_requests` scope - Read PR data

## Expected Output

The system outputs a `ReviewResult` containing:

```python
ReviewResult(
  pr_url="https://github.com/Qiskit/qiskit/pull/12345",
  pr_number=12345,
  findings=[...],  # All findings from all agents
  total_findings=15,
  critical_count=2,
  high_count=5,
  semantic_regression_detected=True,  # If fidelity tests failed
  ffi_risk_detected=False,
  agents_run=['SA-SYN', 'SA-PERF', 'SA-SEM'],
  execution_time_seconds=125.5,
  comment_markdown="### 🚨 Critical Regression Detected..."
)
```

The JudgeAgent generates a structured Markdown comment suitable for posting directly to GitHub PRs.

## Limitations

1. **GitHub API Limits** - Caller search limited to 5 public functions
2. **Token Limits** - Context size trimmed to fit Claude's 4096 token limit
3. **Probe Coverage** - Limited quantum circuit probes (add more as needed)
4. **Rate Limiting** - No automatic retry/backoff for GitHub API

## Future Enhancements

1. Add more quantum fidelity probes for different Qiskit modules
2. Implement GitHub PR comment posting via API
3. Add support for other quantum frameworks
4. Build web dashboard for review results
5. Implement incremental analysis for PR updates

## Contributing

1. Ensure all Python files follow Google Docstring style
2. Add type hints for all public functions
3. Maintain test coverage for new features
4. Update this README for architectural changes

## License

[Specify license - currently empty in codebase]

## Support

For issues or questions:
1. Check existing issues on GitHub
2. Review the QiskitSage_ClaudeCode_Prompt.md file for prompt engineering details
3. Contact maintainers
