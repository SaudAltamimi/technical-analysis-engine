# Technical Analysis Project Documentation

This directory contains detailed documentation for the Technical Analysis project.

## Documentation Files

### Architecture & Design
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - High-level system architecture and component relationships
- **[DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md)** - Detailed project structure and organization

### API Documentation  
- **[README_API.md](./README_API.md)** - Comprehensive FastAPI endpoint documentation and usage examples

## Main Project Documentation

The main project README is located in the root directory: `../README.md`

## Quick Navigation

### For Developers
1. Start with the main [README.md](../README.md) for setup and getting started
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system design
3. Check [DIRECTORY_STRUCTURE.md](./DIRECTORY_STRUCTURE.md) for project organization
4. Use [README_API.md](./README_API.md) for API development and testing

### For API Users
- [README_API.md](./README_API.md) contains complete API endpoint documentation
- Interactive API docs available at `http://localhost:8000/docs` when running

### Testing
- Test examples are provided through the Streamlit application
- Unit and integration tests are located in the `../tests/` directory
- Run tests using `make test` from the project root

## Project Structure Overview

```
├── src/
│   ├── technical_analysis_engine/    # Core engine package
│   ├── app/                          # FastAPI application  
│   └── streamlit_app/                # Streamlit interface
├── tests/                            # Test suite
├── docs/                             # Documentation (this folder)
└── README.md                         # Main project documentation
```

## Getting Started

1. Follow setup instructions in the main [README.md](../README.md)
2. Use `make help` to see available commands
3. Start with `make setup && make dev` for full development environment 