"""
Unit tests for utility functions and decorators.

This module tests utility functions, error handling decorators, and other
helper functionality used throughout the application.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import logging

from app.utils.common_utils import (
    normalize_string,
    safe_int_conversion,
    handle_repository_errors,
    log_and_raise_http_error
)


class TestNormalizeString:
    """Test class for normalize_string function."""

    @pytest.mark.parametrize("input_str,expected", [
        ("Hello World", "hello world"),
        ("  Hello World  ", "hello world"),
        ("UPPERCASE", "uppercase"),
        ("MiXeD cAsE", "mixed case"),
        ("", ""),
        ("   ", ""),
        ("123", "123"),
        ("Special!@#$%Characters", "special!@#$%characters"),
    ])
    def test_normalize_string_cases(self, input_str: str, expected: str) -> None:
        """Test normalize_string with various input cases."""
        result = normalize_string(input_str)
        assert result == expected

    def test_normalize_string_none_input(self) -> None:
        """Test normalize_string with None input."""
        result = normalize_string(None)
        assert result == ""


class TestSafeIntConversion:
    """Test class for safe_int_conversion function."""

    @pytest.mark.parametrize("input_value,expected", [
        ("123", 123),
        ("0", 0),
        ("-456", -456),
        ("", None),
        (None, None),
        ("not_a_number", None),
        ("123.45", None),
        ("  123  ", 123),
    ])
    def test_safe_int_conversion_cases(self, input_value, expected) -> None:
        """Test safe_int_conversion with various inputs."""
        result = safe_int_conversion(input_value)
        assert result == expected


class TestHandleRepositoryErrors:
    """Test class for handle_repository_errors decorator."""

    @pytest.mark.asyncio
    async def test_successful_operation(self) -> None:
        """Test decorator with successful operation."""
        @handle_repository_errors
        async def successful_operation():
            return "success"

        result = await successful_operation()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_value_error_handling(self) -> None:
        """Test decorator handling ValueError."""
        @handle_repository_errors
        async def operation_with_value_error():
            raise ValueError("Invalid value")

        with pytest.raises(HTTPException) as exc_info:
            await operation_with_value_error()
        
        assert exc_info.value.status_code == 400
        assert "Invalid value" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_file_not_found_error_handling(self) -> None:
        """Test decorator handling FileNotFoundError."""
        @handle_repository_errors
        async def operation_with_file_error():
            raise FileNotFoundError("File not found")

        with pytest.raises(HTTPException) as exc_info:
            await operation_with_file_error()
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_generic_exception_handling(self) -> None:
        """Test decorator handling generic exceptions."""
        @handle_repository_errors
        async def operation_with_generic_error():
            raise RuntimeError("Something went wrong")

        with pytest.raises(HTTPException) as exc_info:
            await operation_with_generic_error()
        
        assert exc_info.value.status_code == 500
        assert "unexpected error occurred" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_logging_behavior(self) -> None:
        """Test that decorator logs errors appropriately."""
        @handle_repository_errors
        async def operation_with_error():
            raise ValueError("Test error for logging")

        with patch('app.utils.common_utils.logger') as mock_logger:
            with pytest.raises(HTTPException):
                await operation_with_error()
            
            # Verify error was logged
            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args[0][0]
            assert "Test error for logging" in call_args

    def test_decorator_preserves_function_metadata(self) -> None:
        """Test that decorator preserves original function metadata."""
        @handle_repository_errors
        async def original_function():
            """Original docstring."""
            pass

        assert original_function.__name__ == "original_function"
        assert "Original docstring." in original_function.__doc__


class TestLogAndRaiseHttpError:
    """Test class for log_and_raise_http_error function."""

    def test_basic_error_logging_and_raising(self) -> None:
        """Test basic error logging and HTTPException raising."""
        test_error = ValueError("Test error")
        
        with patch('app.utils.common_utils.logger') as mock_logger:
            with pytest.raises(HTTPException) as exc_info:
                log_and_raise_http_error(test_error, "test_operation")
            
            # Verify logging
            mock_logger.error.assert_called_once()
            log_message = mock_logger.error.call_args[0][0]
            assert "test_operation" in log_message
            assert "Test error" in log_message
            
            # Verify HTTPException
            assert exc_info.value.status_code == 500
            assert "server error" in str(exc_info.value.detail).lower()

    def test_custom_status_code_and_message(self) -> None:
        """Test with custom status code and user message."""
        test_error = ValueError("Internal error")
        
        with patch('app.utils.common_utils.logger'):
            with pytest.raises(HTTPException) as exc_info:
                log_and_raise_http_error(
                    test_error, 
                    "custom_operation", 
                    status_code=400, 
                    user_message="Custom user message"
                )
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "Custom user message" 