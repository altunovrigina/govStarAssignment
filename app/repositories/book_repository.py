"""Book repository interfaces and implementations"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

from app.models import BookCreate, BookResponse, BookFilters, PaginatedResponse, StatsResponse
from app.utils.common_utils import normalize_string
from app.services import PaginationService


class BookRepository(ABC):
    """Abstract repository interface for book operations"""
    
    @abstractmethod
    async def create_book(self, book_data: BookCreate) -> BookResponse:
        """Create a new book"""
        pass
    
    @abstractmethod
    async def get_book(self, book_id: int) -> Optional[BookResponse]:
        """Get a book by ID"""
        pass
    
    @abstractmethod
    async def delete_book(self, book_id: int) -> bool:
        """Delete a book by ID, returns True if deleted, False if not found"""
        pass
    
    @abstractmethod
    async def get_books(self, filters: BookFilters) -> PaginatedResponse[BookResponse]:
        """Get books with filtering, sorting, and pagination"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> StatsResponse:
        """Get collection statistics"""
        pass
    
    @abstractmethod
    async def load_initial_books(self, books: List[BookResponse]) -> None:
        """Load initial books into the repository"""
        pass


class InMemoryBookRepository(BookRepository):
    """In-memory implementation of book repository with async operations"""
    
    def __init__(self):
        self._books: Dict[int, BookResponse] = {}
        self._next_id: int = 1
        # No locks needed - FastAPI async is single-threaded by default
        
    async def load_initial_books(self, books: List[BookResponse]) -> None:
        """Load initial books into the repository"""
        for book in books:
            self._books[book.id] = book
            self._next_id = max(self._next_id, book.id + 1)
                
    async def create_book(self, book_data: BookCreate) -> BookResponse:
        """Create a new book with auto-generated ID"""
        book_id = self._next_id
        self._next_id += 1
        
        book = BookResponse(
            id=book_id,
            title=book_data.title,
            author=book_data.author,
            year=book_data.year,
            tags=book_data.tags or []
        )
        
        self._books[book_id] = book
        return book
            
    async def get_book(self, book_id: int) -> Optional[BookResponse]:
        """Get a book by ID"""
        return self._books.get(book_id)
        
    async def delete_book(self, book_id: int) -> bool:
        """Delete a book by ID"""
        if book_id in self._books:
            del self._books[book_id]
            return True
        return False
        
    async def get_books(self, filters: BookFilters) -> PaginatedResponse[BookResponse]:
        """Get books with filtering, sorting, and pagination"""
        # Start with all books
        books = list(self._books.values())
        
        # Apply filters
        if filters.author:
            author_normalized = normalize_string(filters.author)
            books = [
                book for book in books 
                if author_normalized in normalize_string(book.author)
            ]
            
        if filters.year:
            books = [book for book in books if book.year == filters.year]
            
        if filters.search:
            search_normalized = normalize_string(filters.search)
            books = [
                book for book in books 
                if search_normalized in normalize_string(book.title)
            ]
        
        # Apply sorting
        if filters.sort_by:
            reverse = filters.sort_order == "desc"
            if filters.sort_by == "year":
                books.sort(key=lambda x: x.year, reverse=reverse)
            elif filters.sort_by == "author":
                books.sort(key=lambda x: normalize_string(x.author), reverse=reverse)
        
        # Use centralized pagination service
        return PaginationService.paginate(books, filters.page, filters.limit)
        
    async def get_stats(self) -> StatsResponse:
        """Get collection statistics"""
        total_books = len(self._books)
        unique_authors = len(set(book.author for book in self._books.values()))
        
        return StatsResponse(
            total_books=total_books,
            unique_authors=unique_authors
        ) 