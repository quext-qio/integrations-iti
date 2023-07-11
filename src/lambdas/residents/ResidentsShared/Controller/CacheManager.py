import logging
from datetime import datetime, timedelta

class CacheManager:
    '''
    class to read and write to cache
    '''
    __cache = {}

    def get_from_cache(self, cache_name: str, cache_key: str, decrypt: bool = False) -> str:
        # Method to read data from cache
        cache = self.__cache.get(cache_name)
        if cache is None:
            return None
        cache_value = cache.get(cache_key)
        if cache_value is None:
            return None
        if decrypt:
            cache_value = self.__decrypt(cache_value)
        logging.info("Query Read from cache success")
        return cache_value

    def update_cache(self, cache_name: str, cache_key: str, value: str, cache_dur: float = 600.0, encrypt: bool = False):
        # Method to update data in cache
        cache = self.__cache.get(cache_name)
        if cache is None:
            cache = {}
            self.__cache[cache_name] = cache
        if encrypt:
            value = self.__encrypt(value)
        cache[cache_key] = value
        # Set cache duration
        expire_time = datetime.now() + timedelta(seconds=cache_dur)
        cache["__expire_time__"] = expire_time

    def __encrypt(self, value: str) -> str:
        # Encrypt the value (implement your encryption logic here)
        # ...
        return value

    def __decrypt(self, value: str) -> str:
        # Decrypt the value (implement your decryption logic here)
        # ...
        return value
