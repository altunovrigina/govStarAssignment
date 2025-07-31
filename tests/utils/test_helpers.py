"""
Test helper utilities for common testing patterns and assertions.

This module provides reusable helper functions that encapsulate common
testing patterns, following DRY principles.
"""

from typing import Dict, Any, List, Optional, Union
from fastapi.testclient import TestClient
from httpx import Response
import pytest
from app.models import BookResponse, PaginatedResponse


class APITestHelpers:
    """Helper class for API testing with common patterns and assertions."""
    
    @staticmethod
    def assert_successful_response(response: Response, expected_status: int = 200) -> Dict[str, Any]:
        """
        Assert that a response is successful and return the JSON data.
        
        Args:
            response: HTTP response object
            expected_status: Expected HTTP status code
            
        Returns:
            Dict[str, Any]: Response JSON data
            
        Raises:
            AssertionError: If response is not successful
        """
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, got {response.status_code}. "
            f"Response: {response.text}"
        )
        return response.json()
    
    @staticmethod
    def assert_error_response(
        response: Response, 
        expected_status: int, 
        expected_error_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Assert that a response contains an error with expected status and keywords.
        
        Args:
            response: HTTP response object
            expected_status: Expected HTTP status code
            expected_error_keywords: Keywords that should appear in error message
            
        Returns:
            Dict[str, Any]: Response JSON data
            
        Raises:
            AssertionError: If error response doesn't match expectations
        """
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        data = response.json()
        
        # Check for error message presence
        error_message = data.get("detail", "").lower()
        assert error_message, "Error response should contain a detail message"
        
        # Check for specific keywords if provided
        if expected_error_keywords:
            for keyword in expected_error_keywords:
                assert keyword.lower() in error_message, (
                    f"Expected keyword '{keyword}' not found in error message: {error_message}"
                )
        
        return data
    
    @staticmethod
    def assert_book_response_structure(book_data: Dict[str, Any]) -> None:
        """
        Assert that book data has the correct structure and types.
        
        Args:
            book_data: Book data dictionary to validate
            
        Raises:
            AssertionError: If book structure is invalid
        """
        required_fields = ["id", "title", "author", "year", "tags"]
        
        for field in required_fields:
            assert field in book_data, f"Missing required field: {field}"
        
        # Type assertions
        assert isinstance(book_data["id"], int), "ID should be an integer"
        assert isinstance(book_data["title"], str), "Title should be a string"
        assert isinstance(book_data["author"], str), "Author should be a string"
        assert isinstance(book_data["year"], int), "Year should be an integer"
        assert isinstance(book_data["tags"], list), "Tags should be a list"
        
        # Value assertions
        assert book_data["id"] > 0, "ID should be positive"
        assert len(book_data["title"].strip()) > 0, "Title should not be empty"
        assert len(book_data["author"].strip()) > 0, "Author should not be empty"
        assert 1400 <= book_data["year"] <= 2030, "Year should be in valid range"
        
        # Tags should be strings
        for tag in book_data["tags"]:
            assert isinstance(tag, str), "All tags should be strings"
    
    @staticmethod
    def assert_paginated_response_structure(
        response_data: Dict[str, Any],
        expected_page: int = 1,
        expected_limit: int = 10
    ) -> None:
        """
        Assert that paginated response has the correct structure.
        
        Args:
            response_data: Paginated response data
            expected_page: Expected current page
            expected_limit: Expected items per page
            
        Raises:
            AssertionError: If paginated response structure is invalid
        """
        required_fields = ["items", "total", "page", "limit", "has_next", "has_prev"]
        
        for field in required_fields:
            assert field in response_data, f"Missing required field: {field}"
        
        # Type assertions
        assert isinstance(response_data["items"], list), "Items should be a list"
        assert isinstance(response_data["total"], int), "Total should be an integer"
        assert isinstance(response_data["page"], int), "Page should be an integer"
        assert isinstance(response_data["limit"], int), "Limit should be an integer"
        assert isinstance(response_data["has_next"], bool), "has_next should be boolean"
        assert isinstance(response_data["has_prev"], bool), "has_prev should be boolean"
        
        # Value assertions
        assert response_data["total"] >= 0, "Total should be non-negative"
        assert response_data["page"] == expected_page, f"Expected page {expected_page}"
        assert response_data["limit"] == expected_limit, f"Expected limit {expected_limit}"
        assert len(response_data["items"]) <= response_data["limit"], "Items should not exceed limit"
        
        # Validate each book in items
        for book in response_data["items"]:
            APITestHelpers.assert_book_response_structure(book)
    
    @staticmethod
    def create_book_via_api(
        client: TestClient, 
        book_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a book via API and return the created book data.
        
        Args:
            client: Test client instance
            book_data: Book data to create
            
        Returns:
            Dict[str, Any]: Created book data
            
        Raises:
            AssertionError: If book creation fails
        """
        response = client.post("/books/", json=book_data)
        created_book = APITestHelpers.assert_successful_response(response, 201)
        APITestHelpers.assert_book_response_structure(created_book)
        return created_book
    
    @staticmethod
    def get_book_via_api(client: TestClient, book_id: int) -> Dict[str, Any]:
        """
        Get a book by ID via API and return the book data.
        
        Args:
            client: Test client instance
            book_id: Book ID to retrieve
            
        Returns:
            Dict[str, Any]: Book data
            
        Raises:
            AssertionError: If book retrieval fails
        """
        response = client.get(f"/books/{book_id}")
        book_data = APITestHelpers.assert_successful_response(response, 200)
        APITestHelpers.assert_book_response_structure(book_data)
        return book_data
    
    @staticmethod
    def get_books_via_api(
        client: TestClient, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get books with optional parameters via API.
        
        Args:
            client: Test client instance
            params: Optional query parameters
            
        Returns:
            Dict[str, Any]: Paginated response data
            
        Raises:
            AssertionError: If books retrieval fails
        """
        response = client.get("/books/", params=params or {})
        response_data = APITestHelpers.assert_successful_response(response, 200)
        APITestHelpers.assert_paginated_response_structure(response_data)
        return response_data
    
    @staticmethod
    def delete_book_via_api(client: TestClient, book_id: int) -> Dict[str, Any]:
        """
        Delete a book by ID via API and return the response.
        
        Args:
            client: Test client instance
            book_id: Book ID to delete
            
        Returns:
            Dict[str, Any]: Deletion response data
            
        Raises:
            AssertionError: If book deletion fails
        """
        response = client.delete(f"/books/{book_id}")
        return APITestHelpers.assert_successful_response(response, 200)


class ValidationTestHelpers:
    """Helper class for validation testing patterns."""
    
    @staticmethod
    def assert_validation_error(
        response: Response,
        field_name: str,
        error_type: Optional[str] = None
    ) -> None:
        """
        Assert that response contains a validation error for a specific field.
        
        Args:
            response: HTTP response object
            field_name: Name of the field that should have validation error
            error_type: Optional specific error type to check for
            
        Raises:
            AssertionError: If validation error is not as expected
        """
        assert response.status_code == 422, (
            f"Expected validation error (422), got {response.status_code}"
        )
        
        data = response.json()
        assert "detail" in data, "Validation error should contain detail"
        
        # Check if the field is mentioned in the error
        error_str = str(data["detail"]).lower()
        assert field_name.lower() in error_str, (
            f"Field '{field_name}' not mentioned in validation error: {data['detail']}"
        )
        
        if error_type:
            assert error_type.lower() in error_str, (
                f"Error type '{error_type}' not found in validation error: {data['detail']}"
            )
    
    @staticmethod
    def test_field_validation(
        client: TestClient,
        endpoint: str,
        method: str,
        base_data: Dict[str, Any],
        field_name: str,
        invalid_values: List[Any],
        valid_values: Optional[List[Any]] = None
    ) -> None:
        """
        Test field validation with multiple invalid and valid values.
        
        Args:
            client: Test client instance
            endpoint: API endpoint to test
            method: HTTP method (POST, PUT, etc.)
            base_data: Base valid data to modify
            field_name: Field name to test
            invalid_values: List of invalid values to test
            valid_values: Optional list of valid values to test
        """
        # Test invalid values
        for invalid_value in invalid_values:
            test_data = base_data.copy()
            test_data[field_name] = invalid_value
            
            if method.upper() == "POST":
                response = client.post(endpoint, json=test_data)
            elif method.upper() == "PUT":
                response = client.put(endpoint, json=test_data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            ValidationTestHelpers.assert_validation_error(response, field_name)
        
        # Test valid values if provided
        if valid_values:
            for valid_value in valid_values:
                test_data = base_data.copy()
                test_data[field_name] = valid_value
                
                if method.upper() == "POST":
                    response = client.post(endpoint, json=test_data)
                elif method.upper() == "PUT":
                    response = client.put(endpoint, json=test_data)
                
                assert response.status_code in [200, 201], (
                    f"Valid value {valid_value} for {field_name} should be accepted"
                )


class DataComparisonHelpers:
    """Helper class for comparing data structures in tests."""
    
    @staticmethod
    def assert_books_equal(
        actual: Dict[str, Any], 
        expected: Dict[str, Any],
        ignore_id: bool = False
    ) -> None:
        """
        Assert that two book objects are equal, with optional ID ignoring.
        
        Args:
            actual: Actual book data
            expected: Expected book data
            ignore_id: Whether to ignore ID field in comparison
            
        Raises:
            AssertionError: If books are not equal
        """
        if ignore_id:
            actual = {k: v for k, v in actual.items() if k != "id"}
            expected = {k: v for k, v in expected.items() if k != "id"}
        
        assert actual["title"] == expected["title"], "Titles should match"
        assert actual["author"] == expected["author"], "Authors should match"
        assert actual["year"] == expected["year"], "Years should match"
        assert actual["tags"] == expected["tags"], "Tags should match"
    
    @staticmethod
    def assert_books_sorted(
        books: List[Union[Dict[str, Any], Any]], 
        sort_field: str, 
        ascending: bool = True
    ) -> None:
        """
        Assert that a list of books is properly sorted by the specified field.
        
        Args:
            books: List of book objects or dictionaries to check
            sort_field: Field name to check sorting on ('year', 'author', etc.)
            ascending: Whether the sort should be ascending (True) or descending (False)
        """
        if len(books) <= 1:
            return  # Single item or empty list is always sorted
        
        # Handle both dictionary and object inputs
        values = []
        for book in books:
            if isinstance(book, dict):
                values.append(book[sort_field])
            else:
                values.append(getattr(book, sort_field))
        
        if ascending:
            expected_values = sorted(values)
            assert values == expected_values, f"Books not sorted ascending by {sort_field}. Got: {values}, Expected: {expected_values}"
        else:
            expected_values = sorted(values, reverse=True)
            assert values == expected_values, f"Books not sorted descending by {sort_field}. Got: {values}, Expected: {expected_values}"
    
    @staticmethod
    def assert_books_filtered(
        books: List[Dict[str, Any]], 
        filter_field: str, 
        filter_value: Union[str, int]
    ) -> None:
        """
        Assert that all books match the specified filter.
        
        Args:
            books: List of book dictionaries
            filter_field: Field to check filter on
            filter_value: Expected filter value
            
        Raises:
            AssertionError: If books don't match filter
        """
        for book in books:
            if filter_field == "author" or filter_field == "search":
                # Case-insensitive partial match for author and search
                actual_value = str(book.get(filter_field, "")).lower()
                expected_value = str(filter_value).lower()
                assert expected_value in actual_value, (
                    f"Book {book['id']} doesn't match filter {filter_field}={filter_value}"
                )
            else:
                # Exact match for other fields
                assert book.get(filter_field) == filter_value, (
                    f"Book {book['id']} doesn't match filter {filter_field}={filter_value}"
                ) 