from datetime import datetime
from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict, field_validator

T = TypeVar('T')


class BookCreateFromJSON(BaseModel):
    """Model for loading books from JSON files with field mapping"""
    title: str = Field(..., min_length=1, max_length=500, description="The title of the book")
    author: str = Field(..., min_length=1, max_length=200, description="The author of the book")
    release_year: int = Field(..., ge=1400, le=datetime.now().year, description="The publication year")
    tags: Optional[List[str]] = Field(None, description="Optional list of tags")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )

    def to_book_create(self) -> 'BookCreate':
        """Convert to BookCreate model with proper field mapping"""
        return BookCreate(
            title=self.title,
            author=self.author,
            year=self.release_year,  # Map release_year to year
            tags=self.tags
        )


class BookCreate(BaseModel):
    """Model for creating a new book"""
    title: str = Field(..., min_length=1, max_length=500, description="The title of the book")
    author: str = Field(..., min_length=1, max_length=200, description="The author of the book")
    year: int = Field(..., ge=1400, le=datetime.now().year, description="The publication year")
    tags: Optional[List[str]] = Field(None, description="Optional list of tags")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )


class BookResponse(BookCreate):
    """Model for book responses including the generated ID"""
    id: int = Field(..., description="Unique book identifier")

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )


class BookFilters(BaseModel):
    """Model for book filtering and pagination parameters"""
    author: Optional[str] = Field(None, description="Filter by author name (case-insensitive)")
    year: Optional[int] = Field(None, description="Filter by publication year")
    search: Optional[str] = Field(None, description="Search in book title (case-insensitive)")
    sort_by: Optional[str] = Field(None, pattern="^(year|author)$", description="Sort by field")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Sort order")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Items per page")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic model for paginated responses"""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, description="Items per page")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )


class StatsResponse(BaseModel):
    """Model for statistics response"""
    total_books: int = Field(..., ge=0, description="Total number of books")
    unique_authors: int = Field(..., ge=0, description="Number of unique authors")

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )


class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    ) 