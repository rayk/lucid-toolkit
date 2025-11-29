# Design Document: [System Name]

> Complete this template to generate TDD execution prompts using `/planner:generate`.
> Remove guidance comments (lines starting with >) before generating the execution prompt.

## 1. System Identity

> Provide basic system identification for execution environment setup.

**System Name**: [e.g., cache-service, auth-manager, data-processor]

**Primary Language**: [python | typescript | go | rust | java | ruby]

**Language Version**: [e.g., Python 3.11+, TypeScript 5.0+, Go 1.21+]

**Framework(s)**: [e.g., FastAPI, Express.js, none]

**Target Runtime**: [e.g., Docker container, AWS Lambda, standalone binary]

## 2. Dependencies

> Categorize dependencies by timing. This is CRITICAL for phase planning.

### External Libraries

> Libraries installed via package manager. Include version constraints.

```yaml
# Example for Python:
redis: ">=4.0.0"
pydantic: ">=2.0.0"
pytest: ">=7.0.0"  # dev dependency
pytest-asyncio: ">=0.21.0"  # dev dependency
```

### Pre-Existing Internal Dependencies

> Internal modules that MUST exist BEFORE execution starts.
> If these don't exist, generation will FAIL with PREREQ_MISSING.

```yaml
# Example:
common.logging.logger: "Logger class for structured logging"
common.config.settings: "Application configuration management"
```

### Created Internal Dependencies

> Modules created DURING execution, with phase mapping.
> Used for dependency ordering and validation.

```yaml
# Example:
cache.types: "Phase 2 - Core types and interfaces"
cache.errors: "Phase 2 - Error hierarchy"
cache.config: "Phase 2 - Configuration models"
cache.service: "Phase 3 - Main CacheService class"
cache.redis_backend: "Phase 4 - Redis implementation"
cache.memory_backend: "Phase 4 - In-memory implementation"
```

## 3. Module Structure

> Define directory layout and file responsibilities.

### Directory Layout

```
[project-root]/
├── src/
│   └── [module-name]/
│       ├── __init__.py          # Public API exports
│       ├── types.py             # Core types and protocols
│       ├── errors.py            # Exception hierarchy
│       ├── config.py            # Configuration models
│       ├── [main-service].py    # Primary service class
│       ├── [feature-1].py       # Feature module 1
│       └── [feature-2].py       # Feature module 2
└── tests/
    └── [module-name]/
        ├── test_types.py
        ├── test_errors.py
        ├── test_config.py
        ├── test_[main-service].py
        ├── test_[feature-1].py
        └── test_[feature-2].py
```

### File Responsibilities

> Map each file to its purpose and key exports.

| File | Purpose | Key Exports |
|------|---------|-------------|
| `types.py` | Core data types and protocols | `CacheKey`, `CacheValue`, `CacheBackend` (protocol) |
| `errors.py` | Exception hierarchy | `CacheError`, `CacheKeyError`, `CacheConnectionError` |
| `config.py` | Configuration models | `CacheConfig`, `RedisConfig`, `MemoryConfig` |
| `service.py` | Main service implementation | `CacheService` |
| `redis_backend.py` | Redis-backed cache | `RedisCacheBackend` |
| `memory_backend.py` | In-memory cache | `MemoryCacheBackend` |

### Public API Surface

> Define what gets exported from `__init__.py`.

```python
# Example for Python:
from .service import CacheService
from .types import CacheKey, CacheValue, CacheBackend
from .errors import CacheError, CacheKeyError, CacheConnectionError
from .config import CacheConfig

__all__ = [
    "CacheService",
    "CacheKey",
    "CacheValue",
    "CacheBackend",
    "CacheError",
    "CacheKeyError",
    "CacheConnectionError",
    "CacheConfig",
]
```

## 4. Type System

> Define all core types, configuration models, errors, and result types.

### Core Data Types

> Foundation types used throughout the system.

