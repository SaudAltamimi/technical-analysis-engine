# Technical Analysis Engine Tests

This directory contains comprehensive tests for the Technical Analysis Engine project.

## Structure

```
tests/
├── unit/                    # Unit tests for engine components
│   ├── test_engine_core.py      # Core engine functionality
│   └── test_framework.py        # Framework tests (moved from engine)
├── integration/             # Integration tests
│   └── test_api_integration.py  # API + Engine integration

│   └── my_strategy.json         # Sample strategy configuration
└── conftest.py             # Pytest configuration and fixtures
```

## Running Tests

### Prerequisites

1. **Install test dependencies:**
   ```bash
   pip install -e .[dev]
   ```

2. **For integration tests, start the API server:**
   ```bash
   make api
   # or manually: cd src/app && uvicorn main:app --reload
   ```

### Test Commands

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit/

# Run only integration tests (requires API server)
pytest tests/integration/ -m integration

# Run with coverage
pytest --cov=src/technical_analysis_engine

# Run specific test file
pytest tests/unit/test_engine_core.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Test Categories

- **Unit Tests**: Test individual engine components in isolation
- **Integration Tests**: Test API + Engine integration (requires running API server)
- **Sample Configurations**: Strategy configuration examples

## Writing New Tests

### Unit Tests
Place in `tests/unit/` and follow the pattern:
```python
import pytest
from technical_analysis_engine import SomeComponent

class TestSomeComponent:
    def test_functionality(self):
        # Test code here
        pass
```

### Integration Tests
Place in `tests/integration/` and mark with `@pytest.mark.integration`:
```python
import pytest

@pytest.mark.integration
class TestAPIIntegration:
    def test_api_endpoint(self):
        # Integration test code
        pass
```

### Fixtures
Use shared fixtures from `conftest.py` or create test-specific ones.

## Usage Examples

Usage examples are available through:
- **Unit tests** - Show how to use the engine independently
- **Integration tests** - Demonstrate API + Engine integration
- **Streamlit application** - Interactive examples and testing
- **Sample configurations** - Strategy examples in JSON format

Run tests to see usage patterns:
```bash
cd tests
python run_tests.py
```

## Test Data

Tests use:
- **Live data** for integration tests (Yahoo Finance)
- **Sample strategies** from fixtures in `conftest.py`
- **Mock data** where appropriate to avoid external dependencies 