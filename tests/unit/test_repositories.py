"""
Unit tests for book repository implementations.

This module tests the InMemoryBookRepository class, covering all CRUD operations,
filtering, sorting, pagination, and statistics functionality.
"""

import pytest
from typing import List

from app.models.book import BookResponse, BookFilters, StatsResponse
from app.repositories.book_repository import InMemoryBookRepository
from tests.utils.test_data import TestDataFactory
from tests.utils.test_helpers import DataComparisonHelpers


class TestInMemoryBookRepository:
    """Test class for InMemoryBookRepository basic functionality."""

    @pytest.mark.asyncio
    async def test_repository_initialization(self, clean_repository: InMemoryBookRepository) -> None:
        """Test that repository initializes correctly."""
        stats = await clean_repository.get_stats()
        assert stats.total_books == 0
        assert stats.unique_authors == 0


class TestBookCreation:
    """Test class for book creation operations."""

    @pytest.mark.asyncio
    async def test_create_single_book(
        self,
        clean_repository: InMemoryBookRepository,
        test_data_factory: TestDataFactory
    ) -> None:
        """Test creating a single book."""
        book_data = test_data_factory.create_book_create(
            title="Test Book",
            author="Test Author",
            year=2023,
            tags=["test"]
        )

        created_book = await clean_repository.create_book(book_data)

        # Verify created book structure
        assert isinstance(created_book, BookResponse)
        assert created_book.id == 1  # First book should have ID 1
        assert created_book.title == "Test Book"
        assert created_book.author == "Test Author"
        assert created_book.year == 2023
        assert created_book.tags == ["test"]

    @pytest.mark.asyncio
    async def test_create_multiple_books_sequential(
        self,
        clean_repository: InMemoryBookRepository,
        test_data_factory: TestDataFactory
    ) -> None:
        """Test creating multiple books with sequential IDs."""
        book1_data = test_data_factory.create_book_create("Book 1", "Author 1", 2023)
        book2_data = test_data_factory.create_book_create("Book 2", "Author 2", 2024)

        created_book1 = await clean_repository.create_book(book1_data)
        created_book2 = await clean_repository.create_book(book2_data)

        # Verify sequential ID assignment
        assert created_book1.id == 1
        assert created_book2.id == 2

        # Verify data integrity
        assert created_book1.title == "Book 1"
        assert created_book2.title == "Book 2"

    @pytest.mark.asyncio
    async def test_create_book_with_empty_tags(
        self,
        clean_repository: InMemoryBookRepository,
        test_data_factory: TestDataFactory
    ) -> None:
        """Test creating book with empty tags list."""
        book_data = test_data_factory.create_book_create(
            title="Book Without Tags",
            author="Test Author",
            year=2023,
            tags=None  # Should be converted to empty list
        )

        created_book = await clean_repository.create_book(book_data)

        assert created_book.tags == []

    @pytest.mark.asyncio
    async def test_id_generation_after_initial_load(
        self,
        clean_repository: InMemoryBookRepository,
        test_data_factory: TestDataFactory
    ) -> None:
        """Test that ID generation continues correctly after loading initial books."""
        # Load initial books with specific IDs
        initial_books = [
            test_data_factory.create_book_response(5, "Initial Book 1", "Author 1", 2023),
            test_data_factory.create_book_response(10, "Initial Book 2", "Author 2", 2024)
        ]
        await clean_repository.load_initial_books(initial_books)

        # Create new book - should get ID 11 (max existing ID + 1)
        new_book_data = test_data_factory.create_book_create("New Book", "New Author", 2025)
        created_book = await clean_repository.create_book(new_book_data)

        assert created_book.id == 11


class TestBookRetrieval:
    """Test class for book retrieval operations."""

    @pytest.mark.asyncio
    async def test_get_existing_book(self, populated_repository: InMemoryBookRepository) -> None:
        """Test retrieving an existing book."""
        book = await populated_repository.get_book(1)
        
        assert book is not None
        assert book.id == 1
        assert isinstance(book, BookResponse)

    @pytest.mark.asyncio
    async def test_get_nonexistent_book(self, populated_repository: InMemoryBookRepository) -> None:
        """Test retrieving a non-existent book."""
        book = await populated_repository.get_book(9999)
        assert book is None

    @pytest.mark.asyncio
    async def test_get_book_from_empty_repository(
        self,
        clean_repository: InMemoryBookRepository
    ) -> None:
        """Test retrieving book from empty repository."""
        book = await clean_repository.get_book(1)
        assert book is None