```python
# Example for Python:

from typing import TypeAlias, Protocol, Any
from datetime import timedelta

# Type aliases for clarity
CacheKey: TypeAlias = str
CacheValue: TypeAlias = Any

class CacheBackend(Protocol):
    """Protocol defining cache backend interface.

    LLM Context:
    - All cache backends MUST implement this protocol
    - Enables swapping between Redis, in-memory, or custom backends
    - All methods are async to support async cache operations

    See Also:
        RedisCacheBackend: Redis implementation
        MemoryCacheBackend: In-memory implementation
    """

    async def get(self, key: CacheKey) -> CacheValue | None:
        """Retrieve value by key, return None if not found."""
        ...

    async def set(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: timedelta | None = None
    ) -> None:
        """Store value with optional TTL."""
        ...

    async def delete(self, key: CacheKey) -> bool:
        """Delete key, return True if existed."""
        ...

    async def clear(self) -> None:
        """Clear all cache entries."""
        ...
```

### Configuration Types

> Configuration models with validation.

```python
# Example for Python with Pydantic:

from pydantic import BaseModel, Field, validator
from typing import Literal

class RedisConfig(BaseModel):
    """Redis backend configuration.

    LLM Context:
    - Used when backend_type is 'redis'
    - Validates connection parameters
    - Supports connection pooling configuration
    """

    host: str = Field(default="localhost")
    port: int = Field(default=6379, ge=1, le=65535)
    db: int = Field(default=0, ge=0, le=15)
    password: str | None = Field(default=None)
    max_connections: int = Field(default=10, ge=1)

class MemoryConfig(BaseModel):
    """In-memory backend configuration.

    LLM Context:
    - Used when backend_type is 'memory'
    - Simple configuration for testing/development
    """

    max_size: int = Field(default=1000, ge=1)

class CacheConfig(BaseModel):
    """Main cache service configuration.

    LLM Context:
    - Top-level configuration model
    - Uses discriminated union for backend-specific config
    - Validates configuration before service initialization
    """

    backend_type: Literal["redis", "memory"]
    default_ttl: int = Field(default=300, ge=0)  # seconds
    redis: RedisConfig | None = None
    memory: MemoryConfig | None = None

    @validator("redis")
    def validate_redis_config(cls, v, values):
        if values.get("backend_type") == "redis" and v is None:
            raise ValueError("redis config required when backend_type is 'redis'")
        return v

    @validator("memory")
    def validate_memory_config(cls, v, values):
        if values.get("backend_type") == "memory" and v is None:
            raise ValueError("memory config required when backend_type is 'memory'")
        return v
```

### Error/Exception Types

> Complete exception hierarchy with context.

```python
# Example for Python:

class CacheError(Exception):
    """Base exception for all cache errors.

    LLM Context:
    - Catch this to handle any cache-related error
    - All cache errors inherit from this
    - Includes error code for programmatic handling

    Attributes:
        message: Human-readable error description
        code: Machine-readable error code
        details: Additional context (optional)
    """

    def __init__(self, message: str, code: str, details: dict | None = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class CacheKeyError(CacheError):
    """Raised when cache key is invalid.

    LLM Context:
    - Use for key validation failures
    - Includes the invalid key in details

    Example:
        raise CacheKeyError(
            message="Key cannot be empty",
            code="INVALID_KEY",
            details={"key": ""}
        )
    """
    pass

class CacheConnectionError(CacheError):
    """Raised when backend connection fails.

    LLM Context:
    - Use for Redis connection failures
    - Indicates transient error, retry may help
    - Includes connection details for debugging
    """
    pass

class CacheOperationError(CacheError):
    """Raised when cache operation fails.

    LLM Context:
    - Use for get/set/delete failures
    - Wraps underlying backend errors
    """
    pass
```

### Result/Response Types

> Types for function returns, API responses, etc.

```python
# Example:

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass
class CacheStats:
    """Cache statistics.

    LLM Context:
    - Returned by get_stats() method
    - Useful for monitoring and debugging
    """

    hits: int
    misses: int
    size: int
    hit_rate: float
```

## 5. API Contracts

> Define all public method signatures with contracts.

### Main Service Class

