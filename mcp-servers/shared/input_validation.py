"""Input validation and sanitization for MCP servers."""

import ast
import html
import logging
import re
import urllib.parse
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Security patterns to detect malicious input
DANGEROUS_PATTERNS = [
    # Command injection patterns
    r"[;&|`$\(\)]",
    r"(rm|del|format|shutdown|reboot)\s+",
    r"(sudo|su)\s+",
    r"(chmod|chown)\s+",
    r">\s*/dev/",
    r"nc\s+.*-[el]",
    r"wget\s+.*\|",
    r"curl\s+.*\|",
    # SQL injection patterns
    r"(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+",
    r"(\b(or|and)\s+\w+\s*=\s*\w+)",
    r"(--|/\*|\*/)",
    r"(xp_|sp_)\w+",
    # Path traversal patterns
    r"\.\./",
    r"\.\.\\",
    r"/etc/",
    r"\\windows\\",
    r"~/",
    # Script injection patterns
    r"<script[^>]*>",
    r"javascript:",
    r"onload\s*=",
    r"onerror\s*=",
    r"eval\s*\(",
    # Python code injection patterns
    r"__import__\s*\(",
    r"exec\s*\(",
    r"eval\s*\(",
    r"compile\s*\(",
    r"globals\s*\(",
    r"locals\s*\(",
    r"vars\s*\(",
    r"dir\s*\(",
    r"getattr\s*\(",
    r"setattr\s*\(",
    r"hasattr\s*\(",
    r"delattr\s*\(",
]

# File extension whitelist for safe file operations
SAFE_FILE_EXTENSIONS = {".csv", ".json", ".txt", ".xlsx", ".parquet", ".feather"}

# Maximum input lengths
MAX_INPUT_LENGTHS = {
    "string": 10000,
    "sql_query": 5000,
    "file_path": 500,
    "dataset_name": 100,
    "column_name": 100,
    "python_code": 50000,
}


class InputValidationError(Exception):
    """Raised when input validation fails."""

    pass


