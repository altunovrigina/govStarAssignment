"""Common utility functions for reusable logic"""

import logging
from functools import wraps
from typing import Optional, Callable, Any
from fastapi import HTTPException, status

# Logger instance for this module that can be patched in tests
logger = logging.getLogger(__name__)


def normalize_string(value: str) -> str:
    """
    Normalize a string by stripping whitespace and converting to lowercase.
    
    Args:
        value: String to normalize
        
    Returns:
        Normalized string
    """
    return value.strip().lower() if value else ""


def safe_int_conversion(value: str) -> Optional[int]:
    """
    Safely convert a string to integer.
    
    Args:
        value: String to convert
        
    Returns:
        Integer value or None if conversion fails
    """
    try:
        return int(value) if value else None
    except (ValueError, TypeError):
        return None


def handle_repository_errors(func: Callable) -> Callable:
    """
    Decorator to handle repository operation errors consistently.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        operation_name = func.__name__
        
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            # Handle validation or data-related errors
            logger.warning(f"Validation error in {operation_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data for {operation_name}: {str(e)}"
            )
        except FileNotFoundError as e:
            # Handle missing file errors
            logger.warning(f"File not found in {operation_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resource not found for {operation_name}"
            )
        except AttributeError as e:
            # Handle missing attributes (e.g., repository not initialized)
            logger.error(f"Service not properly initialized for {operation_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error occurred during {operation_name}"
            )
        except Exception as e:
            # Handle unexpected errors with full logging
            logger.error(f"Unexpected error in {operation_name}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during {operation_name}"
            )
    
    return wrapper


def log_and_raise_http_error(
    error: Exception,
    operation: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    user_message: Optional[str] = None
) -> None:
    """
    Log an error and raise an HTTPException with consistent formatting.
    
    Args:
        error: The original exception
        operation: Description of the operation that failed
        status_code: HTTP status code to return
        user_message: Optional custom message for users
    """
    logger.error(f"Error in {operation}: {str(error)}", exc_info=True)
    
    if user_message is None:
        user_message = f"An internal server error occurred during {operation}"
    
    raise HTTPException(
        status_code=status_code,
        detail=user_message
    ) 