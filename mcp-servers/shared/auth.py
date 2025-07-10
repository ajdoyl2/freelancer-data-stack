"""Authentication and authorization for MCP servers."""

import logging
import os
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import wraps

from jose import JWTError, jwt
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET environment variable is required")
if len(SECRET_KEY) < 32:
    raise ValueError("JWT_SECRET must be at least 32 characters long")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes


class TokenData(BaseModel):
    """JWT token payload data."""

    username: str
    role: str = "user"
    permissions: list[str] = []
    exp: datetime | None = None


class AuthManager:
    """Manages authentication and authorization for MCP servers."""

    def __init__(self, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.failed_attempts = {}  # Track failed login attempts
        self.locked_users = {}  # Track locked users
        self.role_permissions = {
            "admin": ["*"],  # All permissions
            "data_engineer": [
                "execute_query",
                "manage_pipelines",
                "view_metadata",
                "run_transformations",
            ],
            "analyst": ["execute_query", "view_metadata", "create_reports"],
            "viewer": ["view_metadata", "view_reports"],
        }

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """Create a new JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> TokenData:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            role: str = payload.get("role", "user")
            permissions: list = payload.get("permissions", [])

            if username is None:
                logger.warning("Token validation failed: missing username")
                raise ValueError("Invalid token: missing username")

            # Check if user is locked
            if self._is_user_locked(username):
                logger.warning(f"Access denied for locked user: {username}")
                raise ValueError("User account is locked")

            logger.info(f"Token validated successfully for user: {username}")
            return TokenData(username=username, role=role, permissions=permissions)
        except JWTError as e:
            logger.warning(f"Token validation failed: {e}")
            raise ValueError(f"Invalid token: {e}")

    def _is_user_locked(self, username: str) -> bool:
        """Check if user account is locked."""
        if username in self.locked_users:
            lock_time = self.locked_users[username]
            if time.time() - lock_time < LOCKOUT_DURATION:
                return True
            else:
                # Unlock user after lockout duration
                del self.locked_users[username]
                if username in self.failed_attempts:
                    del self.failed_attempts[username]
        return False

    def _record_failed_attempt(self, username: str) -> None:
        """Record a failed authentication attempt."""
        current_time = time.time()

        if username not in self.failed_attempts:
            self.failed_attempts[username] = []

        # Clean old attempts (older than 1 hour)
        self.failed_attempts[username] = [
            attempt_time
            for attempt_time in self.failed_attempts[username]
            if current_time - attempt_time < 3600
        ]

        self.failed_attempts[username].append(current_time)

        # Lock user if too many failed attempts
        if len(self.failed_attempts[username]) >= MAX_FAILED_ATTEMPTS:
            self.locked_users[username] = current_time
            logger.warning(f"User {username} locked due to too many failed attempts")

    def check_permission(self, token_data: TokenData, required_permission: str) -> bool:
        """Check if user has required permission."""
        # Admin has all permissions
        if token_data.role == "admin" or "*" in token_data.permissions:
            return True

        # Check role-based permissions
        role_perms = self.role_permissions.get(token_data.role, [])
        if required_permission in role_perms or "*" in role_perms:
            return True

        # Check explicit permissions
        return required_permission in token_data.permissions

    def require_permission(self, permission: str):
        """Decorator to require specific permission for a function."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract token from kwargs (passed by MCP framework)
                auth_header = kwargs.get("_auth_header")
                if not auth_header:
                    raise PermissionError("Authentication required")

                try:
                    # Extract token from "Bearer <token>" format
                    token = (
                        auth_header.split(" ")[1] if " " in auth_header else auth_header
                    )
                    token_data = self.verify_token(token)

                    if not self.check_permission(token_data, permission):
                        raise PermissionError(
                            f"Permission denied: requires '{permission}'"
                        )

                    # Add token data to kwargs for use in function
                    kwargs["_token_data"] = token_data

                    return await func(*args, **kwargs)
                except ValueError as e:
                    raise PermissionError(f"Authentication failed: {e}")

            return wrapper

        return decorator


# Global auth manager instance
auth_manager = AuthManager()


def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication for MCP tools."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract auth header from MCP context
        context = kwargs.get("_context", {})
        auth_header = context.get("auth_header")

        if not auth_header:
            logger.warning("Authentication required but no auth header provided")
            return {"error": "Authentication required", "status": "unauthorized"}

        try:
            # Verify token
            token = auth_header.split(" ")[1] if " " in auth_header else auth_header
            token_data = auth_manager.verify_token(token)

            # Add user info to kwargs
            kwargs["_user"] = token_data

            return await func(*args, **kwargs)
        except Exception as e:
            # Record failed attempt if we can extract username
            try:
                token = auth_header.split(" ")[1] if " " in auth_header else auth_header
                payload = jwt.decode(
                    token, verify=False
                )  # Don't verify for failed attempt logging
                username = payload.get("sub")
                if username:
                    auth_manager._record_failed_attempt(username)
            except:
                pass  # If we can't extract username, continue with error response

            logger.warning(f"Authentication failed: {str(e)}")
            return {
                "error": f"Authentication failed: {str(e)}",
                "status": "unauthorized",
            }

    return wrapper
