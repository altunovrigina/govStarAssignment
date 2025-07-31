"""Main FastAPI application with clean architecture and dependency injection"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, Annotated

from fastapi import FastAPI, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models import ErrorResponse
from app.repositories import BookRepository, InMemoryBookRepository
from app.routers import books
from app.utils import log_and_raise_http_error
from app.utils.data_loader import DataLoader
from app.dependencies import get_book_repository

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup and shutdown events.
    
    Uses modern async patterns and dependency injection instead of global state.
    Repository is stored in app.state for clean architecture.
    """
    # Startup
    logger.info("Starting Book Catalog API...")
    
    # Initialize repository (dependency injection pattern)
    book_repository = InMemoryBookRepository()
    
    # Load initial books from JSON
    try:
        data_loader = DataLoader()
        initial_books = data_loader.load_initial_books()
        await book_repository.load_initial_books(initial_books)
        logger.info(f"Loaded {len(initial_books)} initial books")
    except FileNotFoundError:
        logger.warning("Initial books file not found - starting with empty catalog")
    except ValueError as e:
        logger.warning(f"Invalid data in initial books file: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error loading initial books: {e}")
        # Continue startup even if initial data loading fails
    
    # Store repository in app state (not global variable)
    app.state.book_repository = book_repository
    
    logger.info("Book Catalog API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Book Catalog API...")


# Create FastAPI app with lifespan and modern configuration
app = FastAPI(
    title="Book Catalog API",
    description="A robust API for managing a book catalog",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for production readiness
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(books.router)


# Global exception handler for consistent error responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for consistent error responses"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred"
        ).model_dump()
    )


@app.get(
    "/",
    summary="API Information",
    description="Get API information and welcome message",
    response_model=dict,
    tags=["info"]
)
async def root():
    """API information and welcome message"""
    return {
        "message": "Welcome to the Book Catalog API! ",
        "description": "A robust RESTful API for managing a book catalog",
        "features": [
            "Create, read, and delete books",
            "Advanced filtering and search",
            "Pagination and sorting",
            "Collection statistics",
            "Thread-safe operations",
            "Comprehensive validation"
        ],
        "documentation": {
            "interactive": "/docs",
            "redoc": "/redoc"
        },
        "version": "1.0.0"
    }


@app.get(
    "/health",
    summary="Health Check",
    description="Check API health and repository status",
    response_model=dict,
    tags=["monitoring"]
)
async def health_check(
    repository: Annotated[BookRepository, Depends(get_book_repository)]
):
    """Health check endpoint for monitoring"""
    try:
        # Test repository functionality
        stats = await repository.get_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "repository": "connected",
            "books_count": stats.total_books,
            "version": "1.0.0"
        }
    except AttributeError as e:
        # Repository not properly initialized
        log_and_raise_http_error(
            logger=logger,
            error=e,
            operation="health check",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            user_message="Repository not available"
        )
    except Exception as e:
        # Handle unexpected errors
        log_and_raise_http_error(
            logger=logger,
            error=e,
            operation="health check",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            user_message="Service unhealthy"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 