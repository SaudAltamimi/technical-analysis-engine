# Technical Analysis Project - Makefile
# Automates development workflows for FastAPI and Streamlit applications

# =============================================================================
# CONFIGURATION
# =============================================================================

# Python and environment settings
PYTHON := python3
UV := uv
VENV_NAME := .venv
SHELL := /bin/bash

# Project directories
SRC_DIR := src
API_DIR := $(SRC_DIR)/app
STREAMLIT_DIR := $(SRC_DIR)/streamlit_app
ENGINE_DIR := $(SRC_DIR)/technical_analysis_engine

# Server settings
API_HOST := localhost
API_PORT := 8000
STREAMLIT_HOST := localhost
STREAMLIT_PORT := 8501

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
NC := \033[0m # No Color

# =============================================================================
# HELP & INFO
# =============================================================================

.PHONY: help
help: ## Show this help message
	@echo "$(CYAN)Technical Analysis Project - Development Commands$(NC)"
	@echo "=================================================="
	@echo ""
	@echo "$(YELLOW)🚀 Quick Start:$(NC)"
	@echo "  make setup           - Setup core engine + API (uv environment)"
	@echo "  make setup-streamlit - Setup Streamlit app (pip environment)"
	@echo "  make dev             - Start both API and Streamlit servers"
	@echo ""
	@echo "$(YELLOW)📋 Available Commands:$(NC)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)🎯 Common Workflows:$(NC)"
	@echo "  make setup && make dev    - Full setup and development"
	@echo "  make api                  - Start API server only"
	@echo "  make streamlit            - Start Streamlit app only"
	@echo "  make test                 - Run tests"
	@echo "  make clean                - Clean temporary files"

.PHONY: info
info: ## Show project information
	@echo "$(CYAN)Project Information$(NC)"
	@echo "==================="
	@echo "$(YELLOW)Name:$(NC)           Technical Analysis API & Streamlit App"
	@echo "$(YELLOW)Structure:$(NC)      FastAPI Backend + Streamlit Frontend"
	@echo "$(YELLOW)API URL:$(NC)        http://$(API_HOST):$(API_PORT)"
	@echo "$(YELLOW)Streamlit URL:$(NC)  http://$(STREAMLIT_HOST):$(STREAMLIT_PORT)"
	@echo "$(YELLOW)Documentation:$(NC)  http://$(API_HOST):$(API_PORT)/docs"
	@echo ""
	@echo "$(YELLOW)Directories:$(NC)"
	@echo "  API:         $(API_DIR)"
	@echo "  Streamlit:   $(STREAMLIT_DIR)" 
	@echo "  Engine:      $(ENGINE_DIR)"

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================

.PHONY: setup
setup: init-env install-deps install-api install-engine ## Complete project setup
	@echo "$(GREEN)✅ Project setup complete!$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  make setup-streamlit - Setup Streamlit app (separate)"
	@echo "  make dev             - Start development servers"
	@echo "  make api             - Start API server only"

.PHONY: setup-streamlit
setup-streamlit: install-streamlit ## Setup Streamlit app separately
	@echo "$(GREEN)✅ Streamlit app setup complete!$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@echo "  make streamlit       - Start Streamlit app"
	@echo "  Note: Make sure API server is running first with 'make api'"

.PHONY: init-env
init-env: ## Initialize uv virtual environment
	@echo "$(BLUE)🔧 Initializing uv environment...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(YELLOW)Creating uv virtual environment...$(NC)"; \
		$(UV) venv; \
		echo "$(GREEN)✅ Virtual environment created$(NC)"; \
	else \
		echo "$(GREEN)✅ Virtual environment already exists$(NC)"; \
	fi

.PHONY: check-env
check-env: ## Check if uv virtual environment exists and is activated
	@echo "$(BLUE)🔍 Checking uv environment...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(RED)❌ No uv virtual environment found!$(NC)"; \
		echo "$(YELLOW)Please create and activate environment first:$(NC)"; \
		echo "  uv venv"; \
		echo "  source $(VENV_NAME)/bin/activate"; \
		exit 1; \
	else \
		echo "$(GREEN)✅ UV virtual environment exists: $(VENV_NAME)$(NC)"; \
	fi

.PHONY: install-deps
install-deps: check-env ## Install core engine dependencies
	@echo "$(BLUE)📦 Installing core technical analysis engine dependencies...$(NC)"
	$(UV) sync
	@echo "$(GREEN)✅ Core dependencies installed$(NC)"

.PHONY: install-api
install-api: check-env ## Install FastAPI dependencies
	@echo "$(BLUE)📦 Installing FastAPI dependencies...$(NC)"
	$(UV) sync --extra api
	@echo "$(GREEN)✅ API dependencies installed$(NC)"

.PHONY: install-streamlit
install-streamlit: ## Install Streamlit app dependencies (separate environment)
	@echo "$(BLUE)📦 Installing Streamlit dependencies...$(NC)"
	cd $(STREAMLIT_DIR) && pip install -r requirements.txt
	@echo "$(GREEN)✅ Streamlit dependencies installed$(NC)"

.PHONY: install-engine
install-engine: check-env ## Install technical analysis engine
	@echo "$(BLUE)⚙️ Installing technical analysis engine...$(NC)"
	$(UV) pip install -e .
	@echo "$(GREEN)✅ Engine installed$(NC)"

.PHONY: upgrade-deps
upgrade-deps: check-env ## Upgrade all dependencies
	@echo "$(BLUE)🔄 Upgrading dependencies...$(NC)"
	$(UV) sync --upgrade
	@echo "$(GREEN)✅ Dependencies upgraded$(NC)"

# =============================================================================
# DEVELOPMENT SERVERS
# =============================================================================

.PHONY: dev
dev: ## Start both API and Streamlit servers in background
	@echo "$(BLUE)🚀 Starting development environment...$(NC)"
	@echo "$(YELLOW)Starting API server...$(NC)"
	@cd $(API_DIR) && $(UV) run uvicorn main:app --reload --host $(API_HOST) --port $(API_PORT) &
	@sleep 3
	@echo "$(YELLOW)Starting Streamlit app...$(NC)"
	@cd $(STREAMLIT_DIR) && streamlit run streamlit_app.py --server.port $(STREAMLIT_PORT) --server.headless true &
	@sleep 2
	@echo "$(GREEN)✅ Development servers started!$(NC)"
	@echo ""
	@echo "$(CYAN)🌐 Access URLs:$(NC)"
	@echo "  API Server:      http://$(API_HOST):$(API_PORT)"
	@echo "  API Docs:        http://$(API_HOST):$(API_PORT)/docs"
	@echo "  Streamlit App:   http://$(STREAMLIT_HOST):$(STREAMLIT_PORT)"
	@echo ""
	@echo "$(YELLOW)Press Ctrl+C to stop all servers$(NC)"
	@trap 'make stop' INT; while true; do sleep 1; done

.PHONY: api
api: check-env ## Start FastAPI server only
	@echo "$(BLUE)🚀 Starting FastAPI server...$(NC)"
	@echo "$(CYAN)API will be available at: http://$(API_HOST):$(API_PORT)$(NC)"
	@echo "$(CYAN)Documentation at: http://$(API_HOST):$(API_PORT)/docs$(NC)"
	cd $(API_DIR) && $(UV) run uvicorn main:app --reload --host $(API_HOST) --port $(API_PORT)

.PHONY: streamlit
streamlit: ## Start Streamlit app only (uses separate pip environment)
	@echo "$(BLUE)🚀 Starting Streamlit app...$(NC)"
	@echo "$(CYAN)App will be available at: http://$(STREAMLIT_HOST):$(STREAMLIT_PORT)$(NC)"
	@echo "$(YELLOW)Note: Make sure API server is running on port $(API_PORT)$(NC)"
	@echo "$(YELLOW)Note: Uses pip environment separate from uv$(NC)"
	cd $(STREAMLIT_DIR) && streamlit run streamlit_app.py --server.port $(STREAMLIT_PORT)

.PHONY: api-prod
api-prod: check-env ## Start FastAPI in production mode
	@echo "$(BLUE)🚀 Starting FastAPI in production mode...$(NC)"
	cd $(API_DIR) && $(UV) run uvicorn main:app --host 0.0.0.0 --port $(API_PORT) --workers 4

.PHONY: stop
stop: ## Stop all running servers
	@echo "$(YELLOW)🛑 Stopping all servers...$(NC)"
	@pkill -f "uvicorn main:app" || echo "No API server running"
	@pkill -f "streamlit run" || echo "No Streamlit server running"
	@echo "$(GREEN)✅ All servers stopped$(NC)"

# =============================================================================
# TESTING & VALIDATION
# =============================================================================

.PHONY: test
test: check-env ## Run all tests
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@echo "$(YELLOW)Testing API endpoints...$(NC)"
	@if curl -s http://$(API_HOST):$(API_PORT)/health > /dev/null; then \
		echo "$(GREEN)✅ API server is responding$(NC)"; \
	else \
		echo "$(RED)❌ API server not responding$(NC)"; \
	fi
	@echo "$(YELLOW)Testing engine imports...$(NC)"
	@cd $(ENGINE_DIR) && $(UV) run python -c "import config, ticker_config, ta_types; print('✅ Engine imports successful')" || echo "$(RED)❌ Engine import failed$(NC)"

.PHONY: test-api
test-api: ## Test API endpoints
	@echo "$(BLUE)🧪 Testing API endpoints...$(NC)"
	@curl -s http://$(API_HOST):$(API_PORT)/ | head -c 100
	@echo ""
	@curl -s http://$(API_HOST):$(API_PORT)/health | head -c 100
	@echo ""
	@echo "$(GREEN)✅ API tests completed$(NC)"

.PHONY: validate
validate: check-env ## Validate project structure and configuration
	@echo "$(BLUE)🔍 Validating project structure...$(NC)"
	@echo "$(YELLOW)Checking directories...$(NC)"
	@test -d $(API_DIR) && echo "✅ API directory exists" || echo "❌ API directory missing"
	@test -d $(STREAMLIT_DIR) && echo "✅ Streamlit directory exists" || echo "❌ Streamlit directory missing"
	@test -d $(ENGINE_DIR) && echo "✅ Engine directory exists" || echo "❌ Engine directory missing"
	@echo "$(YELLOW)Checking key files...$(NC)"
	@test -f $(API_DIR)/main.py && echo "✅ API main.py exists" || echo "❌ API main.py missing"
	@test -f $(STREAMLIT_DIR)/streamlit_app.py && echo "✅ Streamlit app exists" || echo "❌ Streamlit app missing"
	@test -f $(ENGINE_DIR)/tickers.yaml && echo "✅ Tickers config exists" || echo "❌ Tickers config missing"
	@echo "$(GREEN)✅ Validation completed$(NC)"

# =============================================================================
# DEVELOPMENT UTILITIES
# =============================================================================

.PHONY: logs
logs: ## Show recent logs (if running with systemd)
	@echo "$(BLUE)📋 Recent application logs...$(NC)"
	@echo "$(YELLOW)API Server logs:$(NC)"
	@tail -n 20 /tmp/api.log 2>/dev/null || echo "No API logs found"
	@echo "$(YELLOW)Streamlit logs:$(NC)"
	@tail -n 20 /tmp/streamlit.log 2>/dev/null || echo "No Streamlit logs found"

.PHONY: status
status: ## Check status of services
	@echo "$(BLUE)📊 Service Status$(NC)"
	@echo "================"
	@echo "$(YELLOW)API Server:$(NC)"
	@if curl -s http://$(API_HOST):$(API_PORT)/health > /dev/null 2>&1; then \
		echo "  $(GREEN)✅ Running$(NC) - http://$(API_HOST):$(API_PORT)"; \
	else \
		echo "  $(RED)❌ Not running$(NC)"; \
	fi
	@echo "$(YELLOW)Streamlit App:$(NC)"
	@if curl -s http://$(STREAMLIT_HOST):$(STREAMLIT_PORT) > /dev/null 2>&1; then \
		echo "  $(GREEN)✅ Running$(NC) - http://$(STREAMLIT_HOST):$(STREAMLIT_PORT)"; \
	else \
		echo "  $(RED)❌ Not running$(NC)"; \
	fi

.PHONY: urls
urls: ## Show application URLs
	@echo "$(CYAN)🌐 Application URLs$(NC)"
	@echo "==================="
	@echo "$(YELLOW)FastAPI Application:$(NC)"
	@echo "  Main API:        http://$(API_HOST):$(API_PORT)"
	@echo "  Interactive Docs: http://$(API_HOST):$(API_PORT)/docs"
	@echo "  ReDoc:           http://$(API_HOST):$(API_PORT)/redoc"
	@echo "  Health Check:    http://$(API_HOST):$(API_PORT)/health"
	@echo ""
	@echo "$(YELLOW)Streamlit Application:$(NC)"
	@echo "  Web Interface:   http://$(STREAMLIT_HOST):$(STREAMLIT_PORT)"

.PHONY: docs
docs: ## Show documentation locations
	@echo "$(CYAN)📚 Documentation$(NC)"
	@echo "================="
	@echo "$(YELLOW)Main Documentation:$(NC)"
	@echo "  Project README:   ./README.md"
	@echo "  API Reference:    ./docs/README_API.md"
	@echo "  Architecture:     ./docs/ARCHITECTURE.md"
	@echo "  Directory Guide:  ./docs/DIRECTORY_STRUCTURE.md"
	@echo ""
	@echo "$(YELLOW)Interactive Docs:$(NC)"
	@echo "  API Docs:         http://$(API_HOST):$(API_PORT)/docs (when API running)"
	@echo "  Examples:         Use Streamlit app for interactive examples"

# =============================================================================
# MAINTENANCE & CLEANUP
# =============================================================================

.PHONY: clean
clean: ## Clean temporary files and caches
	@echo "$(BLUE)🧹 Cleaning temporary files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.log" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

.PHONY: clean-all
clean-all: clean stop ## Deep clean including stopping services
	@echo "$(BLUE)🧹 Deep cleaning...$(NC)"
	rm -rf $(SRC_DIR)/technical_analysis.egg-info/ 2>/dev/null || true
	rm -rf .pytest_cache/ 2>/dev/null || true
	rm -rf build/ dist/ 2>/dev/null || true
	@echo "$(GREEN)✅ Deep cleanup completed$(NC)"

.PHONY: reset
reset: clean-all ## Reset project to clean state
	@echo "$(YELLOW)⚠️  This will reset the project to a clean state$(NC)"
	@echo "$(YELLOW)Continue? (y/N)$(NC)"
	@read -r REPLY; \
	if [ "$$REPLY" = "y" ] || [ "$$REPLY" = "Y" ]; then \
		echo "$(BLUE)🔄 Resetting project...$(NC)"; \
		make clean-all; \
		echo "$(GREEN)✅ Project reset completed$(NC)"; \
		echo "$(YELLOW)Run 'make setup' to reinstall dependencies$(NC)"; \
	else \
		echo "$(YELLOW)Reset cancelled$(NC)"; \
	fi

# =============================================================================
# DOCKER SUPPORT (Optional)
# =============================================================================

.PHONY: docker-build
docker-build: ## Build Docker image (if Dockerfile exists)
	@if [ -f Dockerfile ]; then \
		echo "$(BLUE)🐳 Building Docker image...$(NC)"; \
		docker build -t technical-analysis .; \
		echo "$(GREEN)✅ Docker image built$(NC)"; \
	else \
		echo "$(YELLOW)No Dockerfile found$(NC)"; \
	fi

.PHONY: docker-run
docker-run: ## Run Docker container
	@echo "$(BLUE)🐳 Running Docker container...$(NC)"
	docker run -p $(API_PORT):$(API_PORT) -p $(STREAMLIT_PORT):$(STREAMLIT_PORT) technical-analysis

# =============================================================================
# CONFIGURATION
# =============================================================================

# Default target
.DEFAULT_GOAL := help

# Prevent make from treating file names as targets
.PHONY: all clean clean-all setup install-deps install-engine check-env \
        dev api streamlit api-prod stop test test-api validate \
        logs status urls docs help info upgrade-deps reset \
        docker-build docker-run 