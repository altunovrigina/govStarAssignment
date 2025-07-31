#!/bin/bash

# Book Catalog API - Development Script
# Usage: ./run.sh [command]
# Commands: setup, run, test, clean, help

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VENV_NAME="venv"
PYTHON_VERSION="python3"
APP_MODULE="app.main:app"
HOST="0.0.0.0"
PORT="8000"

# Helper functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}================================${NC}\n"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_NAME" ]; then
        print_error "Virtual environment not found. Please run './run.sh setup' first."
        exit 1
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -f "$VENV_NAME/bin/activate" ]; then
        source "$VENV_NAME/bin/activate"
        print_info "Virtual environment activated"
    else
        print_error "Cannot activate virtual environment"
        exit 1
    fi
}

# Setup command
setup() {
    print_header "Setting up Book Catalog API"
    
    # Check Python version
    print_info "Checking Python version..."
    if command -v python3.13 &> /dev/null; then
        PYTHON_VERSION="python3.13"
        print_success "Using Python 3.13"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION="python3"
        PYTHON_VER=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_info "Using Python $PYTHON_VER"
    else
        print_error "Python 3 not found. Please install Python 3.13+"
        exit 1
    fi
    
    # Remove existing virtual environment if it exists
    if [ -d "$VENV_NAME" ]; then
        print_warning "Removing existing virtual environment..."
        rm -rf "$VENV_NAME"
    fi
    
    # Create virtual environment
    print_info "Creating virtual environment..."
    $PYTHON_VERSION -m venv "$VENV_NAME"
    print_success "Virtual environment created"
    
    # Activate virtual environment
    activate_venv
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    print_info "Installing dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Verify installation
    print_info "Verifying installation..."
    python -c "import fastapi, pydantic, uvicorn; print('✓ All dependencies imported successfully')"
    
    print_success "Setup completed successfully!"
    print_info "You can now run the application with: ./run.sh run"
}

# Run command
run() {
    print_header "Starting Book Catalog API"
    
    check_venv
    activate_venv
    
    print_info "Starting FastAPI server..."
    print_info "Host: $HOST"
    print_info "Port: $PORT"
    print_info "API Documentation: http://localhost:$PORT/docs"
    print_info "ReDoc: http://localhost:$PORT/redoc"
    print_info ""
    print_info "Press Ctrl+C to stop the server"
    print_info ""
    
    # Start the application
    uvicorn "$APP_MODULE" \
        --host "$HOST" \
        --port "$PORT" \
        --reload \
        --log-level info \
        --access-log
}

# Test command (comprehensive testing support)
test() {
    print_header "Running Tests"
    
    check_venv
    activate_venv
    
    # Install test dependencies if needed
    print_info "Ensuring test dependencies are installed..."
    pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
    
    # Run all tests with coverage
    print_info "Running comprehensive test suite..."
    python -m pytest tests/ -v \
        --cov=app \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-report=xml \
        --tb=short
    
    if [ $? -eq 0 ]; then
        print_success "All tests passed!"
        print_info "Coverage report generated in htmlcov/"
        print_info "Open htmlcov/index.html in your browser to view detailed coverage"
    else
        print_error "Some tests failed. Check the output above for details."
        exit 1
    fi
}

# Test unit command
test-unit() {
    print_header "Running Unit Tests"
    
    check_venv
    activate_venv
    
    print_info "Installing test dependencies..."
    pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
    
    print_info "Running unit tests..."
    python -m pytest tests/unit/ -v \
        --cov=app \
        --cov-report=term-missing \
        --tb=short \
        -m "unit"
    
    if [ $? -eq 0 ]; then
        print_success "Unit tests passed!"
    else
        print_error "Unit tests failed. Check the output above for details."
        exit 1
    fi
}

# Test integration command
test-integration() {
    print_header "Running Integration Tests"
    
    check_venv
    activate_venv
    
    print_info "Installing test dependencies..."
    pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
    
    print_info "Running integration tests..."
    python -m pytest tests/integration/ -v \
        --cov=app \
        --cov-report=term-missing \
        --tb=short \
        -m "integration"
    
    if [ $? -eq 0 ]; then
        print_success "Integration tests passed!"
    else
        print_error "Integration tests failed. Check the output above for details."
        exit 1
    fi
}

# Test with watch mode
test-watch() {
    print_header "Running Tests in Watch Mode"
    
    check_venv
    activate_venv
    
    print_info "Installing test dependencies..."
    pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock pytest-watch
    
    print_info "Starting test watch mode..."
    print_info "Tests will re-run automatically when files change"
    print_info "Press Ctrl+C to stop"
    
    ptw tests/ app/ --runner "python -m pytest tests/ -v --tb=short"
}

# Test coverage command
test-coverage() {
    print_header "Generating Test Coverage Report"
    
    check_venv
    activate_venv
    
    print_info "Installing test dependencies..."
    pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
    
    print_info "Running tests with detailed coverage..."
    python -m pytest tests/ \
        --cov=app \
        --cov-report=html \
        --cov-report=term \
        --cov-report=xml \
        --cov-fail-under=85 \
        --tb=short
    
    if [ $? -eq 0 ]; then
        print_success "Coverage report generated!"
        print_info "HTML report: htmlcov/index.html"
        print_info "XML report: coverage.xml"
        
        # Try to open coverage report in browser (macOS/Linux)
        if command -v open >/dev/null 2>&1; then
            print_info "Opening coverage report in browser..."
            open htmlcov/index.html
        elif command -v xdg-open >/dev/null 2>&1; then
            print_info "Opening coverage report in browser..."
            xdg-open htmlcov/index.html
        fi
    else
        print_error "Coverage requirements not met or tests failed."
        exit 1
    fi
}

