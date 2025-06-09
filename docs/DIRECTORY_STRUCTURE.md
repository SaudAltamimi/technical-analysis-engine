# Project Directory Structure

This document outlines the organization of the Custom Strategy Technical Analysis project.

## 📁 **Root Structure**

```
technical-analysis-prod/
├── src/                              # Source code directory
│   ├── app/                          # FastAPI application
│   ├── streamlit_app/                # Streamlit web interface
│   ├── techincal-analysis-engine/    # Core technical analysis engine
│   └── technical_analysis.egg-info/  # Package metadata
├── .venv/                            # UV virtual environment (auto-created)
├── .gitignore                        # Git ignore patterns
├── Makefile                          # Development automation with UV
├── pyproject.toml                    # UV/Python project configuration
├── DIRECTORY_STRUCTURE.md            # This file
└── README.md                         # Main project documentation
```

## 🔧 **FastAPI Application (`src/app/`)**

**Purpose**: RESTful API for custom strategy creation and backtesting

```
src/app/
├── __init__.py              # Package initialization
├── main.py                  # FastAPI application with all endpoints
├── models.py                # Pydantic models for API requests/responses
├── services.py              # Business logic and service layer
└── data_service.py          # Yahoo Finance data integration
```

**Key Features**:
- Custom strategy creation API (`/strategies/custom`)
- Backtesting endpoints (`/backtest/custom/*`)
- Ticker management and validation
- YAML-based ticker configuration
- Comprehensive API documentation at `/docs`

## 🎨 **Streamlit Web Interface (`src/streamlit_app/`)**

**Purpose**: User-friendly web interface for strategy development

```
src/streamlit_app/
├── __init__.py              # Package initialization
├── streamlit_app.py         # Main Streamlit application
├── requirements.txt         # Streamlit-specific dependencies
├── run_streamlit.py         # Convenience script to run the app
├── README.md                # Streamlit app documentation
└── pages/
    ├── strategy_builder.py  # Strategy creation page
    └── strategy_tester.py   # Strategy backtesting page
```

**Key Features**:
- **Strategy Builder**: Interactive strategy configuration
- **Strategy Tester**: Comprehensive backtesting interface
- **API-only architecture**: No direct engine access
- **Real-time validation**: Immediate feedback on configurations

## ⚙️ **Technical Analysis Engine (`src/techincal-analysis-engine/`)**

**Purpose**: Core technical analysis and strategy processing engine

```
src/techincal-analysis-engine/
├── __init__.py              # Package initialization with imports
├── config.py                # Configuration models and validation
├── ticker_config.py         # Ticker configuration management
├── tickers.yaml             # Curated ticker lists and metadata
├── ta_types.py              # Type definitions and enums
├── indicators.py            # Technical indicator implementations
├── strategy.py              # Strategy definition and processing
├── signals.py               # Signal generation logic
├── engine.py                # Main analysis engine
├── builders.py              # Strategy and indicator builders
├── utils.py                 # Utility functions
├── test_framework.py        # Testing and validation framework
└── README.md                # Engine documentation
```

**Key Features**:
- Technical indicator calculations (EMA, SMA, RSI, MACD)
- Strategy definition and validation
- Signal generation and backtesting
- YAML-based configuration management

## 🔄 **Data Flow Architecture**

### **Clean Separation of Concerns**:

```
Streamlit UI ──API calls──> FastAPI App ──imports──> Technical Engine
     ↑                           ↑                         ↑
User Interface           RESTful API Layer           Core Logic
```

**Benefits**:
- **API-first**: Streamlit validates all API endpoints work correctly
- **Modular**: Each component can be developed/deployed independently  
- **Scalable**: API can serve multiple frontends (web, mobile, etc.)
- **Testable**: Clear boundaries make testing straightforward

## 🚀 **Getting Started**

### **Quick Start with Makefile + UV (Recommended)**:
```bash
# Complete setup and start development environment
make setup && make dev

# Or step by step:
make setup     # Create uv environment and install dependencies
make api       # Start FastAPI server only
make streamlit # Start Streamlit app only (in separate terminal)
make status    # Check service status
make help      # Show all available commands

# Note: All commands use 'uv run' automatically - no need to activate environment
```

### **Manual Setup (Alternative)**:
```bash
# 1. Start FastAPI Server
cd src/app
python -m uvicorn main:app --reload
# API available at: http://localhost:8000
# Documentation: http://localhost:8000/docs

# 2. Launch Streamlit Interface (in separate terminal)
cd src/streamlit_app
pip install -r requirements.txt
python run_streamlit.py
# Web interface: http://localhost:8501
```

### **3. Development Workflow**:
1. **Engine Development**: Modify core logic in `src/techincal-analysis-engine/`
2. **API Development**: Update endpoints in `src/app/main.py`
3. **Frontend Development**: Enhance UI in `src/streamlit_app/`
4. **Configuration**: Update tickers in `src/techincal-analysis-engine/tickers.yaml`

## 📋 **Development Guidelines**

### **For API Development**:
- All endpoints should follow REST conventions
- Use Pydantic models for request/response validation
- Maintain comprehensive error handling
- Update API documentation in docstrings

### **For Streamlit Development**:
- Use only API endpoints (no direct engine imports)
- Implement proper error handling for API failures
- Follow Streamlit best practices for UI/UX
- Test with API server running

### **For Engine Development**:
- Maintain backward compatibility for API layer
- Add comprehensive tests for new features
- Document configuration changes in YAML files
- Follow type hints and validation patterns

## 🎯 **Key Benefits of This Structure**

1. **Clear Separation**: Each component has a single responsibility
2. **API Validation**: Streamlit usage ensures APIs work correctly
3. **Scalability**: Components can be scaled independently
4. **Developer Friendly**: Multiple developers can work on different parts
5. **Production Ready**: Clean architecture for deployment
6. **Maintainability**: Easy to understand and modify

---

**Need help?** Check individual README files in each directory for detailed documentation. 