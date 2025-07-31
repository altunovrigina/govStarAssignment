"""Application dependencies using dependency injection pattern"""

from fastapi import HTTPException, Request, status
from app.repositories import BookRepository


def get_book_repository(request: Request) -> BookRepository:
    """
    Dependency to get the book repository instance from app state.
    
    This follows the dependency injection pattern, making the code:
    - More testable (easy to mock)
    - Loosely coupled (depends on abstraction)
    - Following SOLID principles
    
    Args:
        request: FastAPI request object containing app state
        
    Returns:
        BookRepository: The repository instance
        
    Raises:
        HTTPException: If repository is not initialized
    """
    if not hasattr(request.app.state, 'book_repository'):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Book repository not initialized"
        )
    
    return request.app.state.book_repository 