class TestBookDeletion:
    """Test class for book deletion operations."""

    @pytest.mark.asyncio
    async def test_delete_existing_book(self, populated_repository: InMemoryBookRepository) -> None:
        """Test deleting an existing book."""
        # Verify book exists first
        book = await populated_repository.get_book(1)
        assert book is not None

        # Delete the book
        result = await populated_repository.delete_book(1)
        assert result is True

        # Verify book is gone
        book = await populated_repository.get_book(1)
        assert book is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_book(self, populated_repository: InMemoryBookRepository) -> None:
        """Test deleting a non-existent book."""
        result = await populated_repository.delete_book(9999)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_from_empty_repository(
        self,
        clean_repository: InMemoryBookRepository
    ) -> None:
        """Test deleting from empty repository."""
        result = await clean_repository.delete_book(1)
        assert result is False


class TestBookFiltering:
    """Test class for book filtering operations."""

    @pytest.mark.asyncio
    async def test_get_all_books_no_filters(self, populated_repository: InMemoryBookRepository) -> None:
        """Test getting all books without filters."""
        filters = BookFilters()
        result = await populated_repository.get_books(filters)
        
        assert result.total > 0
        assert len(result.items) > 0
        assert result.page == 1
        assert result.limit == 10

    @pytest.mark.asyncio
    async def test_filter_by_author(self, populated_repository: InMemoryBookRepository) -> None:
        """Test filtering books by author."""
        # Get sample data to find a valid author
        all_books = await populated_repository.get_books(BookFilters(limit=100))
        if all_books.items:
            sample_author = all_books.items[0].author
            
            filters = BookFilters(author=sample_author)
            result = await populated_repository.get_books(filters)
            
            assert result.total > 0
            for book in result.items:
                assert sample_author.lower() in book.author.lower()

    @pytest.mark.asyncio
    async def test_filter_by_author_case_insensitive(self, populated_repository: InMemoryBookRepository) -> None:
        """Test that author filtering is case-insensitive."""
        # Get sample data
        all_books = await populated_repository.get_books(BookFilters(limit=100))
        if all_books.items:
            sample_author = all_books.items[0].author
            
            filters = BookFilters(author=sample_author.upper())
            result = await populated_repository.get_books(filters)
            
            assert result.total > 0
            for book in result.items:
                assert sample_author.lower() in book.author.lower()

    @pytest.mark.asyncio
    async def test_filter_by_author_partial_match(self, populated_repository: InMemoryBookRepository) -> None:
        """Test filtering by partial author name."""
        # Get sample data
        all_books = await populated_repository.get_books(BookFilters(limit=100))
        if all_books.items:
            sample_author = all_books.items[0].author
            partial_author = sample_author[:3]  # First 3 characters
            
            filters = BookFilters(author=partial_author)
            result = await populated_repository.get_books(filters)
            
            for book in result.items:
                assert partial_author.lower() in book.author.lower()

    @pytest.mark.asyncio
    async def test_filter_by_year(self, populated_repository: InMemoryBookRepository) -> None:
        """Test filtering books by year."""
        # Get sample data to find a valid year
        all_books = await populated_repository.get_books(BookFilters(limit=100))
        if all_books.items:
            sample_year = all_books.items[0].year
            
            filters = BookFilters(year=sample_year)
            result = await populated_repository.get_books(filters)
            
            for book in result.items:
                assert book.year == sample_year

    @pytest.mark.asyncio
    async def test_filter_by_nonexistent_year(self, populated_repository: InMemoryBookRepository) -> None:
        """Test filtering by a year that doesn't exist."""
        filters = BookFilters(year=1800)  # Year that definitely doesn't exist in sample data
        result = await populated_repository.get_books(filters)
        
        assert result.total == 0
        assert len(result.items) == 0

    @pytest.mark.asyncio
    async def test_search_by_title(self, populated_repository: InMemoryBookRepository) -> None:
        """Test searching books by title."""
        # Get sample data
        all_books = await populated_repository.get_books(BookFilters(limit=100))
        if all_books.items:
            sample_title = all_books.items[0].title
            search_term = sample_title.split()[0]  # First word of title
            
            filters = BookFilters(search=search_term)
            result = await populated_repository.get_books(filters)
            
            for book in result.items:
                assert search_term.lower() in book.title.lower()

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, populated_repository: InMemoryBookRepository) -> None:
        """Test that title search is case-insensitive."""
        # Get sample data
        all_books = await populated_repository.get_books(BookFilters(limit=100))
        if all_books.items:
            sample_title = all_books.items[0].title
            search_term = sample_title.split()[0].upper()  # First word in uppercase
            
            filters = BookFilters(search=search_term)
            result = await populated_repository.get_books(filters)
            
            for book in result.items:
                assert search_term.lower() in book.title.lower()

    @pytest.mark.asyncio
    async def test_combined_filters(
        self,
        clean_repository: InMemoryBookRepository,
        test_data_factory: TestDataFactory
    ) -> None:
        """Test combining multiple filters."""
        # Add specific test data
        books = [
            test_data_factory.create_book_response(1, "Python Programming", "John Doe", 2020, ["python"]),
            test_data_factory.create_book_response(2, "Java Programming", "John Doe", 2020, ["java"]),
            test_data_factory.create_book_response(3, "Python Advanced", "Jane Smith", 2020, ["python"]),
        ]
        await clean_repository.load_initial_books(books)

        # Filter by author AND search term
        filters = BookFilters(author="John Doe", search="Python")
        result = await clean_repository.get_books(filters)

        assert result.total == 1
        assert result.items[0].title == "Python Programming"
        assert result.items[0].author == "John Doe"


