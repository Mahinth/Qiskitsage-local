# QiskitSage 🤖🔬

An intelligent code review tool that uses Anthropic's Claude to analyze Qiskit pull requests and identify potential issues.

## Overview

QiskitSage is a specialized PR review system for the Qiskit ecosystem. It orchestrates multiple AI agents to perform comprehensive code analysis on GitHub pull requests, detecting:

- **Semantic correctness** - Detects quantum algorithm regressions via fidelity testing
- **FFI safety** - Identifies unsafe Rust FFI patterns and panic risks
- **Performance** - Flags O(n³+) loops and scalability concerns
- **Syntax** - Enforces Google-style docstrings, type hints, and deprecation practices

## Architecture

QiskitSage uses a 4-stage pipeline:

```
Stage 1: Skeleton from diff → Stage 2: AST parsing + history → Stage 3: Caller search → Stage 4: Caller content
```

**Key Components:**
- **ContextBuilder** - Orchestrates context graph construction
- **GitHubClient** - Fetches PR data and commit history
- **PythonASTAnalyser** - Parses Python AST for function metadata
- **RustAnalyser** - Parses Rust code (with regex fallback)
- **Agents** - Specialized Claude-powered reviewers (SA-SYN, SA-PERF, SA-SEM, SA-FFI)

## Installation

### Prerequisites

- Python 3.9+
- Anthropic API key
- GitHub personal access token

### Setup

1. Clone and install:
```bash
git clone <repository-url>
cd qiskit2.0
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.dist .env
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
```

### Dependencies

```
anthropic>=0.25.0
PyGithub>=2.1.1
qiskit>=1.2.0
numpy>=1.26.0
tree-sitter>=0.21.0
tree-sitter-rust>=0.21.0
python-dotenv>=1.0.0
pytest>=7.4.0
```

## Configuration

Key settings in `qiskitsage/config.py`:

```python
LLM_MODEL = 'claude-sonnet-4-20250514'
LLM_MAX_TOKENS = 4096
LLM_TEMPERATURE = 0.1
MIN_CONFIDENCE = 0.70
MAX_FINDINGS = 12
FIDELITY_THRESHOLD = 0.9999
MAX_CALLER_SEARCHES = 5
MAX_COMMIT_HISTORY = 10
```

## Usage

### CLI

```bash
python main.py --pr "https://github.com/Qiskit/qiskit/pull/12345"
python main.py --pr "https://github.com/Qiskit/qiskit/pull/12345" --verbose
```

### Python API

```python
from qiskitsage.context_builder import ContextBuilder
from qiskitsage.agents.syntax_agent import SyntaxAgent
from qiskitsage.agents.semantic_agent import SemanticAgent
from qiskitsage.agents.performance_agent import PerformanceAgent
from qiskitsage.agents.ffi_agent import FFIAgent

builder = ContextBuilder()
graph = builder.build("https://github.com/Qiskit/qiskit/pull/12345")

findings = []
findings.extend(SyntaxAgent().review(graph))
findings.extend(SemanticAgent().review(graph))
findings.extend(PerformanceAgent().review(graph))
findings.extend(FFIAgent().review(graph))
```

## Quantum Fidelity Probes

The SemanticAgent runs quantum circuits to detect regressions:

- `bell_transpile` - Bell state transpilation
- `controlled_subgate` - Controlled gate operations
- `unitary_synthesis` - Custom unitary synthesis
- `qft_round_trip` - Quantum Fourier Transform

## Output Format

Returns a `ReviewResult` with:
- `findings` - All detected issues across agents
- `critical_count`, `high_count` - Issue severity counts
- `semantic_regression_detected` - Fidelity test failures
- `comment_markdown` - GitHub-ready review comment

## Testing

```bash
pytest tests/
```

## Limitations

1. GitHub API call limits for caller searches
2. Claude context size trimmed to 4096 tokens
3. Limited quantum circuit probes
4. No automatic retry for rate limits

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

For issues, check:
- Existing GitHub issues
- QiskitSage_ClaudeCode_Prompt.md for prompt details


## Architecture

QiskitSage uses a 4-stage pipeline:

```
Stage 1: Skeleton from diff → Stage 2: AST parsing + history → Stage 3: Caller search → Stage 4: Caller content
```

**Key Components:**
- **ContextBuilder** - Orchestrates context graph construction
- **GitHubClient** - Fetches PR data and commit history
- **PythonASTAnalyser** - Parses Python AST for function metadata
- **RustAnalyser** - Parses Rust code (with regex fallback)
- **Agents** - Specialized Claude-powered reviewers (SA-SYN, SA-PERF, SA-SEM, SA-FFI)

## Installation

### Prerequisites

- Python 3.9+
- Anthropic API key
- GitHub personal access token

### Setup

1. Clone and install:
```bash
git clone <repository-url>
cd qiskit2.0
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.dist .env
```

Edit `.env` and add your API keys:
```env
ANTHROPIC_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
```

### Dependencies

```
anthropic>=0.25.0
PyGithub>=2.1.1
qiskit>=1.2.0
numpy>=1.26.0
tree-sitter>=0.21.0
tree-sitter-rust>=0.21.0
python-dotenv>=1.0.0
pytest>=7.4.0
```

## Configuration

Key settings in `qiskitsage/config.py`:

```python
LLM_MODEL = 'claude-sonnet-4-20250514'
LLM_MAX_TOKENS = 4096
LLM_TEMPERATURE = 0.1
MIN_CONFIDENCE = 0.70
MAX_FINDINGS = 12
FIDELITY_THRESHOLD = 0.9999
MAX_CALLER_SEARCHES = 5
MAX_COMMIT_HISTORY = 10
```

## Usage

### CLI

```bash
python main.py --pr "https://github.com/Qiskit/qiskit/pull/12345"
python main.py --pr "https://github.com/Qiskit/qiskit/pull/12345" --verbose
```

### Python API

```python
from qiskitsage.context_builder import ContextBuilder
from qiskitsage.agents.syntax_agent import SyntaxAgent
from qiskitsage.agents.semantic_agent import SemanticAgent
from qiskitsage.agents.performance_agent import PerformanceAgent
from qiskitsage.agents.ffi_agent import FFIAgent

builder = ContextBuilder()
graph = builder.build("https://github.com/Qiskit/qiskit/pull/12345")

findings = []
findings.extend(SyntaxAgent().review(graph))
findings.extend(SemanticAgent().review(graph))
findings.extend(PerformanceAgent().review(graph))
findings.extend(FFIAgent().review(graph))
```

## Quantum Fidelity Probes

The SemanticAgent runs quantum circuits to detect regressions:

- `bell_transpile` - Bell state transpilation
- `controlled_subgate` - Controlled gate operations
- `unitary_synthesis` - Custom unitary synthesis
- `qft_round_trip` - Quantum Fourier Transform

## Output Format

Returns a `ReviewResult` with:
- `findings` - All detected issues across agents
- `critical_count`, `high_count` - Issue severity counts
- `semantic_regression_detected` - Fidelity test failures
- `comment_markdown` - GitHub-ready review comment

## Testing

```bash
pytest tests/
```

## Limitations

1. GitHub API call limits for caller searches
2. Claude context size trimmed to 4096 tokens
3. Limited quantum circuit probes
4. No automatic retry for rate limits

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

For issues, check:
- Existing GitHub issues
- QiskitSage_ClaudeCode_Prompt.md for prompt details
