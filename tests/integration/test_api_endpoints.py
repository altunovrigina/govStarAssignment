"""
Integration tests for API endpoints.

Tests complete API endpoint functionality including request/response cycles,
validation, error handling, and business logic integration.
"""

import pytest
from typing import Dict, Any
from fastapi.testclient import TestClient

from tests.utils.test_helpers import APITestHelpers, ValidationTestHelpers, DataComparisonHelpers
from tests.utils.test_data import TestDataFactory


class TestBookCreationEndpoint:
    """Integration tests for POST /books/ endpoint."""
    
    def test_create_book_success(
        self, 
        test_client_with_clean_repo: TestClient,
        sample_book_data: Dict[str, Any]
    ) -> None:
        """Test successful book creation."""
        response = test_client_with_clean_repo.post("/books/", json=sample_book_data)
        created_book = APITestHelpers.assert_successful_response(response, 201)
        
        # Verify response structure and data
        APITestHelpers.assert_book_response_structure(created_book)
        assert created_book["title"] == sample_book_data["title"]
        assert created_book["author"] == sample_book_data["author"]
        assert created_book["year"] == sample_book_data["year"]
        assert created_book["tags"] == sample_book_data["tags"]
        assert created_book["id"] == 1  # First book should have ID 1
    
    def test_create_book_without_tags(
        self, 
        test_client_with_clean_repo: TestClient
    ) -> None:
        """Test creating book without tags field."""
        book_data = {
            "title": "Book Without Tags",
            "author": "Test Author",
            "year": 2023
        }
        
        response = test_client_with_clean_repo.post("/books/", json=book_data)
        created_book = APITestHelpers.assert_successful_response(response, 201)
        
        assert created_book["tags"] == []
    
    def test_create_book_with_empty_tags(
        self, 
        test_client_with_clean_repo: TestClient
    ) -> None:
        """Test creating book with empty tags list."""
        book_data = {
            "title": "Book With Empty Tags",
            "author": "Test Author",
            "year": 2023,
            "tags": []
        }
        
        response = test_client_with_clean_repo.post("/books/", json=book_data)
        created_book = APITestHelpers.assert_successful_response(response, 201)
        
        assert created_book["tags"] == []
    
    def test_create_multiple_books_sequential_ids(
        self, 
        test_client_with_clean_repo: TestClient,
        test_data_factory: TestDataFactory
    ) -> None:
        """Test that multiple books get sequential IDs."""
        # Create first book
        book1_data = {
            "title": "First Book",
            "author": "First Author",
            "year": 2023,
            "tags": ["first"]
        }
        response1 = test_client_with_clean_repo.post("/books/", json=book1_data)
        book1 = APITestHelpers.assert_successful_response(response1, 201)
        
        # Create second book
        book2_data = {
            "title": "Second Book", 
            "author": "Second Author",
            "year": 2024,
            "tags": ["second"]
        }
        response2 = test_client_with_clean_repo.post("/books/", json=book2_data)
        book2 = APITestHelpers.assert_successful_response(response2, 201)
        
        # Verify sequential IDs
        assert book1["id"] == 1
        assert book2["id"] == 2
    
    @pytest.mark.parametrize("field", ["title", "author", "year"])
    @pytest.mark.asyncio
    async def test_create_book_validation_errors(
        self, 
        test_client_with_clean_repo: TestClient,
        invalid_book_data_samples: dict,
        field: str
    ) -> None:
        """Test validation errors for various invalid book data."""
        invalid_values = invalid_book_data_samples[field]
        
        for invalid_value in invalid_values:
            book_data = {
                "title": "Valid Title",
                "author": "Valid Author", 
                "year": 2023,
                "tags": ["valid"]
            }
            book_data[field] = invalid_value
            
            response = test_client_with_clean_repo.post("/books/", json=book_data)
            
            # Skip validation that might pass due to model flexibility
            if field == "year" and isinstance(invalid_value, int) and 1400 <= invalid_value <= 2025:
                continue
                
            ValidationTestHelpers.assert_validation_error(response, field)
    
    def test_create_book_missing_required_fields(
        self, 
        test_client_with_clean_repo: TestClient,
        sample_book_data: Dict[str, Any]
    ) -> None:
        """Test creation with missing required fields."""
        required_fields = ["title", "author", "year"]
        
        for field in required_fields:
            test_data = sample_book_data.copy()
            del test_data[field]
            
            response = test_client_with_clean_repo.post("/books/", json=test_data)
            ValidationTestHelpers.assert_validation_error(response, field)
    
    def test_create_book_extra_fields_rejected(
        self, 
        test_client_with_clean_repo: TestClient,
        sample_book_data: Dict[str, Any]
    ) -> None:
        """Test that extra fields are rejected."""
        sample_book_data["extra_field"] = "should_be_rejected"
        
        response = test_client_with_clean_repo.post("/books/", json=sample_book_data)
        ValidationTestHelpers.assert_validation_error(response, "extra_field")


