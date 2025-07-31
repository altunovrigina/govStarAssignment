"""Book API routes with clean architecture and async operations"""

from typing import Annotated, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import JSONResponse

from app.models import (
    BookCreate, BookResponse, BookFilters, 
    PaginatedResponse, StatsResponse, ErrorResponse
)
from app.repositories import BookRepository
from app.dependencies import get_book_repository
from app.utils import handle_repository_errors

# Create router with clean configuration
router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    description="Create a new book with title, author, year, and optional tags"
)
@handle_repository_errors
async def create_book(
    book_data: BookCreate,
    repository: Annotated[BookRepository, Depends(get_book_repository)]
) -> BookResponse:
    """Create a new book with automatic ID generation"""
    book = await repository.create_book(book_data)
    return book


@router.get(
    "/",
    response_model=PaginatedResponse[BookResponse],
    summary="Get books with filtering and pagination",
    description="Retrieve books with optional filtering by author, year, or title search, plus pagination and sorting"
)
@handle_repository_errors
async def get_books(
    filters: Annotated[BookFilters, Depends()],
    repository: Annotated[BookRepository, Depends(get_book_repository)]
) -> PaginatedResponse[BookResponse]:
    """Get books with filtering, sorting, and pagination using async operations"""
    result = await repository.get_books(filters)
    return result


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get a book by ID",
    description="Retrieve a single book by its unique ID"
)
async def get_book(
    book_id: int,
    repository: Annotated[BookRepository, Depends(get_book_repository)]
) -> BookResponse:
    """Get a book by ID with proper error handling"""
    book = await repository.get_book(book_id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
        
    return book


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a book",
    description="Delete a book by its unique ID"
)
async def delete_book(
    book_id: int,
    repository: Annotated[BookRepository, Depends(get_book_repository)]
) -> dict:
    """Delete a book by ID with async operations"""
    success = await repository.delete_book(book_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
        
    return {"message": f"Book with ID {book_id} has been deleted successfully"}


@router.get(
    "/stats/summary",
    response_model=StatsResponse,
    summary="Get book collection statistics",
    description="Get statistics about the book collection including total books and unique authors"
)
@handle_repository_errors
async def get_stats(
    repository: Annotated[BookRepository, Depends(get_book_repository)]
) -> StatsResponse:
    """Get statistics about the book collection using async operations"""
    stats = await repository.get_stats()
    return stats 