# Test specific file or pattern
test-file() {
    if [ -z "$2" ]; then
        print_error "Usage: ./run.sh test-file <file_pattern>"
        print_info "Examples:"
        print_info "  ./run.sh test-file tests/unit/test_models.py"
        print_info "  ./run.sh test-file tests/integration/"
        print_info "  ./run.sh test-file -k 'test_create_book'"
        exit 1
    fi
    
    print_header "Running Specific Tests: $2"
    
    check_venv
    activate_venv
    
    print_info "Installing test dependencies..."
    pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
    
    print_info "Running specified tests..."
    python -m pytest "$2" -v --tb=short
    
    if [ $? -eq 0 ]; then
        print_success "Specified tests passed!"
    else
        print_error "Specified tests failed. Check the output above for details."
        exit 1
    fi
}

# Clean command
clean() {
    print_header "Cleaning Environment"
    
    if [ -d "$VENV_NAME" ]; then
        print_info "Removing virtual environment..."
        rm -rf "$VENV_NAME"
        print_success "Virtual environment removed"
    else
        print_info "No virtual environment found"
    fi
    
    # Remove Python cache files
    print_info "Removing Python cache files..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    print_success "Cache files removed"
    
    print_success "Cleanup completed"
}

# Status command
status() {
    print_header "Environment Status"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VER=$(python3 --version 2>&1)
        print_success "Python: $PYTHON_VER"
    else
        print_error "Python 3 not found"
    fi
    
    # Check virtual environment
    if [ -d "$VENV_NAME" ]; then
        print_success "Virtual environment: Present"
        if [ -f "$VENV_NAME/bin/activate" ]; then
            activate_venv
            print_info "Installed packages:"
            pip list | grep -E "(fastapi|pydantic|uvicorn)" || print_warning "Core packages not found"
        fi
    else
        print_warning "Virtual environment: Not found"
    fi
    
    # Check requirements file
    if [ -f "requirements.txt" ]; then
        print_success "Requirements file: Present"
    else
        print_error "Requirements file: Missing"
    fi
    
    # Check app structure
    if [ -f "app/main.py" ]; then
        print_success "Application: Present"
    else
        print_error "Application: Missing"
    fi
}

# Help command
help() {
    echo -e "\n${BLUE}Book Catalog API - Development Script${NC}"
    echo -e "${BLUE}=====================================${NC}\n"
    
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Setup Commands:"
    echo "  setup              - Create virtual environment and install dependencies"
    echo "  clean              - Remove virtual environment and cache files"
    echo "  status             - Show environment status"
    echo ""
    echo "Development Commands:"
    echo "  run                - Start the FastAPI development server"
    echo ""
    echo "Testing Commands:"
    echo "  test               - Run all tests with coverage report"
    echo "  test-unit          - Run unit tests only"
    echo "  test-integration   - Run integration tests only"
    echo "  test-coverage      - Generate detailed coverage report and open in browser"
    echo "  test-watch         - Run tests in watch mode (re-run on file changes)"
    echo "  test-file <pattern> - Run specific test file or pattern"
    echo ""
    echo "Other Commands:"
    echo "  help               - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run.sh setup                              # First time setup"
    echo "  ./run.sh run                                # Start the server"
    echo "  ./run.sh test                               # Run all tests"
    echo "  ./run.sh test-unit                          # Run only unit tests"
    echo "  ./run.sh test-integration                   # Run only integration tests"
    echo "  ./run.sh test-coverage                      # Generate coverage report"
    echo "  ./run.sh test-watch                         # Watch mode for development"
    echo "  ./run.sh test-file tests/unit/test_models.py # Run specific test file"
    echo "  ./run.sh test-file -k 'test_create_book'    # Run tests matching pattern"
    echo "  ./run.sh status                             # Check environment"
    echo "  ./run.sh clean                              # Clean everything"
    echo ""
    echo "After setup, access the API at:"
    echo "  - API: http://localhost:8000"
    echo "  - Docs: http://localhost:8000/docs"
    echo "  - ReDoc: http://localhost:8000/redoc"
    echo ""
    echo "Test Reports:"
    echo "  - Coverage HTML: htmlcov/index.html"
    echo "  - Coverage XML: coverage.xml"
    echo ""
}

# Main script logic
case "${1:-help}" in
    setup)
        setup
        ;;
    run)
        run
        ;;
    test)
        test
        ;;
    test-unit)
        test-unit
        ;;
    test-integration)
        test-integration
        ;;
    test-coverage)
        test-coverage
        ;;
    test-watch)
        test-watch
        ;;
    test-file)
        test-file "$@"
        ;;
    status)
        status
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        help
        ;;
    *)
        print_error "Unknown command: $1"
        help
        exit 1
        ;;
esac 