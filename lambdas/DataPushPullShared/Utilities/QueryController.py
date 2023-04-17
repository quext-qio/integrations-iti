import logging

from pathlib import Path

from VendorShared.Model.ServiceRequest import ServiceRequest
from DataPushPullShared.Utilities.CacheController import CacheManager

class QueryController:
    '''
    Functions to read query from file
    '''
    __cache_obj = CacheManager()
    '''
    __dir_path is /opt/zato/3.1.0/code/zato_extra_paths/
    '''
    __dir_path = Path(__file__).resolve().parent.parent.parent

    def read_query(self, service_request: ServiceRequest, path: str,
                   cache_name: str, cache_key: str, cache_dur: float) -> str:
        '''
        Read the query from SQL file and returns it as string
        '''
        output = self.__cache_obj.get_from_cache(service_request, cache_name, cache_key)
        if not output:
            with open(str(self.__dir_path) + path,'r') as f:
                logging.info(str(self.__dir_path) + path)
                output = f.read()
            self.__cache_obj.update_cache(service_request, cache_name, cache_key, output, cache_dur)
        return output