```python
# Example:

class CacheService:
    """Main cache service with pluggable backends.

    LLM Context:
    - Primary interface for all cache operations
    - Delegates to backend implementation (Redis or in-memory)
    - Handles statistics tracking and error translation
    - All operations are async

    Initialization:
        service = CacheService(config)
        await service.initialize()

    Cleanup:
        await service.close()

    Example:
        config = CacheConfig(backend_type="redis", redis=RedisConfig())
        service = CacheService(config)
        await service.initialize()
        try:
            await service.set("user:123", {"name": "Alice"})
            user = await service.get("user:123")
        finally:
            await service.close()

    See Also:
        CacheBackend: Backend protocol
        CacheConfig: Configuration model
    """

    def __init__(self, config: CacheConfig):
        """Initialize cache service.

        Args:
            config: Cache configuration

        Raises:
            ValueError: If config is invalid
        """
        ...

    async def initialize(self) -> None:
        """Initialize backend connection.

        LLM Context:
        - MUST be called before any cache operations
        - Establishes connection to Redis or initializes in-memory store
        - Idempotent - safe to call multiple times

        Raises:
            CacheConnectionError: If backend connection fails
        """
        ...

    async def get(self, key: CacheKey) -> CacheValue | None:
        """Retrieve value by key.

        Args:
            key: Cache key (non-empty string)

        Returns:
            Cached value if exists, None otherwise

        Raises:
            CacheKeyError: If key is invalid (empty, wrong type)
            CacheOperationError: If backend operation fails

        Example:
            value = await service.get("user:123")
            if value is None:
                # Cache miss
                value = load_from_database("user:123")
                await service.set("user:123", value)
        """
        ...

    async def set(
        self,
        key: CacheKey,
        value: CacheValue,
        ttl: timedelta | None = None
    ) -> None:
        """Store value with optional TTL.

        Args:
            key: Cache key (non-empty string)
            value: Value to cache (must be serializable)
            ttl: Time-to-live (optional, uses default_ttl if None)

        Raises:
            CacheKeyError: If key is invalid
            CacheOperationError: If backend operation fails

        Example:
            # Use default TTL
            await service.set("user:123", user_data)

            # Custom TTL
            await service.set(
                "session:abc",
                session_data,
                ttl=timedelta(hours=1)
            )
        """
        ...

    async def delete(self, key: CacheKey) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key existed and was deleted, False if key didn't exist

        Raises:
            CacheKeyError: If key is invalid
            CacheOperationError: If backend operation fails
        """
        ...

    async def clear(self) -> None:
        """Clear all cache entries.

        LLM Context:
        - Use with caution - removes ALL cached data
        - Useful for testing and cache invalidation

        Raises:
            CacheOperationError: If backend operation fails
        """
        ...

    async def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            Current cache statistics

        Example:
            stats = await service.get_stats()
            print(f"Hit rate: {stats.hit_rate:.2%}")
        """
        ...

    async def close(self) -> None:
        """Close backend connection and cleanup.

        LLM Context:
        - MUST be called when done with service
        - Releases connections and resources
        - Idempotent - safe to call multiple times
        """
        ...
```

### Async/Sync Requirements

> Specify which methods must be async/sync and why.

- **All cache operations MUST be async** - Supports async backends (Redis) without blocking
- **Configuration and validation are sync** - No I/O, immediate validation
- **Statistics tracking is sync** - In-memory counters, no I/O

### Error Handling Contracts

> Define error handling expectations.

| Method | Errors | Contract |
|--------|--------|----------|
| `initialize()` | `CacheConnectionError` | Retry with exponential backoff recommended |
| `get()` | `CacheKeyError`, `CacheOperationError` | Key validation before backend call |
| `set()` | `CacheKeyError`, `CacheOperationError` | Key/value validation before backend call |
| `delete()` | `CacheKeyError`, `CacheOperationError` | Returns False for missing keys (not error) |
| `clear()` | `CacheOperationError` | Cannot be undone, use with caution |
| `get_stats()` | Never raises | Always returns current stats |
| `close()` | Never raises | Swallows errors, logs warnings |

## 6. Implementation Patterns

> Provide concrete examples of required patterns.

### Required Patterns

#### Pattern 1: Backend Factory

```python
def _create_backend(config: CacheConfig) -> CacheBackend:
    """Create backend instance based on config.

    LLM Context:
    - Factory pattern for backend creation
    - Centralizes backend instantiation logic
    - Returns protocol-compliant backend
    """
    if config.backend_type == "redis":
        return RedisCacheBackend(config.redis)
    elif config.backend_type == "memory":
        return MemoryCacheBackend(config.memory)
    else:
        raise ValueError(f"Unknown backend type: {config.backend_type}")
```

