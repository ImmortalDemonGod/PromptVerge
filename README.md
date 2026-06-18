# PromptVerge MVP

> **An AI-powered system for transforming code into actionable tasks and research papers into knowledge quizzes.**

PromptVerge accelerates development workflows by automatically generating structured deliverables from raw inputs, enabling rapid iteration from concept to execution.

## 🎯 Mission Statement

PromptVerge bridges the gap between unstructured technical content and actionable work items. By leveraging AI-powered analysis, it transforms:

- **Source Code** → **Code Audits** → **Product Requirements** → **Deep Work Tasks**
- **Research Papers** → **Knowledge Graphs** → **Interactive Quizzes**

## ✨ Features

### Engineering Workflow
- **Automated Code Auditing**: Comprehensive analysis of code quality, security, and architecture
- **PRD Generation**: Structured product requirements based on code analysis and user stories
- **Task Creation**: Detailed deep work tasks with implementation steps and testing strategies

### Knowledge Workflow
- **Knowledge Graph Extraction**: Automatic extraction of relationships from scientific papers
- **Quiz Generation**: Interactive quizzes based on extracted knowledge for enhanced learning

## 🛠 Tech Stack

- **AI Framework**: [Marvin](https://github.com/prefecthq/marvin) for AI function orchestration
- **Workflow Engine**: [Prefect](https://prefect.io) for robust pipeline execution
- **Data Validation**: [Pydantic](https://pydantic.dev) for type-safe schema definitions
- **CLI Framework**: [Typer](https://typer.tiangolo.com) with [Rich](https://rich.readthedocs.io) for beautiful terminal output
- **Testing**: [pytest](https://pytest.org) with comprehensive mocking

## 🚀 Quick Start

### Prerequisites

```bash
# Ensure you have Python 3.9+ and uv installed
python --version  # Should be 3.9+
uv --version      # Should be installed
```

### Installation

```bash
# Clone and navigate to the PromptVerge directory
cd cultivation/systems/PromptVerge

# Install dependencies
uv pip install -e .
```

### Usage

#### Engineering Workflow: Code → Task

```bash
# Analyze a Python file and generate a complete workflow
uv run python -m promptverge run-engineering path/to/your_code.py "Your user story here"

# Example with the provided test fixture
uv run python -m promptverge run-engineering tests/fixtures/dummy_code.py "As a developer, I want to improve this function's robustness"
```

**Output**: Complete audit report, PRD, and actionable deep work task

#### Knowledge Workflow: Paper → Quiz

```bash
# Process a research paper and generate a knowledge quiz
uv run python -m promptverge run-knowledge path/to/paper.txt

# Example with the provided test fixture
uv run python -m promptverge run-knowledge tests/fixtures/dummy_paper.txt
```

**Output**: Interactive quiz based on extracted knowledge relationships

## 📁 Project Structure

```
PromptVerge/
├── promptverge/
│   ├── flows/                    # Prefect workflow definitions
│   │   ├── engineering_workflow.py
│   │   └── knowledge_workflow.py
│   ├── schemas/                  # Pydantic data models
│   │   ├── documents.py         # Core document schemas
│   │   └── validator.py         # Schema validation utilities
│   ├── main.py                  # CLI entry point
│   └── prompts.py              # AI prompt templates
├── tests/
│   ├── fixtures/               # Test data
│   └── test_e2e_flow.py       # End-to-end integration tests
├── docs/                       # Comprehensive documentation
└── outputs/                    # Generated artifacts
```

## 🧪 Testing

```bash
# Run the full test suite
uv run python -m pytest tests/ -v

# Run only fast tests (skip slow/e2e tests)
uv run python -m pytest tests/ -v -m "not slow"

# Run with coverage
uv run python -m pytest tests/ --cov=promptverge --cov-report=html
```

## 📊 Quality Assurance

```bash
# Code formatting and linting
uv run ruff check .
uv run ruff format .

# Security scanning
gitleaks detect --source . --verbose --no-git
```

## 🔧 Development

### Adding New Workflows

1. **Define Schemas**: Add new Pydantic models in `schemas/documents.py`
2. **Create AI Functions**: Add `@fn` decorated functions in the appropriate workflow file
3. **Build Flow**: Create a `@flow` decorated orchestration function
4. **Add CLI Command**: Register new commands in `main.py`
5. **Write Tests**: Add comprehensive tests in `tests/`

### Schema Validation

All document schemas are automatically validated using the `schemas/validator.py` utility:

```python
from promptverge.schemas.validator import validate_document
from promptverge.schemas.documents import CodeAudit

# Validate any Pydantic model instance
audit = CodeAudit(...)
is_valid = validate_document(audit)  # Returns True/False
```

## 📈 Performance & Monitoring

- **Prefect Dashboard**: Monitor workflow execution and performance
- **Rich Terminal Output**: Real-time progress indicators and formatted results
- **Comprehensive Logging**: Detailed execution traces for debugging

## 🤝 Contributing

PromptVerge follows the Cultivation project's development standards:

1. **Test-Driven Development**: Write tests before implementation
2. **Schema-First Design**: Define Pydantic models before building workflows
3. **Comprehensive Documentation**: Document all public APIs and workflows
4. **Quality Gates**: All code must pass linting, formatting, and security scans

## 📚 Documentation

- **[Architecture Overview](docs/architecture_overview.md)**: System design and component relationships
- **[Document Schemas](docs/DocumentSchemas.md)**: Complete schema reference
- **[Project Charter](docs/project_charter.md)**: Vision, goals, and strategic context
- **[Technical Debt](docs/TECHNICAL_DEBT.md)**: Known limitations and future improvements

## 🎯 Roadmap

- [ ] **Real AI Integration**: Replace mocks with actual OpenAI/Anthropic API calls
- [ ] **Output Persistence**: Save generated artifacts to structured files
- [ ] **Batch Processing**: Support for processing multiple files
- [ ] **Custom Prompts**: User-configurable prompt templates
- [ ] **Integration APIs**: REST endpoints for external system integration

---

**Built with ❤️ as part of the [Cultivation](../../) Holistic Performance Enhancement ecosystem.**