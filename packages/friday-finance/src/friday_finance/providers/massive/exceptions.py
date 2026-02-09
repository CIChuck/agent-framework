class MassiveBaseException(Exception):
    """Base exception for all massive-agent-core errors."""
    pass

class MassiveAuthError(MassiveBaseException):
    """Raised when the API Key is invalid or missing."""
    pass

class MassiveRateLimitError(MassiveBaseException):
    """Raised when the 5 calls/minute limit is exceeded."""
    def __init__(self, message="Rate limit exceeded. Wait 60 seconds.", retry_after=60):
        super().__init__(message)
        self.retry_after = retry_after

class MassiveMarketClosedError(MassiveBaseException):
    """Raised when data is requested for a time the market was closed."""
    pass

class MassiveNotFoundError(MassiveBaseException):
    """Raised when a ticker or indicator is not found."""
    pass

class MassiveTimeoutError(MassiveBaseException):
    """Raised when a query exceeds the defined timeout."""
    pass
