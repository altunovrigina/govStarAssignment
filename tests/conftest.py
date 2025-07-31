"""
Pytest configuration and shared fixtures for Book Catalog API tests.
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Any, List
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.dependencies import get_book_repository
from app.repositories import InMemoryBookRepository
from app.models import BookResponse
from tests.utils.test_data import TestDataFactory


@pytest.fixture(scope="session")
def test_data_factory() -> TestDataFactory:
    """
    Session-scoped test data factory for consistent test data generation.
    
    Returns:
        TestDataFactory: Factory for generating test data
    """
    return TestDataFactory()


@pytest_asyncio.fixture
async def clean_repository() -> InMemoryBookRepository:
    """
    Provides a clean, empty repository for each test.
    
    This ensures test isolation and prevents test interference.
    
    Returns:
        InMemoryBookRepository: Fresh repository instance
    """
    return InMemoryBookRepository()


@pytest_asyncio.fixture
async def populated_repository(
    clean_repository: InMemoryBookRepository,
    test_data_factory: TestDataFactory
) -> InMemoryBookRepository:
    """
    Provides a repository pre-populated with test data.
    
    Args:
        clean_repository: Fresh repository instance
        test_data_factory: Factory for generating test data
    
    Returns:
        InMemoryBookRepository: Repository with sample books
    """
    sample_books = test_data_factory.create_sample_books()
    await clean_repository.load_initial_books(sample_books)
    return clean_repository


@pytest_asyncio.fixture
async def test_client_with_clean_repo(clean_repository: InMemoryBookRepository) -> AsyncGenerator[TestClient, None]:
    """
    Provides a test client with a clean repository for integration tests.
    
    Uses dependency override to inject the test repository.
    
    Args:
        clean_repository: Clean repository instance
        
    Yields:
        TestClient: FastAPI test client with overridden dependencies
    """
    # Override the repository dependency
    app.dependency_overrides[get_book_repository] = lambda: clean_repository
    
    with TestClient(app) as client:
        yield client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_client_with_data(populated_repository: InMemoryBookRepository) -> AsyncGenerator[TestClient, None]:
    """
    Provides a test client with pre-populated data for integration tests.
    
    Args:
        populated_repository: Repository with sample data
        
    Yields:
        TestClient: FastAPI test client with sample data
    """
    # Override the repository dependency
    app.dependency_overrides[get_book_repository] = lambda: populated_repository
    
    with TestClient(app) as client:
        yield client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client_with_clean_repo(clean_repository: InMemoryBookRepository) -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an async HTTP client for advanced integration testing.
    
    Args:
        clean_repository: Clean repository instance
        
    Yields:
        AsyncClient: Async HTTP client for testing
    """
    # Override the repository dependency
    app.dependency_overrides[get_book_repository] = lambda: clean_repository
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_book_data() -> Dict[str, Any]:
    """
    Provides sample book data for testing.
    
    Returns:
        Dict[str, Any]: Sample book creation data
    """
    return {
        "title": "The Art of Clean Code",
        "author": "Robert C. Martin",
        "year": 2008,
        "tags": ["programming", "software engineering"]
    }


@pytest.fixture
def invalid_book_data_samples() -> Dict[str, List[Any]]:
    """
    Provides various invalid book data samples for validation testing.
    
    Returns:
        Dict[str, List[Any]]: Dictionary mapping field names to lists of invalid values
    """
    return {
        "title": [
            "",  # Empty string
            "x" * 501,  # Too long
            None,  # None value
        ],
        "author": [
            "",  # Empty string
            "x" * 201,  # Too long
            None,  # None value
        ],
        "year": [
            1399,  # Too early
            2025,  # Too late (assuming current year is 2024)
            "not_a_number",  # Invalid type
            None,  # None value
        ]
    }


# Configure pytest-asyncio
pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_environment():
    """
    Session-wide setup for async testing environment.
    
    This ensures proper async context for all tests.
    """
    pass


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to integration tests
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        # Add performance marker to performance tests
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow) 