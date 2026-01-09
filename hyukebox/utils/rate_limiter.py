"""Rate limiting for API calls using token bucket algorithm."""

import asyncio
from datetime import datetime, timedelta
from typing import List


class RateLimiter:
    """Token bucket rate limiter for API calls.

    Ensures API calls don't exceed specified rate limits.
    """

    def __init__(self, calls_per_minute: int):
        """Initialize rate limiter.

        Args:
            calls_per_minute: Maximum number of calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.calls: List[datetime] = []

    async def acquire(self) -> None:
        """Wait until we can make a call within rate limits.

        This method blocks if the rate limit would be exceeded.
        """
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)

        # Remove calls older than 1 minute
        self.calls = [t for t in self.calls if t > cutoff]

        if len(self.calls) >= self.calls_per_minute:
            # Calculate wait time
            oldest_call = self.calls[0]
            wait_seconds = 60 - (now - oldest_call).total_seconds()

            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)

            # Re-check after waiting
            now = datetime.now()
            cutoff = now - timedelta(minutes=1)
            self.calls = [t for t in self.calls if t > cutoff]

        # Record this call
        self.calls.append(now)

    def reset(self) -> None:
        """Reset the rate limiter."""
        self.calls.clear()

    def get_remaining(self) -> int:
        """Get number of remaining calls in current window.

        Returns:
            Number of calls that can be made without waiting
        """
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        self.calls = [t for t in self.calls if t > cutoff]

        return max(0, self.calls_per_minute - len(self.calls))
