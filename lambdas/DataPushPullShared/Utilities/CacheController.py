import logging

from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.Utils import encrypt_base64, decrypt_base64

class CacheManager:
    '''
    class to read and write to cache
    '''
    BUILTIN = 'builtin'
    
    def get_from_cache(self, service_request: ServiceRequest, cache_name: str,
                         cache_key: str, decrypt: bool = False) -> str:
        # Method to read data from cache
        cache = service_request.cache.get_cache(self.BUILTIN, cache_name)
        # TODO: need to validate whether the cache is None or not
        cache_value = cache.get(cache_key)
        if cache_value is None:
            return None
        if decrypt:
            cache_value = decrypt_base64(cache_value)
        logging.info("Query Read from cache success")
        return cache_value

    def update_cache(self, service_request: ServiceRequest, cache_name: str,
                       cache_key: str, value: str, cache_dur: float = 600.0, encrypt: bool = False):
        # Method to update data in cache
        cache = service_request.cache.get_cache(self.BUILTIN, cache_name)
        if encrypt:
            value = encrypt_base64(value)
        cache.set(cache_key, value, cache_dur)