"""
Unit tests for service layer components.

This module tests the service layer functionality including pagination,
data processing, and business logic services.
"""

import pytest
from typing import List

from app.services.pagination_service import PaginationService
from tests.utils.test_data import TestDataFactory


class TestPaginationService:
    """Test class for PaginationService functionality."""

    @pytest.fixture
    def sample_books(self, test_data_factory: TestDataFactory) -> List:
        """Create sample books for pagination testing with valid years."""
        return [
            test_data_factory.create_book_response(i, f"Book {i}", f"Author {i}", 2020 + (i % 5))
            for i in range(1, 11)  # Creates books with years 2020-2024
        ]

    @pytest.mark.asyncio
    async def test_paginate_first_page(self, sample_books: List) -> None:
        """Test pagination for the first page."""
        result = PaginationService.paginate(sample_books, page=1, limit=3)
        
        assert len(result.items) == 3
        assert result.items[0].title == "Book 1"
        assert result.items[1].title == "Book 2"
        assert result.items[2].title == "Book 3"
        assert result.total == 10
        assert result.page == 1
        assert result.limit == 3
        assert result.has_next is True
        assert result.has_prev is False

    @pytest.mark.asyncio
    async def test_paginate_middle_page(self, sample_books: List) -> None:
        """Test pagination for a middle page."""
        result = PaginationService.paginate(sample_books, page=2, limit=3)
        
        assert len(result.items) == 3
        assert result.items[0].title == "Book 4"
        assert result.items[1].title == "Book 5"
        assert result.items[2].title == "Book 6"
        assert result.total == 10
        assert result.page == 2
        assert result.has_next is True
        assert result.has_prev is True

    @pytest.mark.asyncio
    async def test_paginate_last_page_partial(self, sample_books: List) -> None:
        """Test pagination for the last page with partial results."""
        result = PaginationService.paginate(sample_books, page=4, limit=3)
        
        assert len(result.items) == 1  # Only 1 item on last page (10 total, 3 per page)
        assert result.items[0].title == "Book 10"
        assert result.total == 10
        assert result.has_next is False
        assert result.has_prev is True

    @pytest.mark.asyncio
    async def test_paginate_single_page_all_items(self, sample_books: List) -> None:
        """Test pagination when all items fit on one page."""
        result = PaginationService.paginate(sample_books, page=1, limit=20)
        
        assert len(result.items) == 10  # All 10 books
        assert result.items[0].title == "Book 1"
        assert result.items[-1].title == "Book 10"
        assert result.total == 10
        assert result.has_next is False
        assert result.has_prev is False

    @pytest.mark.asyncio
    async def test_paginate_empty_list(self) -> None:
        """Test pagination with empty list."""
        result = PaginationService.paginate([], page=1, limit=10)
        
        assert len(result.items) == 0
        assert result.items == []
        assert result.total == 0
        assert result.has_next is False
        assert result.has_prev is False

    @pytest.mark.asyncio
    async def test_paginate_page_beyond_available(self, sample_books: List) -> None:
        """Test pagination beyond available pages."""
        result = PaginationService.paginate(sample_books, page=10, limit=5)
        
        assert len(result.items) == 0
        assert result.items == []
        assert result.total == 10
        assert result.has_next is False
        assert result.has_prev is True

    @pytest.mark.parametrize("test_case", TestDataFactory.get_pagination_test_cases())
    @pytest.mark.asyncio
    async def test_pagination_scenarios(self, test_case: dict, test_data_factory: TestDataFactory) -> None:
        """Test various pagination scenarios using parametrized test cases."""
        # Create test data
        items = [
            test_data_factory.create_book_response(i, f"Book {i}", f"Author {i}", 2020 + (i % 5))
            for i in range(1, test_case["total_items"] + 1)
        ]
        
        # Paginate
        result = PaginationService.paginate(
            items, 
            page=test_case["page"], 
            limit=test_case["limit"]
        )
        
        # Verify results
        assert len(result.items) == test_case["expected_count"]
        assert result.total == test_case["total_items"]
        
        if test_case["expected_count"] > 0 and test_case["expected_first_id"] is not None:
            expected_first_id = test_case["expected_first_id"]
            assert result.items[0].id == expected_first_id

    @pytest.mark.asyncio
    async def test_paginate_with_single_item(self, test_data_factory: TestDataFactory) -> None:
        """Test pagination with single item."""
        items = [test_data_factory.create_book_response(1, "Single Book", "Single Author", 2023)]
        
        result = PaginationService.paginate(items, page=1, limit=10)
        
        assert len(result.items) == 1
        assert result.items[0].title == "Single Book"
        assert result.total == 1

    @pytest.mark.asyncio
    async def test_paginate_edge_case_limit_one(self, sample_books: List) -> None:
        """Test pagination with limit of 1."""
        result = PaginationService.paginate(sample_books, page=5, limit=1)
        
        assert len(result.items) == 1
        assert result.items[0].title == "Book 5"
        assert result.total == 10

    @pytest.mark.asyncio
    async def test_paginate_maintains_item_order(self, test_data_factory: TestDataFactory) -> None:
        """Test that pagination maintains the original order of items."""
        # Create items in specific order
        items = [
            test_data_factory.create_book_response(3, "Book C", "Author C", 2023),
            test_data_factory.create_book_response(1, "Book A", "Author A", 2021),
            test_data_factory.create_book_response(2, "Book B", "Author B", 2022),
        ]
        
        result = PaginationService.paginate(items, page=1, limit=2)
        
        assert len(result.items) == 2
        assert result.items[0].title == "Book C"  # First item in original order
        assert result.items[1].title == "Book A"  # Second item in original order

    @pytest.mark.asyncio
    async def test_paginate_boundary_conditions(self, test_data_factory: TestDataFactory) -> None:
        """Test pagination boundary conditions."""
        items = [
            test_data_factory.create_book_response(i, f"Book {i}", f"Author {i}", 2020 + (i % 5))
            for i in range(1, 6)  # 5 items total
        ]
        
        # Test exact page boundary
        result = PaginationService.paginate(items, page=2, limit=3)
        assert len(result.items) == 2  # Items 4 and 5
        assert result.items[0].title == "Book 4"
        assert result.items[1].title == "Book 5"
        
        # Test page that would be exactly empty
        result = PaginationService.paginate(items, page=3, limit=3)
        assert len(result.items) == 0 