class SecureInputValidator:
    """Secure input validation and sanitization."""

    def __init__(self):
        self.dangerous_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in DANGEROUS_PATTERNS
        ]

    def validate_string(
        self, value: str, max_length: int = MAX_INPUT_LENGTHS["string"]
    ) -> str:
        """Validate and sanitize string input."""
        if not isinstance(value, str):
            raise InputValidationError("Input must be a string")

        if len(value) > max_length:
            raise InputValidationError(
                f"String length exceeds maximum of {max_length} characters"
            )

        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern.search(value):
                logger.warning(
                    f"Dangerous pattern detected in input: {pattern.pattern}"
                )
                raise InputValidationError(
                    "Input contains potentially dangerous content"
                )

        # HTML encode to prevent XSS
        sanitized = html.escape(value)

        return sanitized

    def validate_sql_query(self, query: str) -> str:
        """Validate SQL query for safety."""
        if not isinstance(query, str):
            raise InputValidationError("SQL query must be a string")

        if len(query) > MAX_INPUT_LENGTHS["sql_query"]:
            raise InputValidationError(
                f"SQL query exceeds maximum length of {MAX_INPUT_LENGTHS['sql_query']}"
            )

        # Convert to lowercase for pattern matching
        query_lower = query.lower()

        # Check for dangerous SQL patterns
        dangerous_sql_patterns = [
            r"\b(drop|delete|truncate|alter|create|grant|revoke)\b",
            r"\b(xp_|sp_)\w+",
            r"\b(exec|execute)\b",
            r"(--|/\*|\*/)",
            r"\b(union\s+select|union\s+all)\b",
            r"\b(information_schema|sys\.)\w+",
            r"\b(pg_|mysql\.)\w+",
        ]

        for pattern in dangerous_sql_patterns:
            if re.search(pattern, query_lower):
                logger.warning(f"Dangerous SQL pattern detected: {pattern}")
                raise InputValidationError(
                    "SQL query contains potentially dangerous operations"
                )

        return query.strip()

    def validate_file_path(self, path: str) -> str:
        """Validate file path for safety."""
        if not isinstance(path, str):
            raise InputValidationError("File path must be a string")

        if len(path) > MAX_INPUT_LENGTHS["file_path"]:
            raise InputValidationError(
                f"File path exceeds maximum length of {MAX_INPUT_LENGTHS['file_path']}"
            )

        # Normalize path
        try:
            normalized_path = Path(path).resolve()
        except (OSError, RuntimeError) as e:
            raise InputValidationError(f"Invalid file path: {e}")

        # Check for path traversal attempts
        path_str = str(normalized_path)
        if (
            ".." in path
            or path_str.startswith("/etc/")
            or path_str.startswith("/root/")
        ):
            raise InputValidationError("Path traversal attempt detected")

        # Check file extension
        if normalized_path.suffix.lower() not in SAFE_FILE_EXTENSIONS:
            raise InputValidationError(
                f"File extension not allowed. Allowed: {SAFE_FILE_EXTENSIONS}"
            )

        return str(normalized_path)

    def validate_dataset_name(self, name: str) -> str:
        """Validate dataset name."""
        if not isinstance(name, str):
            raise InputValidationError("Dataset name must be a string")

        if len(name) > MAX_INPUT_LENGTHS["dataset_name"]:
            raise InputValidationError(
                f"Dataset name exceeds maximum length of {MAX_INPUT_LENGTHS['dataset_name']}"
            )

        # Only allow alphanumeric, underscores, and hyphens
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            raise InputValidationError(
                "Dataset name can only contain alphanumeric characters, underscores, and hyphens"
            )

        return name

    def validate_column_name(self, name: str) -> str:
        """Validate column name."""
        if not isinstance(name, str):
            raise InputValidationError("Column name must be a string")

        if len(name) > MAX_INPUT_LENGTHS["column_name"]:
            raise InputValidationError(
                f"Column name exceeds maximum length of {MAX_INPUT_LENGTHS['column_name']}"
            )

        # Only allow alphanumeric, underscores
        if not re.match(r"^[a-zA-Z0-9_]+$", name):
            raise InputValidationError(
                "Column name can only contain alphanumeric characters and underscores"
            )

        return name

    def validate_python_code(self, code: str) -> str:
        """Validate Python code for safety."""
        if not isinstance(code, str):
            raise InputValidationError("Python code must be a string")

        if len(code) > MAX_INPUT_LENGTHS["python_code"]:
            raise InputValidationError(
                f"Python code exceeds maximum length of {MAX_INPUT_LENGTHS['python_code']}"
            )

        # Parse the code to check for dangerous constructs
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise InputValidationError(f"Invalid Python syntax: {e}")

        # Check for dangerous AST nodes
        dangerous_nodes = self._check_ast_nodes(tree)
        if dangerous_nodes:
            logger.warning(f"Dangerous Python constructs detected: {dangerous_nodes}")
            raise InputValidationError(
                f"Python code contains dangerous constructs: {dangerous_nodes}"
            )

        return code

    def _check_ast_nodes(self, tree: ast.AST) -> list[str]:
        """Check AST nodes for dangerous constructs."""
        dangerous_nodes = []

        class DangerousNodeVisitor(ast.NodeVisitor):
            def visit_Import(self, node):
                # Check for dangerous imports
                dangerous_imports = {
                    "os",
                    "sys",
                    "subprocess",
                    "shutil",
                    "socket",
                    "urllib",
                    "requests",
                }
                for alias in node.names:
                    if alias.name in dangerous_imports:
                        dangerous_nodes.append(f"import {alias.name}")
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                # Check for dangerous from imports
                dangerous_modules = {
                    "os",
                    "sys",
                    "subprocess",
                    "shutil",
                    "socket",
                    "urllib",
                    "requests",
                }
                if node.module in dangerous_modules:
                    dangerous_nodes.append(f"from {node.module} import ...")
                self.generic_visit(node)

            def visit_Call(self, node):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    dangerous_functions = {
                        "exec",
                        "eval",
                        "compile",
                        "__import__",
                        "open",
                        "input",
                    }
                    if node.func.id in dangerous_functions:
                        dangerous_nodes.append(f"call to {node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    # Check for dangerous method calls
                    if isinstance(node.func.value, ast.Name):
                        dangerous_methods = {
                            "os": ["system", "popen", "spawn", "exec"],
                            "sys": ["exit", "exec_info"],
                            "subprocess": ["run", "call", "check_output", "Popen"],
                        }
                        module = node.func.value.id
                        method = node.func.attr
                        if (
                            module in dangerous_methods
                            and method in dangerous_methods[module]
                        ):
                            dangerous_nodes.append(f"call to {module}.{method}")
                self.generic_visit(node)

        visitor = DangerousNodeVisitor()
        visitor.visit(tree)

        return dangerous_nodes

    def validate_json_data(self, data: dict | list) -> dict | list:
        """Validate JSON data structure."""
        if not isinstance(data, dict | list):
            raise InputValidationError("Data must be a dictionary or list")

        # Recursively validate strings in the data structure
        return self._validate_json_recursive(data)

    def _validate_json_recursive(self, data: Any) -> Any:
        """Recursively validate JSON data."""
        if isinstance(data, dict):
            return {
                key: self._validate_json_recursive(value) for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._validate_json_recursive(item) for item in data]
        elif isinstance(data, str):
            return self.validate_string(
                data, max_length=1000
            )  # Shorter limit for JSON strings
        else:
            return data

    def validate_url(self, url: str) -> str:
        """Validate URL for safety."""
        if not isinstance(url, str):
            raise InputValidationError("URL must be a string")

        # Parse URL
        try:
            parsed = urllib.parse.urlparse(url)
        except Exception as e:
            raise InputValidationError(f"Invalid URL: {e}")

        # Check scheme
        if parsed.scheme not in ["http", "https"]:
            raise InputValidationError("Only HTTP and HTTPS URLs are allowed")

        # Check for localhost/private IPs to prevent SSRF
        if parsed.hostname in ["localhost", "127.0.0.1", "0.0.0.0"]:
            raise InputValidationError("Localhost URLs are not allowed")

        # Check for private IP ranges
        if parsed.hostname:
            import ipaddress

            try:
                ip = ipaddress.ip_address(parsed.hostname)
                if ip.is_private:
                    raise InputValidationError("Private IP addresses are not allowed")
            except ValueError:
                pass  # Not an IP address, continue

        return url


# Global validator instance
validator = SecureInputValidator()
