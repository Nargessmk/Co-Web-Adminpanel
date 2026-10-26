"""Custom exception hierarchy for the Gateway."""


class GatewayError(Exception):
    """Base exception for all Gateway-specific errors."""


class BackendUnavailableError(GatewayError):
    """Raised when a downstream service is unreachable."""

    def __init__(self, service: str, url: str):
        self.service = service
        self.url = url
        super().__init__(f"Backend service '{service}' unavailable at {url}")


class RateLimitExceededError(GatewayError):
    """Raised when client exceeds rate limit."""

    def __init__(self, client_ip: str):
        self.client_ip = client_ip
        super().__init__(f"Rate limit exceeded for {client_ip}")
