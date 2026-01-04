import time

class SimpleCache:
    def __init__(self):
        self.store = {}

    def get(self, key: str):
        data = self.store.get(key)
        if not data:
            return None

        value, expires_at = data
        if expires_at < time.time():
            del self.store[key]
            return None

        return value

    def set(self, key: str, value, ttl: int = 60):
        self.store[key] = (value, time.time() + ttl)

    def invalidate_prefix(self, prefix: str):
        keys = [k for k in self.store if k.startswith(prefix)]
        for k in keys:
            del self.store[k]

cache = SimpleCache()
