@echo off
REM Book Catalog API - Development Script for Windows
REM Usage: run.bat [command]
REM Commands: setup, run, test, clean, help

setlocal enabledelayedexpansion

REM Configuration
set VENV_NAME=venv
set PYTHON_VERSION=python
set APP_MODULE=app.main:app
set HOST=0.0.0.0
set PORT=8000

REM Colors (limited support in Windows)
set INFO_COLOR=[94m
set SUCCESS_COLOR=[92m
set WARNING_COLOR=[93m
set ERROR_COLOR=[91m
set NC=[0m

REM Helper functions
:print_info
echo %INFO_COLOR%[INFO]%NC% %~1
exit /b

:print_success
echo %SUCCESS_COLOR%[SUCCESS]%NC% %~1
exit /b

:print_warning
echo %WARNING_COLOR%[WARNING]%NC% %~1
exit /b

:print_error
echo %ERROR_COLOR%[ERROR]%NC% %~1
exit /b

:print_header
echo.
echo ================================
echo   %~1
echo ================================
echo.
exit /b

REM Check if virtual environment exists
:check_venv
if not exist "%VENV_NAME%" (
    call :print_error "Virtual environment not found. Please run 'run.bat setup' first."
    exit /b 1
)
exit /b

REM Activate virtual environment
:activate_venv
if exist "%VENV_NAME%\Scripts\activate.bat" (
    call "%VENV_NAME%\Scripts\activate.bat"
    call :print_info "Virtual environment activated"
) else (
    call :print_error "Cannot activate virtual environment"
    exit /b 1
)
exit /b

REM Setup command
:setup
call :print_header "Setting up Book Catalog API"

REM Check Python version
call :print_info "Checking Python version..."
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python not found. Please install Python 3.13+"
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        call :print_info "Using Python %%i"
    )
)

REM Remove existing virtual environment if it exists
if exist "%VENV_NAME%" (
    call :print_warning "Removing existing virtual environment..."
    rmdir /s /q "%VENV_NAME%"
)

REM Create virtual environment
call :print_info "Creating virtual environment..."
python -m venv "%VENV_NAME%"
if errorlevel 1 (
    call :print_error "Failed to create virtual environment"
    exit /b 1
)
call :print_success "Virtual environment created"

REM Activate virtual environment
call :activate_venv

REM Upgrade pip
call :print_info "Upgrading pip..."
python -m pip install --upgrade pip

REM Install requirements
call :print_info "Installing dependencies..."
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        call :print_error "Failed to install dependencies"
        exit /b 1
    )
    call :print_success "Dependencies installed successfully"
) else (
    call :print_error "requirements.txt not found"
    exit /b 1
)

REM Verify installation
call :print_info "Verifying installation..."
python -c "import fastapi, pydantic, uvicorn; print('✓ All dependencies imported successfully')"
if errorlevel 1 (
    call :print_error "Dependency verification failed"
    exit /b 1
)

call :print_success "Setup completed successfully!"
call :print_info "You can now run the application with: run.bat run"
exit /b

REM Run command
:run
call :print_header "Starting Book Catalog API"

call :check_venv
call :activate_venv

call :print_info "Starting FastAPI server..."
call :print_info "Host: %HOST%"
call :print_info "Port: %PORT%"
call :print_info "API Documentation: http://localhost:%PORT%/docs"
call :print_info "ReDoc: http://localhost:%PORT%/redoc"
echo.
call :print_info "Press Ctrl+C to stop the server"
echo.

REM Start the application
uvicorn "%APP_MODULE%" --host "%HOST%" --port "%PORT%" --reload --log-level info --access-log
exit /b

REM Test command (comprehensive testing support)
:test
call :print_header "Running Tests"

call :check_venv
call :activate_venv

REM Install test dependencies if needed
call :print_info "Ensuring test dependencies are installed..."
pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
if errorlevel 1 (
    call :print_error "Failed to install test dependencies"
    exit /b 1
)

REM Run all tests with coverage
call :print_info "Running comprehensive test suite..."
python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml --tb=short
if errorlevel 1 (
    call :print_error "Some tests failed. Check the output above for details."
    exit /b 1
)

call :print_success "All tests passed!"
call :print_info "Coverage report generated in htmlcov/"
call :print_info "Open htmlcov/index.html in your browser to view detailed coverage"
exit /b

REM Test unit command
:test-unit
call :print_header "Running Unit Tests"

call :check_venv
call :activate_venv

call :print_info "Installing test dependencies..."
pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
if errorlevel 1 (
    call :print_error "Failed to install test dependencies"
    exit /b 1
)

call :print_info "Running unit tests..."
python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing --tb=short -m "unit"
if errorlevel 1 (
    call :print_error "Unit tests failed. Check the output above for details."
    exit /b 1
)

call :print_success "Unit tests passed!"
exit /b

REM Test integration command
:test-integration
call :print_header "Running Integration Tests"

call :check_venv
call :activate_venv

call :print_info "Installing test dependencies..."
pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
if errorlevel 1 (
    call :print_error "Failed to install test dependencies"
    exit /b 1
)

call :print_info "Running integration tests..."
python -m pytest tests/integration/ -v --cov=app --cov-report=term-missing --tb=short -m "integration"
if errorlevel 1 (
    call :print_error "Integration tests failed. Check the output above for details."
    exit /b 1
)

call :print_success "Integration tests passed!"
exit /b

REM Test coverage command
:test-coverage
call :print_header "Generating Test Coverage Report"

call :check_venv
call :activate_venv

call :print_info "Installing test dependencies..."
pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
if errorlevel 1 (
    call :print_error "Failed to install test dependencies"
    exit /b 1
)

call :print_info "Running tests with detailed coverage..."
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term --cov-report=xml --cov-fail-under=85 --tb=short
if errorlevel 1 (
    call :print_error "Coverage requirements not met or tests failed."
    exit /b 1
)

call :print_success "Coverage report generated!"
call :print_info "HTML report: htmlcov/index.html"
call :print_info "XML report: coverage.xml"

REM Try to open coverage report in browser (Windows)
if exist "htmlcov\index.html" (
    call :print_info "Opening coverage report in browser..."
    start htmlcov\index.html
)
exit /b

REM Test specific file command
:test-file
if "%~2"=="" (
    call :print_error "Usage: run.bat test-file <file_pattern>"
    call :print_info "Examples:"
    call :print_info "  run.bat test-file tests\unit\test_models.py"
    call :print_info "  run.bat test-file tests\integration\"
    call :print_info "  run.bat test-file -k test_create_book"
    exit /b 1
)

call :print_header "Running Specific Tests: %~2"

call :check_venv
call :activate_venv

call :print_info "Installing test dependencies..."
pip install -q pytest pytest-asyncio pytest-cov httpx pytest-mock
if errorlevel 1 (
    call :print_error "Failed to install test dependencies"
    exit /b 1
)

call :print_info "Running specified tests..."
python -m pytest "%~2" -v --tb=short
if errorlevel 1 (
    call :print_error "Specified tests failed. Check the output above for details."
    exit /b 1
)

call :print_success "Specified tests passed!"
exit /b

REM Clean command
:clean
call :print_header "Cleaning Environment"

if exist "%VENV_NAME%" (
    call :print_info "Removing virtual environment..."
    rmdir /s /q "%VENV_NAME%"
    call :print_success "Virtual environment removed"
) else (
    call :print_info "No virtual environment found"
)

call :print_info "Removing Python cache files..."
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc >nul 2>&1

call :print_success "Cleanup completed"
exit /b

REM Status command
:status
call :print_header "Environment Status"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python 3 not found"
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do (
        call :print_success "Python: %%i"
    )
)