class TestBookSorting:
    """Test class for book sorting operations."""

    @pytest.mark.asyncio
    async def test_sort_by_year_ascending(self, populated_repository: InMemoryBookRepository) -> None:
        """Test sorting books by year in ascending order."""
        filters = BookFilters(sort_by="year", sort_order="asc", limit=100)
        result = await populated_repository.get_books(filters)
        
        if len(result.items) > 1:
            DataComparisonHelpers.assert_books_sorted(result.items, "year", ascending=True)

    @pytest.mark.asyncio
    async def test_sort_by_year_descending(self, populated_repository: InMemoryBookRepository) -> None:
        """Test sorting books by year in descending order."""
        filters = BookFilters(sort_by="year", sort_order="desc", limit=100)
        result = await populated_repository.get_books(filters)
        
        if len(result.items) > 1:
            DataComparisonHelpers.assert_books_sorted(result.items, "year", ascending=False)

    @pytest.mark.asyncio
    async def test_sort_by_author_ascending(self, populated_repository: InMemoryBookRepository) -> None:
        """Test sorting books by author in ascending order."""
        filters = BookFilters(sort_by="author", sort_order="asc", limit=100)
        result = await populated_repository.get_books(filters)
        
        if len(result.items) > 1:
            DataComparisonHelpers.assert_books_sorted(result.items, "author", ascending=True)

    @pytest.mark.asyncio
    async def test_sort_by_author_descending(self, populated_repository: InMemoryBookRepository) -> None:
        """Test sorting books by author in descending order."""
        filters = BookFilters(sort_by="author", sort_order="desc", limit=100)
        result = await populated_repository.get_books(filters)
        
        if len(result.items) > 1:
            DataComparisonHelpers.assert_books_sorted(result.items, "author", ascending=False)

    @pytest.mark.asyncio
    async def test_sort_with_filters(
        self,
        clean_repository: InMemoryBookRepository,
        test_data_factory: TestDataFactory
    ) -> None:
        """Test sorting combined with filtering."""
        # Add books with same author but different years
        books = test_data_factory.create_books_by_author("Test Author", 3)
        await clean_repository.load_initial_books(books)

        # Filter by author and sort by year
        filters = BookFilters(
            author="Test Author",
            sort_by="year",
            sort_order="asc"
        )
        result = await clean_repository.get_books(filters)

        assert result.total == 3
        DataComparisonHelpers.assert_books_sorted(result.items, "year", ascending=True)

        # Verify all books match filter
        for book in result.items:
            assert "Test Author" in book.author


class TestPagination:
    """Test class for pagination functionality."""

    @pytest.mark.asyncio
    async def test_first_page_pagination(self, populated_repository: InMemoryBookRepository) -> None:
        """Test getting the first page of results."""
        filters = BookFilters(page=1, limit=5)
        result = await populated_repository.get_books(filters)
        
        assert result.page == 1
        assert result.limit == 5
        assert len(result.items) <= 5

    @pytest.mark.asyncio
    async def test_middle_page_pagination(self, populated_repository: InMemoryBookRepository) -> None:
        """Test getting a middle page of results."""
        filters = BookFilters(page=2, limit=3)
        result = await populated_repository.get_books(filters)
        
        assert result.page == 2
        assert result.limit == 3

    @pytest.mark.asyncio
    async def test_last_page_pagination(self, populated_repository: InMemoryBookRepository) -> None:
        """Test getting the last page of results."""
        # First, get total count
        all_filters = BookFilters(limit=100)
        all_result = await populated_repository.get_books(all_filters)
        total = all_result.total
        
        # Calculate last page
        page_size = 3
        last_page = (total + page_size - 1) // page_size
        
        filters = BookFilters(page=last_page, limit=page_size)
        result = await populated_repository.get_books(filters)
        
        assert result.page == last_page
        assert result.total == total

    @pytest.mark.asyncio
    async def test_single_page_all_items(self, populated_repository: InMemoryBookRepository) -> None:
        """Test getting all items in a single page."""
        filters = BookFilters(page=1, limit=100)
        result = await populated_repository.get_books(filters)
        
        assert result.page == 1
        assert result.limit == 100
        assert len(result.items) == result.total

    @pytest.mark.asyncio
    async def test_pagination_beyond_available_pages(self, populated_repository: InMemoryBookRepository) -> None:
        """Test requesting a page beyond available data."""
        filters = BookFilters(page=999, limit=10)
        result = await populated_repository.get_books(filters)
        
        assert result.page == 999
        assert len(result.items) == 0
        assert result.total > 0  # Total should still reflect actual count


