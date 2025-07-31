"""
Test data factory for generating consistent, reusable test data.

This module implements the Factory pattern to provide clean, maintainable
test data generation.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models import BookResponse, BookCreate, BookFilters


class TestDataFactory:
    """
    Factory class for generating test data with consistent patterns.
    
    This class provides methods to create various types of test data
    while maintaining consistency and avoiding duplication across tests.
    """
    
    @staticmethod
    def create_book_response(
        book_id: int = 1,
        title: str = "Default Test Book",
        author: str = "Default Test Author", 
        year: int = 2023,
        tags: Optional[List[str]] = None
    ) -> BookResponse:
        """
        Create a BookResponse instance with default or custom values.
        
        Args:
            book_id: Book ID
            title: Book title
            author: Book author
            year: Publication year
            tags: Optional list of tags
            
        Returns:
            BookResponse: Configured book response object
        """
        return BookResponse(
            id=book_id,
            title=title,
            author=author,
            year=year,
            tags=tags or []
        )
    
    @staticmethod
    def create_book_create(
        title: str = "Default Test Book",
        author: str = "Default Test Author",
        year: int = 2023,
        tags: Optional[List[str]] = None
    ) -> BookCreate:
        """
        Create a BookCreate instance with default or custom values.
        
        Args:
            title: Book title
            author: Book author
            year: Publication year
            tags: Optional list of tags
            
        Returns:
            BookCreate: Configured book creation object
        """
        return BookCreate(
            title=title,
            author=author,
            year=year,
            tags=tags or []
        )
    
    def create_sample_books(self) -> List[BookResponse]:
        """
        Create a diverse set of sample books for testing.
        
        This provides a consistent dataset across tests while covering
        various edge cases and scenarios.
        
        Returns:
            List[BookResponse]: List of sample books
        """
        return [
            self.create_book_response(
                book_id=1,
                title="Clean Code: A Handbook of Agile Software Craftsmanship",
                author="Robert C. Martin",
                year=2008,
                tags=["programming", "software engineering", "best practices"]
            ),
            self.create_book_response(
                book_id=2,
                title="The Pragmatic Programmer",
                author="Andrew Hunt",
                year=1999,
                tags=["programming", "career", "methodology"]
            ),
            self.create_book_response(
                book_id=3,
                title="Design Patterns: Elements of Reusable Object-Oriented Software",
                author="Gang of Four",
                year=1994,
                tags=["design patterns", "object-oriented", "architecture"]
            ),
            self.create_book_response(
                book_id=4,
                title="Effective Python: 90 Specific Ways to Write Better Python",
                author="Brett Slatkin",
                year=2019,
                tags=["python", "programming", "best practices"]
            ),
            self.create_book_response(
                book_id=5,
                title="Python Crash Course",
                author="Eric Matthes",
                year=2019,
                tags=["python", "beginner", "tutorial"]
            ),
            self.create_book_response(
                book_id=6,
                title="The Art of Computer Programming",
                author="Donald Knuth",
                year=1968,
                tags=["algorithms", "computer science", "mathematics"]
            ),
            self.create_book_response(
                book_id=7,
                title="Refactoring: Improving the Design of Existing Code",
                author="Martin Fowler",
                year=2018,
                tags=["refactoring", "software engineering", "code quality"]
            ),
            self.create_book_response(
                book_id=8,
                title="Test Book Without Tags",
                author="Test Author",
                year=2023,
                tags=[]
            )
        ]
    
    def create_books_by_author(self, author: str, count: int = 3) -> List[BookResponse]:
        """
        Create multiple books by the same author for testing filtering.
        
        Args:
            author: Author name
            count: Number of books to create
            
        Returns:
            List[BookResponse]: Books by the specified author
        """
        return [
            self.create_book_response(
                book_id=i,
                title=f"Book {i} by {author}",
                author=author,
                year=2020 + i,
                tags=[f"tag{i}", "test"]
            )
            for i in range(1, count + 1)
        ]
    
    def create_books_by_year(self, year: int, count: int = 3) -> List[BookResponse]:
        """
        Create multiple books from the same year for testing filtering.
        
        Args:
            year: Publication year
            count: Number of books to create
            
        Returns:
            List[BookResponse]: Books from the specified year
        """
        return [
            self.create_book_response(
                book_id=i,
                title=f"Book {i} from {year}",
                author=f"Author {i}",
                year=year,
                tags=[f"year-{year}", "test"]
            )
            for i in range(1, count + 1)
        ]
    
    @staticmethod
    def create_book_filters(
        author: Optional[str] = None,
        year: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        page: int = 1,
        limit: int = 10
    ) -> BookFilters:
        """
        Create BookFilters instance with specified parameters.
        
        Args:
            author: Filter by author
            year: Filter by year
            search: Search term
            sort_by: Sort field
            sort_order: Sort order (asc/desc)
            page: Page number
            limit: Items per page
            
        Returns:
            BookFilters: Configured filters object
        """
        return BookFilters(
            author=author,
            year=year,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            limit=limit
        )
    
    @staticmethod
    def get_boundary_years() -> Dict[str, int]:
        """
        Get boundary year values for validation testing.
        
        Returns:
            Dict[str, int]: Dictionary of boundary year values
        """
        current_year = datetime.now().year
        return {
            "min_valid": 1400,
            "min_invalid": 1399,
            "max_valid": current_year,
            "max_invalid": current_year + 1,
            "typical": 2023
        }
    
    @staticmethod
    def get_validation_test_cases() -> Dict[str, Dict[str, Any]]:
        """
        Get comprehensive validation test cases for model testing.
        
        Returns:
            Dict[str, Dict[str, Any]]: Test cases for validation
        """
        current_year = datetime.now().year
        
        return {
            # Valid cases
            "valid_minimal": {
                "title": "Valid Book",
                "author": "Valid Author",
                "year": 2023,
                "expected_valid": True
            },
            "valid_with_tags": {
                "title": "Valid Book with Tags",
                "author": "Valid Author",
                "year": 2023,
                "tags": ["fiction", "adventure"],
                "expected_valid": True
            },
            "valid_boundary_year_min": {
                "title": "Ancient Book",
                "author": "Ancient Author",
                "year": 1400,
                "expected_valid": True
            },
            "valid_boundary_year_max": {
                "title": "Current Book",
                "author": "Current Author", 
                "year": current_year,
                "expected_valid": True
            },
            
            # Invalid cases - Title
            "invalid_empty_title": {
                "title": "",
                "author": "Valid Author",
                "year": 2023,
                "expected_valid": False,
                "expected_error": "title"
            },
            "invalid_whitespace_title": {
                "title": "   ",
                "author": "Valid Author",
                "year": 2023,
                "expected_valid": False,
                "expected_error": "title"
            },
            "invalid_long_title": {
                "title": "x" * 501,
                "author": "Valid Author",
                "year": 2023,
                "expected_valid": False,
                "expected_error": "title"
            },
            
            # Invalid cases - Author
            "invalid_empty_author": {
                "title": "Valid Title",
                "author": "",
                "year": 2023,
                "expected_valid": False,
                "expected_error": "author"
            },
            "invalid_whitespace_author": {
                "title": "Valid Title",
                "author": "   ",
                "year": 2023,
                "expected_valid": False,
                "expected_error": "author"
            },
            "invalid_long_author": {
                "title": "Valid Title",
                "author": "x" * 201,
                "year": 2023,
                "expected_valid": False,
                "expected_error": "author"
            },
            
            # Invalid cases - Year
            "invalid_year_too_early": {
                "title": "Valid Title",
                "author": "Valid Author",
                "year": 1399,
                "expected_valid": False,
                "expected_error": "year"
            },
            "invalid_year_too_late": {
                "title": "Valid Title",
                "author": "Valid Author",
                "year": current_year + 1,
                "expected_valid": False,
                "expected_error": "year"
            }
        }
    
    @staticmethod
    def get_pagination_test_cases() -> List[Dict[str, Any]]:
        """
        Get test cases for pagination testing.
        
        Returns:
            List[Dict[str, Any]]: Pagination test scenarios
        """
        return [
            {
                "name": "first_page_default_limit",
                "page": 1,
                "limit": 10,
                "total_items": 25,
                "expected_count": 10,
                "expected_first_id": 1,
                "expected_has_next": True,
                "expected_has_prev": False
            },
            {
                "name": "middle_page",
                "page": 2,
                "limit": 10,
                "total_items": 25,
                "expected_count": 10,
                "expected_first_id": 11,
                "expected_has_next": True,
                "expected_has_prev": True
            },
            {
                "name": "last_page_partial",
                "page": 3,
                "limit": 10,
                "total_items": 25,
                "expected_count": 5,
                "expected_first_id": 21,
                "expected_has_next": False,
                "expected_has_prev": True
            },
            {
                "name": "single_page_all_items",
                "page": 1,
                "limit": 50,
                "total_items": 25,
                "expected_count": 25,
                "expected_first_id": 1,
                "expected_has_next": False,
                "expected_has_prev": False
            },
            {
                "name": "empty_result",
                "page": 1,
                "limit": 10,
                "total_items": 0,
                "expected_count": 0,
                "expected_first_id": None,  # No items, so no first ID
                "expected_has_next": False,
                "expected_has_prev": False
            }
        ] 