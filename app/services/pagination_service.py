"""Centralized pagination service for consistent pagination across the application"""

from typing import List, TypeVar

from app.models import PaginatedResponse

T = TypeVar('T')


class PaginationService:
    """Service for handling pagination logic consistently across the application"""
    
    @staticmethod
    def paginate(items: List[T], page: int, limit: int) -> PaginatedResponse[T]:
        """
        Apply pagination to a list of items.
        
        Args:
            items: Pre-filtered and sorted list of items to paginate
            page: Page number (1-based indexing)
            limit: Number of items per page
            
        Returns:
            PaginatedResponse containing paginated items and metadata
        """
        total = len(items)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        return PaginatedResponse(
            items=items[start_idx:end_idx],
            total=total,
            page=page,
            limit=limit,
            has_next=(page * limit) < total,
            has_prev=page > 1
        ) 