"""Data loading utilities for initial book data"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Iterator

from app.models import BookResponse, BookCreateFromJSON, BookCreate

logger = logging.getLogger(__name__)


class DataLoader:
    
    def __init__(self, json_file_path: str = "data/books.json"):
        self.json_file_path = Path(json_file_path)
    
    def load_initial_books(self) -> List[BookResponse]:
        """
        Load and validate books from JSON file.
        
        Returns:
            List of validated BookResponse objects with generated IDs
            
        Raises:
            FileNotFoundError: If the JSON file doesn't exist
            json.JSONDecodeError: If the JSON is malformed
            ValueError: If the JSON structure is invalid
        """
        raw_data = self._load_json_file()
        validated_books = list(self._validate_and_transform_books(raw_data))
        books_with_ids = self._assign_ids(validated_books)
        
        logger.info(f"Successfully loaded {len(books_with_ids)} books from {self.json_file_path}")
        return books_with_ids
    
    def _load_json_file(self) -> List[Dict[str, Any]]:
        """Load and parse JSON file"""
        if not self.json_file_path.exists():
            logger.warning(f"JSON file not found: {self.json_file_path}")
            return []
        
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not isinstance(data, list):
                raise ValueError("JSON file should contain a list of books")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {self.json_file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reading {self.json_file_path}: {e}")
            raise
    
    def _validate_and_transform_books(self, raw_data: List[Dict[str, Any]]) -> Iterator[BookCreate]:
        """Validate raw data and transform to BookCreate objects"""
        for idx, book_data in enumerate(raw_data, 1):
            try:
                # Use DTO for validation and transformation
                json_book = BookCreateFromJSON(**book_data)
                book_create = json_book.to_book_create()
                yield book_create
                
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid book at index {idx}: {e}")
                continue
    
    def _assign_ids(self, books: List[BookCreate]) -> List[BookResponse]:
        """Assign sequential IDs to validated books"""
        return [
            BookResponse(id=idx, **book.model_dump())
            for idx, book in enumerate(books, 1)
        ] 