class TestStatistics:
    """Test class for statistics functionality."""

    @pytest.mark.asyncio
    async def test_stats_with_data(self, populated_repository: InMemoryBookRepository) -> None:
        """Test getting statistics with data in repository."""
        stats = await populated_repository.get_stats()
        
        assert isinstance(stats, StatsResponse)
        assert stats.total_books > 0
        assert stats.unique_authors > 0
        # Don't hardcode expected values - just verify they're reasonable
        assert stats.unique_authors <= stats.total_books

    @pytest.mark.asyncio
    async def test_stats_empty_repository(
        self,
        clean_repository: InMemoryBookRepository
    ) -> None:
        """Test getting statistics from empty repository."""
        stats = await clean_repository.get_stats()

        assert stats.total_books == 0
        assert stats.unique_authors == 0

    @pytest.mark.asyncio
    async def test_stats_after_operations(
        self,
        clean_repository: InMemoryBookRepository,
        test_data_factory: TestDataFactory
    ) -> None:
        """Test statistics after various operations."""
        # Start empty
        stats = await clean_repository.get_stats()
        assert stats.total_books == 0
        assert stats.unique_authors == 0

        # Add books
        book1 = test_data_factory.create_book_create("Book 1", "Author 1", 2023)
        book2 = test_data_factory.create_book_create("Book 2", "Author 1", 2024)  # Same author
        book3 = test_data_factory.create_book_create("Book 3", "Author 2", 2023)  # Different author

        await clean_repository.create_book(book1)
        await clean_repository.create_book(book2)
        await clean_repository.create_book(book3)

        stats = await clean_repository.get_stats()
        assert stats.total_books == 3
        assert stats.unique_authors == 2  # Author 1 and Author 2

        # Delete a book
        await clean_repository.delete_book(1)

        stats = await clean_repository.get_stats()
        assert stats.total_books == 2
        assert stats.unique_authors == 2  # Still 2 unique authors


class TestInitialDataLoading:
    """Test class for initial data loading functionality."""

    @pytest.mark.asyncio
    async def test_load_initial_books(
        self,
        clean_repository: InMemoryBookRepository,
        test_data_factory: TestDataFactory
    ) -> None:
        """Test loading initial books."""
        initial_books = [
            test_data_factory.create_book_response(1, "Book 1", "Author 1", 2023),
            test_data_factory.create_book_response(2, "Book 2", "Author 2", 2024)
        ]

        await clean_repository.load_initial_books(initial_books)

        # Verify books are loaded
        book1 = await clean_repository.get_book(1)
        book2 = await clean_repository.get_book(2)

        assert book1 is not None
        assert book2 is not None
        assert book1.title == "Book 1"
        assert book2.title == "Book 2"

    @pytest.mark.asyncio
    async def test_load_empty_initial_books(
        self,
        clean_repository: InMemoryBookRepository
    ) -> None:
        """Test loading empty list of initial books."""
        await clean_repository.load_initial_books([])

        stats = await clean_repository.get_stats()
        assert stats.total_books == 0

    @pytest.mark.asyncio
    async def test_next_id_after_initial_load(
        self,
        clean_repository: InMemoryBookRepository,
        test_data_factory: TestDataFactory
    ) -> None:
        """Test that next ID is set correctly after initial load."""
        # Load books with non-sequential IDs
        initial_books = [
            test_data_factory.create_book_response(5, "Book 5", "Author 5", 2023),
            test_data_factory.create_book_response(3, "Book 3", "Author 3", 2024),
            test_data_factory.create_book_response(10, "Book 10", "Author 10", 2025)
        ]

        await clean_repository.load_initial_books(initial_books)

        # Create new book - should get ID 11 (max existing + 1)
        new_book_data = test_data_factory.create_book_create("New Book", "New Author", 2025)
        created_book = await clean_repository.create_book(new_book_data)

        assert created_book.id == 11 