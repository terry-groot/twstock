"""Resilience patterns: retry logic, circuit breakers, etc."""

import time
from typing import Callable, Any, Optional, List, Dict
from market_monitor.logging_setup import get_logger

logger = get_logger("resilience")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_backoff: float = 1.0,
        max_backoff: float = 60.0,
        exponential_base: float = 2.0,
    ):
        """Initialize retry configuration.

        Args:
            max_attempts: Maximum retry attempts
            initial_backoff: Initial backoff in seconds
            max_backoff: Maximum backoff in seconds
            exponential_base: Base for exponential backoff calculation
        """
        self.max_attempts = max_attempts
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.exponential_base = exponential_base

    def get_backoff(self, attempt: int) -> float:
        """Calculate backoff time for attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Backoff time in seconds
        """
        backoff = self.initial_backoff * (self.exponential_base ** attempt)
        return min(backoff, self.max_backoff)


def retry_with_backoff(
    func: Callable,
    *args,
    config: RetryConfig = None,
    is_retryable: Optional[Callable[[Exception], bool]] = None,
    **kwargs
) -> Any:
    """Retry a function with exponential backoff.

    Args:
        func: Function to retry
        *args: Positional arguments for function
        config: RetryConfig instance
        is_retryable: Optional function to determine if exception is retryable
        **kwargs: Keyword arguments for function

    Returns:
        Function result

    Raises:
        Last exception if all retries exhausted
    """
    if config is None:
        config = RetryConfig()

    last_exception = None
    for attempt in range(config.max_attempts):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            is_final_attempt = (attempt == config.max_attempts - 1)

            # Check if error is retryable
            if is_retryable and not is_retryable(e):
                logger.debug(f"Non-retryable error: {e}")
                raise

            if is_final_attempt:
                logger.error(f"Failed after {config.max_attempts} attempts: {e}")
                raise

            backoff = config.get_backoff(attempt)
            logger.debug(f"Attempt {attempt + 1} failed: {e}. Retrying in {backoff}s")
            time.sleep(backoff)

    # Should not reach here
    raise last_exception


class CircuitBreaker:
    """Circuit breaker pattern to prevent cascading failures."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open

    def record_success(self) -> None:
        """Record a successful call."""
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None

    def record_failure(self) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

    def can_attempt(self) -> bool:
        """Check if call can be attempted.

        Returns:
            True if call can be attempted
        """
        if self.state == "closed":
            return True

        if self.state == "open":
            # Check if recovery timeout has elapsed
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed > self.recovery_timeout:
                    self.state = "half-open"
                    logger.info("Circuit breaker half-open, attempting recovery")
                    return True
            return False

        # Half-open: allow one attempt
        return True

    def get_state(self) -> Dict[str, Any]:
        """Get circuit breaker state.

        Returns:
            State dictionary
        """
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
        }


def call_with_circuit_breaker(
    func: Callable,
    circuit_breaker: CircuitBreaker,
    *args,
    **kwargs
) -> Any:
    """Call function with circuit breaker protection.

    Args:
        func: Function to call
        circuit_breaker: CircuitBreaker instance
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result

    Raises:
        RuntimeError if circuit is open
        Original exception from func
    """
    if not circuit_breaker.can_attempt():
        raise RuntimeError(f"Circuit breaker is {circuit_breaker.state}")

    try:
        result = func(*args, **kwargs)
        circuit_breaker.record_success()
        return result
    except Exception as e:
        circuit_breaker.record_failure()
        raise
