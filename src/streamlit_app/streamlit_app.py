"""
Streamlit App for Custom Trading Strategy Builder & Backtester
Interacts only with FastAPI endpoints to ensure API functionality
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any
import time

# Configure page
st.set_page_config(
    page_title="Custom Strategy Builder & Tester",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'selected_strategy' not in st.session_state:
    st.session_state.selected_strategy = None
if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None
if 'api_status' not in st.session_state:
    st.session_state.api_status = None

def check_api_status():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def make_api_request(endpoint: str, method: str = "GET", data: Dict = None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.Timeout:
        st.error("API request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to API. Please ensure the FastAPI server is running.")
        return None
    except Exception as e:
        st.error(f"Request failed: {str(e)}")
        return None

# Sidebar
st.sidebar.title("📈 Strategy Builder")
st.sidebar.markdown("---")

# API Status Check
api_status = check_api_status()
st.session_state.api_status = api_status

if api_status:
    st.sidebar.success("✅ API Connected")
else:
    st.sidebar.error("❌ API Disconnected")
    st.sidebar.markdown("Please start the FastAPI server:\n```bash\ncd src/app\npython -m uvicorn main:app --reload\n```")

# Page Selection
page = st.sidebar.selectbox(
    "Choose a page:",
    ["🔧 Strategy Builder", "🧪 Strategy Tester"],
    disabled=not api_status
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Help")
st.sidebar.markdown("""
**Strategy Builder**: Create custom strategies with indicators and rules

**Strategy Tester**: Backtest your strategies against historical data
""")

# Main content based on page selection
if page == "🔧 Strategy Builder":
    # Import and run strategy builder page
    exec(open("pages/strategy_builder.py").read())
elif page == "🧪 Strategy Tester":
    # Import and run strategy tester page  
    exec(open("pages/strategy_tester.py").read())

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Custom Strategy Builder & Tester | Powered by FastAPI & Streamlit"
    "</div>",
    unsafe_allow_html=True
) 