# Technical Analysis Project - Separated Architecture

## 🏗️ Architecture Overview

This project follows a **clean separation of concerns** design with three distinct components that can be developed, deployed, and maintained independently.

## 📦 Components

### 1. Core Technical Analysis Engine
**Location**: Root project + `src/techincal-analysis-engine/`  
**Environment**: UV  
**Dependencies**: vectorbt, pandas, numpy, plotly (compatible versions)

**Purpose**:
- Core technical analysis algorithms
- Indicator calculations (EMA, SMA, RSI, MACD)
- Strategy backtesting logic
- Data processing and analysis

**Key Files**:
- `pyproject.toml` - Core engine dependencies
- `src/techincal-analysis-engine/` - Engine implementation

### 2. FastAPI Backend
**Location**: `src/app/`  
**Environment**: UV (shares with engine)  
**Dependencies**: FastAPI, uvicorn + engine dependencies

**Purpose**:
- REST API endpoints
- HTTP interface to technical analysis engine
- JSON data serialization
- API authentication & validation

**Key Files**:
- `src/app/main.py` - FastAPI application
- `src/app/models.py` - API data models
- `src/app/services.py` - Business logic layer

### 3. Streamlit Frontend
**Location**: `src/streamlit_app/`  
**Environment**: pip (separate from engine)  
**Dependencies**: streamlit, requests, plotly (minimal)

**Purpose**:
- Web user interface
- Strategy builder forms
- Visualization dashboards
- API client (HTTP-only communication)

**Key Files**:
- `src/streamlit_app/requirements.txt` - Frontend-only dependencies
- `src/streamlit_app/streamlit_app.py` - Main UI app
- `src/streamlit_app/setup.py` - Independent setup script

## 🔄 Communication Flow

```
User Browser
    ↓
Streamlit Frontend (pip env)
    ↓ HTTP requests
FastAPI Backend (uv env)
    ↓ Python imports
Technical Analysis Engine (uv env)
    ↓ API calls
Yahoo Finance Data
```

## 📋 Benefits of Separation

### ✅ Dependency Isolation
- **No Conflicts**: vectorbt/plotly compatibility issues don't affect frontend
- **Minimal Frontend**: Streamlit app has only UI dependencies
- **Independent Updates**: Each component can upgrade dependencies separately

### ✅ Development Efficiency  
- **Parallel Development**: Frontend and backend teams can work independently
- **Faster Frontend**: No need to install heavy analysis libraries for UI work
- **Clean APIs**: Forces well-defined HTTP interfaces

### ✅ Deployment Flexibility
- **Microservices Ready**: Can deploy components on different servers
- **Scaling**: Frontend and backend can scale independently  
- **Environment Specific**: Different Python versions, OS compatibility per component

### ✅ Maintenance Benefits
- **Clear Boundaries**: Engine logic separate from UI logic
- **Easy Testing**: Mock API for frontend testing, mock data for backend
- **Bug Isolation**: Frontend bugs don't affect analysis, vice versa

## 🚀 Setup Commands

### Complete Setup
```bash
# Core engine + API (vectorbt environment)
make setup

# Streamlit frontend (separate pip environment)  
make setup-streamlit

# Both servers
make dev
```

### Individual Components
```bash
# Just the engine + API
make setup && make api

# Just the frontend (API must be running)
make setup-streamlit && make streamlit

# Engine development
make install-deps && make install-engine

# API development  
make install-api && make api

# Frontend development
cd src/streamlit_app && pip install -r requirements.txt && streamlit run streamlit_app.py
```

## 🔧 Development Workflow

### Frontend Developer
1. `make setup-streamlit` - Install only UI dependencies
2. `make api` - Start backend server (in separate terminal)
3. `make streamlit` - Start frontend development
4. Work with HTTP API calls, no engine coupling

### Backend Developer  
1. `make setup` - Install engine + API dependencies
2. `make api` - Start API server
3. Work with engine integration, no frontend concerns

### Full Stack Developer
1. `make setup && make setup-streamlit` - Setup both environments
2. `make dev` - Start both servers
3. Develop end-to-end features

## 📁 Directory Structure

```
technical-analysis-prod/
├── pyproject.toml              # Core engine dependencies (uv)
├── Makefile                    # Automation for all components
├── src/
│   ├── app/                    # FastAPI backend (uv env)
│   │   ├── main.py
│   │   ├── models.py
│   │   └── services.py
│   ├── streamlit_app/          # Frontend (pip env)
│   │   ├── requirements.txt    # Separate dependencies
│   │   ├── setup.py           # Independent setup
│   │   ├── streamlit_app.py
│   │   └── pages/
│   └── techincal-analysis-engine/  # Core engine (uv env)
└── ...
```

## 🎯 Best Practices

### Environment Management
- Use `uv` for core engine + API
- Use `pip` for Streamlit frontend
- Never mix environments
- Document dependencies clearly

### API Communication
- Frontend only communicates via HTTP
- No direct imports of engine code in frontend  
- Use proper error handling for API calls
- Design APIs with frontend needs in mind

### Development
- Start backend before frontend
- Use `make dev` for full development
- Test components independently
- Keep API documentation updated

## 🚨 Important Notes

### Dependency Conflicts
- **Before**: Single environment caused vectorbt/plotly conflicts
- **After**: Isolated environments prevent conflicts
- **Streamlit**: Uses standard plotly, no vectorbt
- **Engine**: Uses vectorbt-compatible plotly version

### Breaking Changes
- Engine changes don't break frontend (API contract maintained)
- Frontend changes don't affect engine
- Each component can be updated independently
- Clear interfaces prevent cascade failures

This architecture ensures robust, maintainable, and scalable technical analysis application development. 