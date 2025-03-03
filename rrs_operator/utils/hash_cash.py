import typing as tp

class HashCache:
    _cache: tp.Dict[str, tp.Set[str]] = {}

    @classmethod
    def store_hash(cls, sender_address: str, hashes: tp.List[str]) -> None:
        """Stores hashes for a given sender address."""
        if sender_address not in cls._cache:
            cls._cache[sender_address] = set()
        cls._cache[sender_address].update(hashes)

    @classmethod
    def get_hashes(cls, sender_address: str) -> tp.Set[str]:
        """Retrieves all hashes stored for a given sender address."""
        return cls._cache.get(sender_address, set())

    @classmethod
    def remove_hashes(cls, sender_address: str, hashes: tp.List[str]) -> None:
        """Removes specific hashes from the cache for a sender address."""
        if sender_address in cls._cache:
            cls._cache[sender_address] -= set(hashes)
            if not cls._cache[sender_address]: 
                del cls._cache[sender_address]

    @classmethod
    def clear_hashes(cls, sender_address: str) -> None:
        """Clears all hashes for a given sender address."""
        cls._cache.pop(sender_address, None)