#### Pattern 2: Statistics Tracking Decorator

```python
from functools import wraps

def track_stats(operation: str):
    """Decorator to track cache operation statistics.

    LLM Context:
    - Wraps cache methods to track hits/misses
    - Updates internal counters automatically
    - Transparent to callers
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            result = await func(self, *args, **kwargs)

            if operation == "get":
                if result is None:
                    self._stats.misses += 1
                else:
                    self._stats.hits += 1

            return result
        return wrapper
    return decorator
```

#### Pattern 3: Key Validation

```python
def _validate_key(key: CacheKey) -> None:
    """Validate cache key.

    LLM Context:
    - Called before all operations
    - Ensures key is non-empty string
    - Raises CacheKeyError if invalid
    """
    if not isinstance(key, str):
        raise CacheKeyError(
            message="Key must be a string",
            code="INVALID_KEY_TYPE",
            details={"key": key, "type": type(key).__name__}
        )

    if not key:
        raise CacheKeyError(
            message="Key cannot be empty",
            code="EMPTY_KEY",
            details={"key": key}
        )
```

### Initialization Pattern

```python
# Example async context manager pattern:

from contextlib import asynccontextmanager

@asynccontextmanager
async def cache_service(config: CacheConfig):
    """Context manager for cache service lifecycle.

    LLM Context:
    - Ensures proper initialization and cleanup
    - Recommended way to use CacheService

    Example:
        async with cache_service(config) as cache:
            await cache.set("key", "value")
            value = await cache.get("key")
    """
    service = CacheService(config)
    await service.initialize()
    try:
        yield service
    finally:
        await service.close()
```

### Resource Management

> Specify how resources are acquired and released.

- **Connection pooling**: Redis backend uses connection pool (max_connections config)
- **Cleanup on close**: `close()` method releases all connections and clears stats
- **Context manager**: Preferred pattern for automatic cleanup
- **Graceful degradation**: Connection failures log warnings, don't crash service

## 7. Anti-Patterns

> Explicitly prohibit incorrect approaches.

### Prohibitions

**NEVER**:
- Store non-serializable objects without custom serialization
- Call cache operations without calling `initialize()` first
- Ignore `CacheConnectionError` - always handle connection failures
- Use blocking I/O in async methods
- Mutate cached values without re-setting them
- Use cache for persistent storage (cache is ephemeral)

### Rejected Alternatives

> Document approaches considered and rejected.

| Alternative | Why Rejected |
|-------------|--------------|
| Sync-only API | Blocks event loop with Redis I/O |
| Global singleton | Hard to test, couples code to implementation |
| Auto-serialization of objects | Implicit behavior, fails with complex types |
| Infinite TTL default | Memory leaks, stale data |
| Silent error swallowing | Hides bugs, hard to debug |

### Security Constraints

- **No sensitive data in keys** - Keys may be logged for debugging
- **Validate input before caching** - Don't cache unvalidated user input
- **Redis password in config** - Never hardcode, use environment variables
- **Connection encryption** - Use TLS for production Redis connections (out of scope for this design)

## 8. Requirements Priority

> Organize requirements by priority level (P0-P3).

### P0 Requirements (Foundation)

> MUST be implemented first. System doesn't work without these.

- **P0-1**: Core types (`CacheKey`, `CacheValue`, `CacheBackend` protocol)
- **P0-2**: Error hierarchy (`CacheError` and subclasses)
- **P0-3**: Configuration models (`CacheConfig`, `RedisConfig`, `MemoryConfig`)
- **P0-4**: `CacheService` class initialization and cleanup

### P1 Requirements (Core Functionality)

> Primary features. System is minimally functional after P0+P1.

- **P1-1**: `CacheService.get()` - Retrieve values from cache
- **P1-2**: `CacheService.set()` - Store values with TTL
- **P1-3**: `CacheService.delete()` - Remove values
- **P1-4**: In-memory backend implementation (`MemoryCacheBackend`)
- **P1-5**: Redis backend implementation (`RedisCacheBackend`)
- **P1-6**: Backend factory pattern

### P2 Requirements (Extended Features)

> Nice-to-have features. Enhance usability.

