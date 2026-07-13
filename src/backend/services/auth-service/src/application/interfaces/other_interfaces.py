from typing import Protocol, Any


class CacheProtocol(Protocol):
    """
    Protocol for cache operations.

    This protocol defines the interface for caching implementations.
    Values are stored as Any type to support various serialization formats.
    """

    async def get(self, key: str) -> dict[str, Any] | None:
        """
        Retrieve a value from cache by key.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached dictionary data or None if not found
        """
        ...

    async def set(
        self, key: str, value: dict[str, Any], ttl: int | None = None
    ) -> None:
        """
        Store a value in cache with optional TTL.

        Args:
            key: Cache key to store under
            value: Dictionary data to cache
            ttl: Time-to-live in seconds (None for default)

        Returns:
            True if successful, False otherwise
        """
        ...

    async def delete(self, key: str) -> None:
        """
        Delete a value from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False if key didn't exist
        """
        ...

    async def exists(self, key: str) -> None:
        """
        Check if a key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise
        """
        ...

    async def clear(self, pattern: str) -> int:
        """
        Clear cache entries matching a pattern.

        Args:
            pattern: Pattern to match keys (e.g., 'user:*')

        Returns:
            Number of keys deleted
        """
        ...

    async def hgetall(self, pattern: str) -> dict[str, Any] | None: ...


class SerializationMapperProtocol(Protocol):
    """
    Protocol for serialization/deserialization of Application DTOs.

    This interface allows the Application layer to serialize DTOs
    without depending on Infrastructure implementations.
    """

    @staticmethod
    def to_dict(dto) -> dict[str, Any]:
        """
        Converts an Application DTO to a dictionary for serialization.

        Args:
            dto: The ArtifactDTO to convert.

        Returns:
            A dictionary representation of the DTO.
        """
        ...

    @staticmethod
    def from_dict(data: dict[str, Any]):
        """
        Converts a dictionary from deserialization back to an Application DTO.

        Args:
            data: The dictionary to convert.

        Returns:
            An ArtifactDTO object.
        """
        ...


class HttpApiProtocol(Protocol):
    """
    Protocol for http api operations.
    """

    async def get(self, params: str) -> Any: ...

    async def post(self, params: str, value: dict[str, Any]) -> None: ...