REM Check virtual environment
if exist "%VENV_NAME%" (
    call :print_success "Virtual environment: Present"
    if exist "%VENV_NAME%\Scripts\activate.bat" (
        call :activate_venv
        call :print_info "Installed packages:"
        pip list | findstr /i "fastapi pydantic uvicorn" || call :print_warning "Core packages not found"
    )
) else (
    call :print_warning "Virtual environment: Not found"
)

REM Check requirements file
if exist "requirements.txt" (
    call :print_success "Requirements file: Present"
) else (
    call :print_error "Requirements file: Missing"
)

REM Check app structure
if exist "app\main.py" (
    call :print_success "Application: Present"
) else (
    call :print_error "Application: Missing"
)
exit /b

REM Help command
:help
echo.
echo Book Catalog API - Development Script for Windows
echo ================================================
echo.
echo Usage: run.bat [command]
echo.
echo Setup Commands:
echo   setup              - Create virtual environment and install dependencies
echo   clean              - Remove virtual environment and cache files
echo   status             - Show environment status
echo.
echo Development Commands:
echo   run                - Start the FastAPI development server
echo.
echo Testing Commands:
echo   test               - Run all tests with coverage report
echo   test-unit          - Run unit tests only
echo   test-integration   - Run integration tests only
echo   test-coverage      - Generate detailed coverage report and open in browser
echo   test-file ^<pattern^> - Run specific test file or pattern
echo.
echo Other Commands:
echo   help               - Show this help message
echo.
echo Examples:
echo   run.bat setup                              # First time setup
echo   run.bat run                                # Start the server
echo   run.bat test                               # Run all tests
echo   run.bat test-unit                          # Run only unit tests
echo   run.bat test-integration                   # Run only integration tests
echo   run.bat test-coverage                      # Generate coverage report
echo   run.bat test-file tests\unit\test_models.py # Run specific test file
echo   run.bat test-file -k test_create_book      # Run tests matching pattern
echo   run.bat status                             # Check environment
echo   run.bat clean                              # Clean everything
echo.
echo After setup, access the API at:
echo   - API: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo.
echo Test Reports:
echo   - Coverage HTML: htmlcov\index.html
echo   - Coverage XML: coverage.xml
echo.
exit /b

REM Main script logic
if "%1"=="" goto help
if "%1"=="setup" goto setup
if "%1"=="run" goto run
if "%1"=="test" goto test
if "%1"=="test-unit" goto test-unit
if "%1"=="test-integration" goto test-integration
if "%1"=="test-coverage" goto test-coverage
if "%1"=="test-file" goto test-file
if "%1"=="status" goto status
if "%1"=="clean" goto clean
if "%1"=="help" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help

call :print_error "Unknown command: %1"
goto help 