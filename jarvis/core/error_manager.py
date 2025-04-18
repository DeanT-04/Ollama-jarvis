#!/usr/bin/env python3
"""
Error Manager module for Jarvis.

This module provides a system for handling errors, classifying them,
and applying appropriate recovery strategies.
"""

import re
import time
import traceback
from typing import Dict, List, Any, Optional, Callable, Tuple

from jarvis.config import get_config


class ErrorManager:
    """Error manager for handling and recovering from errors."""
    
    def __init__(self):
        """Initialize the error manager."""
        self.error_history: List[Dict[str, Any]] = []
        self.recovery_strategies: Dict[str, Callable] = {
            "ImportError": self._handle_import_error,
            "ModuleNotFoundError": self._handle_import_error,
            "SyntaxError": self._handle_syntax_error,
            "NameError": self._handle_name_error,
            "TypeError": self._handle_type_error,
            "IndexError": self._handle_index_error,
            "KeyError": self._handle_key_error,
            "FileNotFoundError": self._handle_file_not_found_error,
            "PermissionError": self._handle_permission_error,
            "TimeoutError": self._handle_timeout_error,
            "ValueError": self._handle_value_error,
            "ZeroDivisionError": self._handle_zero_division_error,
        }
        
        # Error patterns for more specific error classification
        self.error_patterns = {
            "undefined_variable": (
                r"name '(\w+)' is not defined",
                self._handle_undefined_variable
            ),
            "missing_package": (
                r"No module named '([^']+)'",
                self._handle_missing_package
            ),
            "invalid_syntax": (
                r"invalid syntax",
                self._handle_invalid_syntax
            ),
            "missing_closing_parenthesis": (
                r"unexpected EOF while parsing",
                self._handle_missing_closing_parenthesis
            ),
            "missing_closing_bracket": (
                r"unexpected EOF while parsing",
                self._handle_missing_closing_bracket
            ),
            "missing_closing_brace": (
                r"unexpected EOF while parsing",
                self._handle_missing_closing_brace
            ),
            "indentation_error": (
                r"indentation",
                self._handle_indentation_error
            ),
            "file_not_found": (
                r"No such file or directory: '([^']+)'",
                self._handle_specific_file_not_found
            ),
            "permission_denied": (
                r"Permission denied",
                self._handle_specific_permission_denied
            ),
            "index_out_of_range": (
                r"list index out of range",
                self._handle_index_out_of_range
            ),
            "key_not_found": (
                r"KeyError: '([^']+)'",
                self._handle_key_not_found
            ),
            "division_by_zero": (
                r"division by zero",
                self._handle_specific_division_by_zero
            ),
            "type_mismatch": (
                r"unsupported operand type\(s\) for (.+): '(.+)' and '(.+)'",
                self._handle_type_mismatch
            ),
            "attribute_error": (
                r"'(.+)' object has no attribute '(.+)'",
                self._handle_attribute_error
            ),
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an error and apply a recovery strategy.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                Should include at least 'code' and 'language'.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        # Get the error details
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # Log the error
        error_entry = {
            "error_type": error_type,
            "error_message": error_message,
            "error_traceback": error_traceback,
            "context": context,
            "timestamp": time.time()
        }
        self.error_history.append(error_entry)
        
        # Check for specific error patterns
        for pattern_name, (pattern, handler) in self.error_patterns.items():
            match = re.search(pattern, error_message)
            if match:
                return handler(error, context, match)
        
        # If no specific pattern matches, use the general handler for the error type
        if error_type in self.recovery_strategies:
            return self.recovery_strategies[error_type](error, context)
        
        # If no handler is found, use the default recovery strategy
        return self._default_recovery(error, context)
    
    def get_error_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the error history.
        
        Args:
            limit: The maximum number of errors to return.
                If None, all errors are returned.
                
        Returns:
            A list of error entries.
        """
        if limit is None:
            return self.error_history
        return self.error_history[-limit:]
    
    def clear_error_history(self) -> None:
        """Clear the error history."""
        self.error_history = []
    
    def _default_recovery(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Default recovery strategy.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "default",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"An error occurred: {str(error)}. Please check your code and try again.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_import_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an import error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        error_message = str(error)
        module_name = error_message.split("'")[1] if "'" in error_message else "unknown"
        
        return {
            "strategy": "import_error",
            "error_type": type(error).__name__,
            "error_message": error_message,
            "suggestion": f"The module '{module_name}' could not be imported. "
                         f"You may need to install it using pip: pip install {module_name}",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_syntax_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a syntax error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        code = context.get("code", "")
        lines = code.split("\n")
        
        # Try to get the line number from the error
        line_number = getattr(error, "lineno", None)
        if line_number is not None and 0 <= line_number - 1 < len(lines):
            line = lines[line_number - 1]
            column = getattr(error, "offset", None)
            if column is not None:
                pointer = " " * (column - 1) + "^"
                error_location = f"Line {line_number}: {line}\n{pointer}"
            else:
                error_location = f"Line {line_number}: {line}"
        else:
            error_location = "Unknown location"
        
        return {
            "strategy": "syntax_error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"There is a syntax error in your code:\n{error_location}\n"
                         f"Please check for missing parentheses, brackets, or other syntax issues.",
            "updated_code": code,
            "fixed": False
        }
    
    def _handle_name_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a name error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        error_message = str(error)
        variable_name = error_message.split("'")[1] if "'" in error_message else "unknown"
        
        return {
            "strategy": "name_error",
            "error_type": type(error).__name__,
            "error_message": error_message,
            "suggestion": f"The variable '{variable_name}' is not defined. "
                         f"Make sure you have defined it before using it.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_type_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a type error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "type_error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"There is a type error in your code: {str(error)}. "
                         f"Make sure you are using the correct types for your operations.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_index_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an index error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "index_error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": "You are trying to access an index that is out of range. "
                         "Make sure your indices are within the valid range for your data structure.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_key_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a key error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        error_message = str(error)
        key = error_message.strip("'")
        
        return {
            "strategy": "key_error",
            "error_type": type(error).__name__,
            "error_message": error_message,
            "suggestion": f"The key '{key}' does not exist in the dictionary. "
                         f"Make sure the key exists before trying to access it.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_file_not_found_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a file not found error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        error_message = str(error)
        file_path = error_message.split("'")[1] if "'" in error_message else "unknown"
        
        return {
            "strategy": "file_not_found_error",
            "error_type": type(error).__name__,
            "error_message": error_message,
            "suggestion": f"The file '{file_path}' could not be found. "
                         f"Make sure the file exists and the path is correct.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_permission_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a permission error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "permission_error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": "You do not have permission to access the file or directory. "
                         "Make sure you have the necessary permissions.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_timeout_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a timeout error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "timeout_error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": "The operation timed out. "
                         "This could be due to an infinite loop or a long-running operation. "
                         "Try optimizing your code or adding a timeout mechanism.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_value_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a value error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "value_error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"There is a value error in your code: {str(error)}. "
                         f"Make sure you are using valid values for your operations.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_zero_division_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a zero division error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "zero_division_error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": "You are trying to divide by zero. "
                         "Make sure your divisor is not zero before performing division.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    # Specific error pattern handlers
    
    def _handle_undefined_variable(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle an undefined variable error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        variable_name = match.group(1)
        code = context.get("code", "")
        
        return {
            "strategy": "undefined_variable",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"The variable '{variable_name}' is not defined. "
                         f"Make sure you have defined it before using it.",
            "updated_code": code,
            "fixed": False
        }
    
    def _handle_missing_package(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle a missing package error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        package_name = match.group(1)
        code = context.get("code", "")
        
        return {
            "strategy": "missing_package",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"The package '{package_name}' is not installed. "
                         f"You can install it using pip: pip install {package_name}",
            "updated_code": code,
            "fixed": False
        }
    
    def _handle_invalid_syntax(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle an invalid syntax error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        code = context.get("code", "")
        lines = code.split("\n")
        
        # Try to get the line number from the error
        line_number = getattr(error, "lineno", None)
        if line_number is not None and 0 <= line_number - 1 < len(lines):
            line = lines[line_number - 1]
            column = getattr(error, "offset", None)
            if column is not None:
                pointer = " " * (column - 1) + "^"
                error_location = f"Line {line_number}: {line}\n{pointer}"
            else:
                error_location = f"Line {line_number}: {line}"
        else:
            error_location = "Unknown location"
        
        return {
            "strategy": "invalid_syntax",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"There is a syntax error in your code:\n{error_location}\n"
                         f"Please check for missing parentheses, brackets, or other syntax issues.",
            "updated_code": code,
            "fixed": False
        }
    
    def _handle_missing_closing_parenthesis(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle a missing closing parenthesis error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        code = context.get("code", "")
        
        # Count opening and closing parentheses
        opening_count = code.count("(")
        closing_count = code.count(")")
        
        if opening_count > closing_count:
            # There are more opening parentheses than closing ones
            suggestion = f"You have {opening_count} opening parentheses '(' but only {closing_count} closing parentheses ')'. "
            suggestion += f"Add {opening_count - closing_count} more closing parentheses ')'."
        else:
            suggestion = "Check your code for missing closing parentheses ')'."
        
        return {
            "strategy": "missing_closing_parenthesis",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": suggestion,
            "updated_code": code,
            "fixed": False
        }
    
    def _handle_missing_closing_bracket(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle a missing closing bracket error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        code = context.get("code", "")
        
        # Count opening and closing brackets
        opening_count = code.count("[")
        closing_count = code.count("]")
        
        if opening_count > closing_count:
            # There are more opening brackets than closing ones
            suggestion = f"You have {opening_count} opening brackets '[' but only {closing_count} closing brackets ']'. "
            suggestion += f"Add {opening_count - closing_count} more closing brackets ']'."
        else:
            suggestion = "Check your code for missing closing brackets ']'."
        
        return {
            "strategy": "missing_closing_bracket",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": suggestion,
            "updated_code": code,
            "fixed": False
        }
    
    def _handle_missing_closing_brace(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle a missing closing brace error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        code = context.get("code", "")
        
        # Count opening and closing braces
        opening_count = code.count("{")
        closing_count = code.count("}")
        
        if opening_count > closing_count:
            # There are more opening braces than closing ones
            suggestion = f"You have {opening_count} opening braces '{{' but only {closing_count} closing braces '}}'. "
            suggestion += f"Add {opening_count - closing_count} more closing braces '}}'."
        else:
            suggestion = "Check your code for missing closing braces '}'."
        
        return {
            "strategy": "missing_closing_brace",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": suggestion,
            "updated_code": code,
            "fixed": False
        }
    
    def _handle_indentation_error(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle an indentation error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "indentation_error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": "There is an indentation error in your code. "
                         "Make sure your indentation is consistent and uses either spaces or tabs, but not both.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_specific_file_not_found(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle a specific file not found error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        file_path = match.group(1)
        
        return {
            "strategy": "file_not_found",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"The file '{file_path}' could not be found. "
                         f"Make sure the file exists and the path is correct.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_specific_permission_denied(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle a specific permission denied error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "permission_denied",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": "You do not have permission to access the file or directory. "
                         "Make sure you have the necessary permissions.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_index_out_of_range(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle an index out of range error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "index_out_of_range",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": "You are trying to access an index that is out of range. "
                         "Make sure your indices are within the valid range for your data structure.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_key_not_found(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle a key not found error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        key = match.group(1)
        
        return {
            "strategy": "key_not_found",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"The key '{key}' does not exist in the dictionary. "
                         f"Make sure the key exists before trying to access it.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_specific_division_by_zero(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle a specific division by zero error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        return {
            "strategy": "division_by_zero",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": "You are trying to divide by zero. "
                         "Make sure your divisor is not zero before performing division.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_type_mismatch(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle a type mismatch error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        operation = match.group(1)
        type1 = match.group(2)
        type2 = match.group(3)
        
        return {
            "strategy": "type_mismatch",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"You are trying to perform the operation '{operation}' on incompatible types: '{type1}' and '{type2}'. "
                         f"Make sure the types are compatible or convert them to compatible types.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
    
    def _handle_attribute_error(self, error: Exception, context: Dict[str, Any], match: re.Match) -> Dict[str, Any]:
        """Handle an attribute error.
        
        Args:
            error: The error to handle.
            context: The context in which the error occurred.
            match: The regex match object.
                
        Returns:
            A dictionary containing the recovery strategy and updated code.
        """
        object_type = match.group(1)
        attribute = match.group(2)
        
        return {
            "strategy": "attribute_error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "suggestion": f"The object of type '{object_type}' does not have an attribute '{attribute}'. "
                         f"Make sure you are using the correct attribute name or check the documentation for available attributes.",
            "updated_code": context.get("code", ""),
            "fixed": False
        }
