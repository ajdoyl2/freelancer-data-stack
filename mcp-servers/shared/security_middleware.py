"""Security middleware for MCP servers."""

import hashlib
import logging
import secrets
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for HTTP endpoints."""

    def __init__(
        self, app: ASGIApp, rate_limit_requests: int = 100, rate_limit_window: int = 60
    ):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.request_counts: dict[str, list] = {}
        self.blocked_ips: dict[str, float] = {}
        self.nonce_cache: dict[str, float] = {}

    async def dispatch(self, request: Request, call_next):
        """Process request with security checks."""
        client_ip = self._get_client_ip(request)

        # Check if IP is blocked
        if self._is_ip_blocked(client_ip):
            logger.warning(f"Blocked request from IP: {client_ip}")
            return Response(
                content="Too many requests. Please try again later.",
                status_code=429,
                headers={"Retry-After": "300"},
            )

        # Rate limiting
        if self._is_rate_limited(client_ip):
            logger.warning(f"Rate limited request from IP: {client_ip}")
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=429,
                headers={"Retry-After": "60"},
            )

        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

        # Generate and add nonce for CSP
        nonce = secrets.token_urlsafe(16)
        response.headers["X-Nonce"] = nonce

        # Log security events
        if response.status_code >= 400:
            logger.warning(
                f"Security event: {response.status_code} response for {client_ip} on {request.url}"
            )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers (in case of proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP is blocked."""
        if client_ip in self.blocked_ips:
            block_time = self.blocked_ips[client_ip]
            if time.time() - block_time < 300:  # 5 minute block
                return True
            else:
                del self.blocked_ips[client_ip]
        return False

    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if IP is rate limited."""
        current_time = time.time()

        # Initialize IP tracking if not exists
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []

        # Clean old requests
        self.request_counts[client_ip] = [
            req_time
            for req_time in self.request_counts[client_ip]
            if current_time - req_time < self.rate_limit_window
        ]

        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.rate_limit_requests:
            # Block IP for repeated rate limit violations
            self.blocked_ips[client_ip] = current_time
            return True

        # Add current request
        self.request_counts[client_ip].append(current_time)
        return False


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware."""

    def __init__(self, app: ASGIApp, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key
        self.csrf_tokens: dict[str, float] = {}

    async def dispatch(self, request: Request, call_next):
        """Process request with CSRF protection."""
        # Skip CSRF check for GET, HEAD, OPTIONS
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)

        # Check for CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token:
            logger.warning(f"Missing CSRF token for {request.method} {request.url}")
            return Response(content="CSRF token required", status_code=403)

        # Validate CSRF token
        if not self._validate_csrf_token(csrf_token):
            logger.warning(f"Invalid CSRF token for {request.method} {request.url}")
            return Response(content="Invalid CSRF token", status_code=403)

        return await call_next(request)

    def _validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token."""
        try:
            # Check if token exists and is not expired
            if token in self.csrf_tokens:
                token_time = self.csrf_tokens[token]
                if time.time() - token_time < 3600:  # 1 hour validity
                    return True
                else:
                    del self.csrf_tokens[token]

            # Validate token structure (should be signed with secret)
            expected_token = self._generate_csrf_token()
            return token == expected_token

        except Exception:
            return False

    def _generate_csrf_token(self) -> str:
        """Generate CSRF token."""
        timestamp = str(int(time.time()))
        data = f"{timestamp}:{self.secret_key}"
        token = hashlib.sha256(data.encode()).hexdigest()
        full_token = f"{timestamp}:{token}"

        # Store token
        self.csrf_tokens[full_token] = time.time()

        return full_token


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Request validation middleware."""

    def __init__(self, app: ASGIApp, max_request_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next):
        """Process request with validation."""
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            logger.warning(f"Request size too large: {content_length} bytes")
            return Response(content="Request too large", status_code=413)

        # Validate content type for POST requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            allowed_types = [
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
            ]

            if not any(allowed_type in content_type for allowed_type in allowed_types):
                logger.warning(f"Invalid content type: {content_type}")
                return Response(content="Invalid content type", status_code=415)

        # Check for suspicious headers
        suspicious_headers = [
            "x-forwarded-host",
            "x-forwarded-proto",
            "x-original-url",
            "x-rewrite-url",
        ]

        for header in suspicious_headers:
            if header in request.headers:
                logger.warning(f"Suspicious header detected: {header}")

        return await call_next(request)