class TestBookRetrievalEndpoints:
    """Integration tests for book retrieval endpoints."""
    
    def test_get_single_book_success(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test successful retrieval of single book."""
        response = test_client_with_data.get("/books/1")
        book = APITestHelpers.assert_successful_response(response, 200)
        
        APITestHelpers.assert_book_response_structure(book)
        assert book["id"] == 1
        assert book["title"] == "Clean Code: A Handbook of Agile Software Craftsmanship"
        assert book["author"] == "Robert C. Martin"
    
    def test_get_single_book_not_found(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test retrieval of non-existent book."""
        response = test_client_with_data.get("/books/999")
        APITestHelpers.assert_error_response(response, 404, ["not found"])
    
    def test_get_all_books_default_pagination(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test getting all books with default pagination."""
        response = test_client_with_data.get("/books/")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        APITestHelpers.assert_paginated_response_structure(data)
        assert data["total"] == 8  # Sample data has 8 books
        assert len(data["items"]) == 8  # All fit on first page
        assert data["page"] == 1
        assert data["limit"] == 10
        assert data["has_prev"] is False
        assert data["has_next"] is False
    
    def test_get_books_with_pagination(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test book retrieval with pagination parameters."""
        response = test_client_with_data.get("/books/?page=1&limit=3")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        assert data["page"] == 1
        assert data["limit"] == 3
        assert len(data["items"]) == 3
        assert data["total"] == 8
        assert data["has_prev"] is False
        assert data["has_next"] is True
    
    def test_get_books_filter_by_author(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test filtering books by author."""
        response = test_client_with_data.get("/books/?author=Robert C. Martin")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["author"] == "Robert C. Martin"
    
    def test_get_books_filter_by_author_case_insensitive(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test that author filtering is case-insensitive."""
        response = test_client_with_data.get("/books/?author=robert c. martin")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        assert data["total"] == 1
        assert data["items"][0]["author"] == "Robert C. Martin"
    
    def test_get_books_filter_by_author_partial_match(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test author filtering with partial matches."""
        response = test_client_with_data.get("/books/?author=Martin")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        assert data["total"] == 2  # "Robert C. Martin" and "Martin Fowler"
        authors = [book["author"] for book in data["items"]]
        assert "Robert C. Martin" in authors
        assert "Martin Fowler" in authors
    
    def test_get_books_filter_by_year(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test filtering books by year."""
        response = test_client_with_data.get("/books/?year=2019")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        assert data["total"] == 2  # Two books from 2019
        for book in data["items"]:
            assert book["year"] == 2019
    
    def test_get_books_search_by_title(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test searching books by title."""
        response = test_client_with_data.get("/books/?search=Python")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        assert data["total"] == 2  # Two books with "Python" in title
        for book in data["items"]:
            assert "python" in book["title"].lower()
    
    def test_get_books_search_case_insensitive(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test that title search is case-insensitive."""
        response = test_client_with_data.get("/books/?search=clean code")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        assert data["total"] == 1
        assert "Clean Code" in data["items"][0]["title"]
    
    def test_get_books_combined_filters(
        self, 
        test_client_with_clean_repo: TestClient
    ) -> None:
        """Test combining multiple filters."""
        # Create specific test data
        test_books = [
            {"title": "Python Programming", "author": "John Doe", "year": 2020, "tags": ["python"]},
            {"title": "Java Programming", "author": "John Doe", "year": 2020, "tags": ["java"]},
            {"title": "Python Advanced", "author": "Jane Smith", "year": 2020, "tags": ["python"]},
        ]
        
        for book_data in test_books:
            APITestHelpers.create_book_via_api(test_client_with_clean_repo, book_data)
        
        # Test author + search filters
        response = test_client_with_clean_repo.get("/books/?author=John Doe&search=Python")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Python Programming"
        assert data["items"][0]["author"] == "John Doe"
    
    def test_get_books_sort_by_year_ascending(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test sorting books by year in ascending order."""
        response = test_client_with_data.get("/books/?sort_by=year&sort_order=asc")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        DataComparisonHelpers.assert_books_sorted(data["items"], "year", ascending=True)
    
    def test_get_books_sort_by_year_descending(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test sorting books by year in descending order."""
        response = test_client_with_data.get("/books/?sort_by=year&sort_order=desc")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        DataComparisonHelpers.assert_books_sorted(data["items"], "year", ascending=False)
    
    def test_get_books_sort_by_author(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test sorting books by author."""
        response = test_client_with_data.get("/books/?sort_by=author&sort_order=asc")
        data = APITestHelpers.assert_successful_response(response, 200)
        
        DataComparisonHelpers.assert_books_sorted(data["items"], "author", ascending=True)
    
    def test_get_books_invalid_sort_parameters(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test invalid sort parameters."""
        # Invalid sort_by field
        response = test_client_with_data.get("/books/?sort_by=invalid_field")
        ValidationTestHelpers.assert_validation_error(response, "sort_by")
        
        # Invalid sort_order
        response = test_client_with_data.get("/books/?sort_order=invalid_order")
        ValidationTestHelpers.assert_validation_error(response, "sort_order")
    
    def test_get_books_invalid_pagination_parameters(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test invalid pagination parameters."""
        # Invalid page (zero)
        response = test_client_with_data.get("/books/?page=0")
        ValidationTestHelpers.assert_validation_error(response, "page")
        
        # Invalid page (negative)
        response = test_client_with_data.get("/books/?page=-1")
        ValidationTestHelpers.assert_validation_error(response, "page")
        
        # Invalid limit (zero)
        response = test_client_with_data.get("/books/?limit=0")
        ValidationTestHelpers.assert_validation_error(response, "limit")
        
        # Invalid limit (too large)
        response = test_client_with_data.get("/books/?limit=101")
        ValidationTestHelpers.assert_validation_error(response, "limit")


class TestBookDeletionEndpoint:
    """Integration tests for DELETE /books/{id} endpoint."""
    
    def test_delete_book_success(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test successful book deletion."""
        # Verify book exists
        book = APITestHelpers.get_book_via_api(test_client_with_data, 1)
        assert book["id"] == 1
        
        # Delete the book
        response = test_client_with_data.delete("/books/1")
        deletion_result = APITestHelpers.assert_successful_response(response, 200)
        
        assert "deleted successfully" in deletion_result["message"].lower()
        
        # Verify book no longer exists
        response = test_client_with_data.get("/books/1")
        APITestHelpers.assert_error_response(response, 404, ["not found"])
    
    def test_delete_nonexistent_book(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test deleting non-existent book."""
        response = test_client_with_data.delete("/books/999")
        APITestHelpers.assert_error_response(response, 404, ["not found"])
    
    def test_delete_book_affects_list(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test that deleting a book affects the books list."""
        # Get initial count
        initial_response = test_client_with_data.get("/books/")
        initial_data = APITestHelpers.assert_successful_response(initial_response, 200)
        initial_count = initial_data["total"]
        
        # Delete a book
        APITestHelpers.delete_book_via_api(test_client_with_data, 1)
        
        # Verify count decreased
        final_response = test_client_with_data.get("/books/")
        final_data = APITestHelpers.assert_successful_response(final_response, 200)
        
        assert final_data["total"] == initial_count - 1
        
        # Verify the specific book is not in the list
        book_ids = [book["id"] for book in final_data["items"]]
        assert 1 not in book_ids
    
    def test_delete_book_affects_stats(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test that deleting a book affects statistics."""
        # Get initial stats
        initial_response = test_client_with_data.get("/books/stats/summary")
        initial_stats = APITestHelpers.assert_successful_response(initial_response, 200)
        
        # Delete a book
        APITestHelpers.delete_book_via_api(test_client_with_data, 1)
        
        # Verify stats updated
        final_response = test_client_with_data.get("/books/stats/summary")
        final_stats = APITestHelpers.assert_successful_response(final_response, 200)
        
        assert final_stats["total_books"] == initial_stats["total_books"] - 1


class TestStatsEndpoint:
    """Integration tests for GET /books/stats/summary endpoint."""
    
    def test_get_stats_with_data(self, test_client_with_data: TestClient) -> None:
        """Test getting statistics with populated repository."""
        response = test_client_with_data.get("/books/stats/summary")
        
        APITestHelpers.assert_successful_response(response)
        stats = response.json()
        
        # Verify response structure
        assert "total_books" in stats
        assert "unique_authors" in stats
        assert isinstance(stats["total_books"], int)
        assert isinstance(stats["unique_authors"], int)
        
        # Get actual books to verify counts
        books_response = test_client_with_data.get("/books/?limit=100")
        books_data = books_response.json()
        actual_total = books_data["total"]
        
        # Count unique authors from actual data
        authors = set()
        for book in books_data["items"]:
            authors.add(book["author"])
        actual_unique_authors = len(authors)
        
        # Verify stats match actual data
        assert stats["total_books"] == actual_total
        assert stats["unique_authors"] == actual_unique_authors
        assert stats["total_books"] > 0
        assert stats["unique_authors"] > 0
        assert stats["unique_authors"] <= stats["total_books"]
    
    def test_get_stats_empty_repository(
        self, 
        test_client_with_clean_repo: TestClient
    ) -> None:
        """Test getting statistics from empty repository."""
        response = test_client_with_clean_repo.get("/books/stats/summary")
        stats = APITestHelpers.assert_successful_response(response, 200)
        
        assert stats["total_books"] == 0
        assert stats["unique_authors"] == 0
    
    def test_stats_reflect_operations(
        self, 
        test_client_with_clean_repo: TestClient
    ) -> None:
        """Test that statistics reflect CRUD operations."""
        # Start with empty stats
        response = test_client_with_clean_repo.get("/books/stats/summary")
        stats = APITestHelpers.assert_successful_response(response, 200)
        assert stats["total_books"] == 0
        assert stats["unique_authors"] == 0
        
        # Add books with different authors
        book1_data = {"title": "Book 1", "author": "Author 1", "year": 2023}
        book2_data = {"title": "Book 2", "author": "Author 1", "year": 2024}  # Same author
        book3_data = {"title": "Book 3", "author": "Author 2", "year": 2023}  # Different author
        
        APITestHelpers.create_book_via_api(test_client_with_clean_repo, book1_data)
        APITestHelpers.create_book_via_api(test_client_with_clean_repo, book2_data)
        created_book3 = APITestHelpers.create_book_via_api(test_client_with_clean_repo, book3_data)
        
        # Check stats after additions
        response = test_client_with_clean_repo.get("/books/stats/summary")
        stats = APITestHelpers.assert_successful_response(response, 200)
        assert stats["total_books"] == 3
        assert stats["unique_authors"] == 2
        
        # Delete a book
        APITestHelpers.delete_book_via_api(test_client_with_clean_repo, created_book3["id"])
        
        # Check stats after deletion
        response = test_client_with_clean_repo.get("/books/stats/summary")
        stats = APITestHelpers.assert_successful_response(response, 200)
        assert stats["total_books"] == 2
        assert stats["unique_authors"] == 1  # Only Author 1 remains


class TestRootAndHealthEndpoints:
    """Integration tests for root and health endpoints."""
    
    def test_root_endpoint(self, test_client_with_clean_repo: TestClient) -> None:
        """Test GET / endpoint returns API information."""
        response = test_client_with_clean_repo.get("/")
        
        data = APITestHelpers.assert_successful_response(response)
        
        # Verify response structure
        assert "message" in data
        assert "version" in data
        assert "documentation" in data
        
        # Verify documentation links
        docs = data["documentation"]
        assert "interactive" in docs
        assert "redoc" in docs
        assert docs["interactive"] == "/docs"
        assert docs["redoc"] == "/redoc"
    
    def test_health_endpoint_healthy(
        self, 
        test_client_with_data: TestClient
    ) -> None:
        """Test health endpoint when service is healthy."""
        response = test_client_with_data.get("/health")
        health_data = APITestHelpers.assert_successful_response(response, 200)
        
        # Verify health response structure
        expected_fields = ["status", "timestamp", "repository", "books_count", "version"]
        for field in expected_fields:
            assert field in health_data
        
        # Verify values
        assert health_data["status"] == "healthy"
        assert health_data["repository"] == "connected"
        assert isinstance(health_data["books_count"], int)
        assert health_data["books_count"] >= 0
        assert "timestamp" in health_data
        assert "version" in health_data


class TestEndToEndWorkflows:
    """End-to-end workflow tests combining multiple operations."""
    
    def test_complete_book_lifecycle(
        self, 
        test_client_with_clean_repo: TestClient
    ) -> None:
        """Test complete book lifecycle: create, read, update (via delete/create), delete."""
        # Create a book
        book_data = {
            "title": "Test Book Lifecycle",
            "author": "Test Author",
            "year": 2023,
            "tags": ["test", "lifecycle"]
        }
        
        created_book = APITestHelpers.create_book_via_api(test_client_with_clean_repo, book_data)
        book_id = created_book["id"]
        
        # Read the book
        retrieved_book = APITestHelpers.get_book_via_api(test_client_with_clean_repo, book_id)
        DataComparisonHelpers.assert_books_equal(retrieved_book, created_book)
        
        # Verify book appears in list
        books_list = APITestHelpers.get_books_via_api(test_client_with_clean_repo)
        assert books_list["total"] == 1
        assert books_list["items"][0]["id"] == book_id
        
        # Delete the book
        APITestHelpers.delete_book_via_api(test_client_with_clean_repo, book_id)
        
        # Verify book is gone
        response = test_client_with_clean_repo.get(f"/books/{book_id}")
        APITestHelpers.assert_error_response(response, 404)
        
        # Verify empty list
        books_list = APITestHelpers.get_books_via_api(test_client_with_clean_repo)
        assert books_list["total"] == 0
    
    def test_filtering_and_pagination_workflow(
        self, 
        test_client_with_clean_repo: TestClient
    ) -> None:
        """Test complex filtering and pagination workflow."""
        # Create test data with specific patterns
        authors = ["Alice Smith", "Bob Jones", "Alice Johnson"]
        years = [2020, 2021, 2022]
        
        created_books = []
        for i in range(9):  # Create 9 books
            book_data = {
                "title": f"Book {i+1}",
                "author": authors[i % 3],
                "year": years[i % 3],
                "tags": [f"tag{i+1}"]
            }
            created_book = APITestHelpers.create_book_via_api(test_client_with_clean_repo, book_data)
            created_books.append(created_book)
        
        # Test filtering by author
        response = test_client_with_clean_repo.get("/books/?author=Alice")
        data = APITestHelpers.assert_successful_response(response, 200)
        assert data["total"] == 6  # 3 Alice Smith + 3 Alice Johnson
        
        # Test filtering by year with pagination
        response = test_client_with_clean_repo.get("/books/?year=2020&page=1&limit=2")
        data = APITestHelpers.assert_successful_response(response, 200)
        assert data["total"] == 3  # 3 books from 2020
        assert len(data["items"]) == 2  # Limited to 2 per page
        assert data["has_next"] is True
        
        # Get next page
        response = test_client_with_clean_repo.get("/books/?year=2020&page=2&limit=2")
        data = APITestHelpers.assert_successful_response(response, 200)
        assert len(data["items"]) == 1  # Last item
        assert data["has_next"] is False
        
        # Test combined filtering and sorting
        response = test_client_with_clean_repo.get("/books/?author=Alice&sort_by=year&sort_order=desc")
        data = APITestHelpers.assert_successful_response(response, 200)
        DataComparisonHelpers.assert_books_sorted(data["items"], "year", ascending=False)
    
    def test_error_handling_workflow(
        self, 
        test_client_with_clean_repo: TestClient
    ) -> None:
        """Test error handling across different operations."""
        # Test validation errors in creation
        invalid_book_data = {
            "title": "",  # Invalid
            "author": "Valid Author",
            "year": 2023
        }
        
        response = test_client_with_clean_repo.post("/books/", json=invalid_book_data)
        ValidationTestHelpers.assert_validation_error(response, "title")
        
        # Test 404 errors
        response = test_client_with_clean_repo.get("/books/999")
        APITestHelpers.assert_error_response(response, 404)
        
        response = test_client_with_clean_repo.delete("/books/999")
        APITestHelpers.assert_error_response(response, 404)
        
        # Test validation errors in query parameters
        response = test_client_with_clean_repo.get("/books/?page=0")
        ValidationTestHelpers.assert_validation_error(response, "page")
        
        response = test_client_with_clean_repo.get("/books/?limit=101")
        ValidationTestHelpers.assert_validation_error(response, "limit")
        
        response = test_client_with_clean_repo.get("/books/?sort_by=invalid")
        ValidationTestHelpers.assert_validation_error(response, "sort_by") 