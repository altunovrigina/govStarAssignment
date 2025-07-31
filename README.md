
# Book Catalog API

An asynchronous RESTful API for managing a book catalog, built with **FastAPI**, **Pydantic**, and **Python 3.13**. Designed with clean architecture, modern Python patterns, and full testability in mind.

---

## Features

### Core Functionality

* Create, list, retrieve, and delete books
* Filtering by author, year, and title (search)
* Pagination and sorting
* Statistics endpoint (total books and unique authors)
* Health check and root welcome endpoint

### Technical Highlights

* Full async/await support with non-blocking I/O
* Repository pattern with abstract interfaces
* Dependency injection using FastAPI’s DI system
* Comprehensive data validation using Pydantic v2
* Clean separation of concerns (routers, repositories, models, utils)
* Full type hints with Python 3.13

---

## API Endpoints

| Method | Endpoint               | Description                         |
| ------ | ---------------------- | ----------------------------------- |
| GET    | `/`                    | API information and welcome message |
| GET    | `/health`              | Health check                        |
| POST   | `/books/`              | Create a new book                   |
| GET    | `/books/`              | List books with filters/pagination  |
| GET    | `/books/{id}`          | Retrieve a book by ID               |
| DELETE | `/books/{id}`          | Delete a book by ID                 |
| GET    | `/books/stats/summary` | Collection statistics               |

### Query Parameters

* `author` – Case-insensitive filter by author
* `year` – Filter by exact year
* `search` – Case-insensitive search by title
* `sort_by` – Sort by `year` or `author`
* `sort_order` – `asc` or `desc`
* `page` – Page number (≥1)
* `limit` – Items per page (1–100)

---

## Data Validation

All incoming data is validated with Pydantic. Rules include:

* `title`: 1–500 chars, required
* `author`: 1–200 chars, required
* `year`: Between 1400 and current year
* `tags`: Optional list of up to 50 strings
* Pagination and sorting parameters are also validated

---

## Architecture

### Project Structure

```
app/
├── main.py                 # FastAPI app setup
├── dependencies.py         # Dependency injection
├── models/                 # Pydantic models
├── repositories/           # Abstract + in-memory repository
├── routers/                # API route definitions
└── utils/                  # Utilities and data loader
```

### Design Principles

* Repository Pattern with interface-based design
* Dependency Injection using `app.state` and `Depends`
* Async/await concurrency without manual locks
* No global state
* SOLID principles for maintainability and testability

---

## Technology Stack

* Python 3.13
* FastAPI 0.35.0
* Pydantic 2.11.7
* Uvicorn 0.35.0

---

## Development Setup

### Option 1: Using Script

```bash
./run.sh setup   # Create venv and install dependencies
./run.sh run     # Start the FastAPI server
```

### Option 2: Manual Setup

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access Points

* API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

## Testing

This project includes a test suite with **unit tests**, **integration tests**, and **coverage reporting**.

### Test Architecture

- **Unit Tests** (`tests/unit/`): Fast, isolated tests for individual components (models, repositories, services, utils)
- **Integration Tests** (`tests/integration/`): Full API endpoint testing with request/response cycles
- **Test Utilities** (`tests/utils/`): Reusable test data factories and helper functions
- **Fixtures** (`tests/conftest.py`): Shared test configuration and dependency injection

### Running Tests

#### Quick Start
```bash
# Run all tests with coverage
./run.sh test

# Windows
run.bat test
```

#### Specific Test Types
```bash
# Unit tests only (fast)
./run.sh test-unit

# Integration tests only 
./run.sh test-integration

# Generate detailed coverage report
./run.sh test-coverage

# Run specific test file
./run.sh test-file tests/unit/test_models.py
```


## Testing via Notebook

A Jupyter notebook is provided for interactive testing of the API.

### File

* `project_notebook.ipynb`

### Requirements

* The FastAPI server **must be running locally** at `http://localhost:8000`
* Ensure all dependencies are installed (via `run.sh setup` or `requirements.txt`)

### Usage

1. Start the application:

   ```bash
   ./run.sh run
   ```
2. Open the notebook:

   ```bash
   jupyter notebook project_notebook.ipynb
   ```

This notebook is intended to provide a quick and user-friendly way to test core functionality without needing to manually craft requests.