- **P2-1**: `CacheService.clear()` - Clear all entries
- **P2-2**: Statistics tracking (hits, misses, size)
- **P2-3**: `CacheService.get_stats()` - Retrieve statistics
- **P2-4**: Async context manager helper
- **P2-5**: Key validation with detailed errors

### P3 Requirements (Tooling/Quality)

> Support tools and documentation. Not user-facing features.

- **P3-1**: LLM-optimized documentation for all public symbols
- **P3-2**: 80%+ test coverage
- **P3-3**: Type hints with mypy strict mode compliance
- **P3-4**: Performance benchmarks (get/set latency)

## 9. Exit Criteria

> Define explicit success criteria. Used for cross-check validation.

### Explicit Exit Criteria

**Functional Criteria**:
1. All cache operations (get/set/delete/clear) work with both backends
2. TTL expiration works correctly (tested with short TTLs)
3. Statistics tracking accurately counts hits and misses
4. Connection failures raise `CacheConnectionError` with retry guidance
5. Invalid keys raise `CacheKeyError` with helpful messages

**Quality Criteria**:
1. All tests pass with 80%+ line coverage
2. No mypy errors in strict mode
3. No ruff lint errors or warnings
4. All public symbols have LLM-optimized docstrings

**Performance Criteria**:
1. In-memory backend: < 1ms per operation
2. Redis backend: < 10ms per operation (local Redis)

### Implicit Criteria

> Derived from MUST statements in this document.

- All methods with async signatures MUST be implemented as async
- Configuration validation MUST happen before service initialization
- Backend factory MUST support both redis and memory types
- Close method MUST be idempotent
- Initialize method MUST be idempotent

### Custom Verification

> Specific tests to validate critical behaviors.

```python
# Example custom test:

async def test_ttl_expiration():
    """Verify TTL expiration works correctly.

    Exit criterion: Values expire after TTL and return None.
    """
    async with cache_service(config) as cache:
        await cache.set("key", "value", ttl=timedelta(seconds=1))

        # Immediate get succeeds
        assert await cache.get("key") == "value"

        # After TTL, get returns None
        await asyncio.sleep(1.1)
        assert await cache.get("key") is None

async def test_backend_switch():
    """Verify both backends work identically.

    Exit criterion: Same operations work on Redis and in-memory.
    """
    for backend_type in ["memory", "redis"]:
        config = create_config(backend_type)
        async with cache_service(config) as cache:
            await cache.set("key", "value")
            assert await cache.get("key") == "value"
            assert await cache.delete("key") is True
            assert await cache.get("key") is None
```

---

## Example: Simple Cache Service

> This example demonstrates a complete design for reference.
> Replace with your actual system design.

The template above is structured for a cache service with the following characteristics:

**System**: Cache service with pluggable backends (Redis and in-memory)

**Language**: Python 3.11+ with async/await

**Key Design Decisions**:
- Protocol-based backend abstraction for testability
- Async-first API for non-blocking I/O
- Statistics tracking for monitoring
- Comprehensive error hierarchy for debugging
- LLM-optimized documentation for AI consumption

**Execution Estimate** (approximate):
- **Tokens**: ~85,000 total
- **Duration**: ~45 minutes
- **Model Distribution**: 5% haiku, 85% sonnet, 10% opus
- **Cost**: ~$3.50 USD

**Phase Breakdown**:
- Phase 0: Setup (5 min)
- Phase 1: Scaffolding (5 min, haiku)
- Phase 2: Types/Errors/Config TDD (10 min, sonnet)
- Phase 3: CacheService TDD (10 min, sonnet)
- Phase 4: Backends TDD - parallel (10 min, sonnet)
- Phase 5: Integration (3 min, sonnet)
- Phase 6: Verification (2 min)
- Phase 7: Debug (conditional, opus)
- Phase 8: Cross-checks (15 min, sonnet + opus)

---

## Template Usage

1. **Copy this template** to your design document location
2. **Fill in all sections** - completeness determines execution quality
3. **Be explicit** - The more detail, the better the generated prompt
4. **Validate timing** - Ensure pre-existing deps exist before generation
5. **Remove guidance** - Delete all lines starting with `>` before generating
6. **Generate prompt**:
   ```bash
   /planner:generate ./design.md --language python
   ```

For questions or issues, see `/planner:analyze` for design validation.
