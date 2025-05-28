# Technical Analysis Examples

This directory contains comprehensive examples and documentation for the Technical Analysis API project, organized into specialized subdirectories.

## 📂 Directory Structure

### 🔗 `/api_integration/`
Complete API integration examples showing how to interact with the FastAPI server.

**Files:**
- `api_integration_example.py` - Complete workflow example
- `enhanced_api_visualization.py` - Advanced visualization with stock prices
- `simple_api_visualization.py` - Simple API visualization
- `create_api_visualization.py` - Visualization creation utilities

**Purpose:** Perfect for understanding API endpoints and integration patterns.

### 📱 `/ios_development/`
iOS-specific development resources and code templates.

**Files:**
- `ios_integration.swift` - Complete Swift integration template

**Purpose:** Ready-to-use Swift code for iOS app development.

### 🔧 `/engine_examples/`
Direct technical analysis engine usage examples.

**Files:**
- `real_data_example.py` - Real stock data analysis using Yahoo Finance

**Purpose:** Shows how to use the engine directly without API layer.

### 📊 `/visualizations/`
Generated interactive charts and visualization outputs.

**Files:**
- `GOOGL_complete_analysis.html` - Complete stock analysis with prices
- `GOOGL_api_chart.html` - API-based analysis visualization
- `google_*.html` - Various Google stock analysis charts

**Purpose:** Example outputs and visualization results.

### 📖 `/documentation/`
Comprehensive documentation and guides.

**Files:**
- `ios_api_documentation.md` - Complete API reference for iOS
- `API_VISUALIZATION_SUMMARY.md` - Visualization results summary
- `examples_README.md` - Original examples documentation

**Purpose:** Reference materials and implementation guides.

### 📈 `/analysis_results/`
Analysis outputs, summaries, and result files.

**Files:**
- `GOOGL_api_analysis_summary.txt` - Text analysis summary

**Purpose:** Example analysis results and outputs.

## 🚀 Quick Start Guide

### For API Integration:
```bash
cd examples/api_integration
python api_integration_example.py
```

### For Visualization:
```bash
cd examples/api_integration
python enhanced_api_visualization.py
```

### For iOS Development:
1. Review `ios_development/ios_integration.swift`
2. Read `documentation/ios_api_documentation.md`
3. Test API endpoints using `api_integration/` examples

## 🎯 Use Cases

### **iOS Developer Getting Started:**
1. Start with `documentation/ios_api_documentation.md`
2. Run `api_integration/api_integration_example.py` to see API calls
3. Use `ios_development/ios_integration.swift` as template
4. Review `visualizations/` for expected output formats

### **API Testing:**
1. Use `api_integration/enhanced_api_visualization.py`
2. Review results in `visualizations/`
3. Check `analysis_results/` for output summaries

### **Engine Development:**
1. Study `engine_examples/real_data_example.py`
2. Understand direct engine usage patterns
3. Compare with API-based approaches

## 📊 Example Outputs

The project demonstrates:
- ✅ Real-time stock price analysis
- ✅ EMA crossover strategies
- ✅ RSI momentum analysis
- ✅ Interactive visualizations
- ✅ Trading signal generation
- ✅ Complete backtesting results

## 🔧 Requirements

All examples require the main project dependencies. Run from project root:
```bash
# Install dependencies
uv sync

# Start API server (for API examples)
python start_api.py

# Run specific examples
python examples/api_integration/enhanced_api_visualization.py
```

## 📱 iOS Integration

The examples provide everything needed for iOS integration:
- Complete API documentation
- Swift code templates
- Example HTTP requests
- JSON response formats
- Chart data structures

Perfect for building professional trading apps with real-time technical analysis capabilities. 