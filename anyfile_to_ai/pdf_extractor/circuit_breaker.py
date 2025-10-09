"""Circuit breaker for VLM service failures."""

import time
from dataclasses import dataclass


@dataclass
class VLMCircuitBreaker:
    """Circuit breaker for VLM service failures."""

    failure_count: int = 0
    failure_threshold: int = 3
    last_failure_time: float | None = None
    recovery_timeout: float = 60.0
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_process(self) -> bool:
        """Check if VLM processing is allowed."""
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        return self.state == "HALF_OPEN"

    def record_success(self) -> None:
        """Record successful VLM operation."""
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = None

    def record_failure(self) -> None:
        """Record VLM operation failure."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def get_state(self) -> str:
        """Get current circuit breaker state."""
        return self.state
