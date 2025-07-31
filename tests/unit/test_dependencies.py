"""
Unit tests for application dependencies.

This module tests the dependency injection functions and their error handling.
"""

import pytest
from unittest.mock import Mock
from fastapi import HTTPException, Request

from app.dependencies import get_book_repository
from app.repositories import InMemoryBookRepository


class TestGetBookRepository:
    """Test class for get_book_repository dependency function."""

    def test_get_book_repository_success(self) -> None:
        """Test successful retrieval of book repository from app state."""
        # Create a mock request with app state containing repository
        mock_repository = InMemoryBookRepository()
        mock_request = Mock(spec=Request)
        mock_request.app.state.book_repository = mock_repository
        
        # Call the dependency function
        result = get_book_repository(mock_request)
        
        # Verify it returns the repository from app state
        assert result is mock_repository

    def test_get_book_repository_not_initialized(self) -> None:
        """Test error handling when repository is not initialized."""
        # Create a mock request where app.state exists but book_repository doesn't
        mock_request = Mock(spec=Request)
        mock_request.app.state = Mock()
        
        # Ensure the book_repository attribute doesn't exist by using spec
        mock_request.app.state = Mock(spec=[])  # Empty spec means no attributes
        
        # Call the dependency function and expect HTTPException
        with pytest.raises(HTTPException) as exc_info:
            get_book_repository(mock_request)
        
        # Verify the exception details
        assert exc_info.value.status_code == 503
        assert "Book repository not initialized" in exc_info.value.detail 