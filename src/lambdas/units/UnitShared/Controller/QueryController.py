import logging
from pathlib import Path
from UnitShared.Controller.CacheManager import CacheManager
import mysql.connector
from Utils.Config.Config import config

class QueryController:
    '''
    Functions to read query from file
    '''
    __cache_obj = CacheManager()
    '''
    __dir_path is the path to the directory where the SQL files are located.
    Modify it according to your AWS Lambda environment.
    '''

    @staticmethod
    def read_query(path, cache_name, cache_key, cache_dur):
        '''
        Read the query from SQL file and return it as a string
        '''
        output = QueryController.__cache_obj.get_from_cache(cache_name, cache_key)
        if not output:
            with open(str(path), 'r') as f:
                logging.info(str(path))
                output = f.read()
            QueryController.__cache_obj.update_cache(cache_name, cache_key, output, cache_dur)
        return output
    
    

    def get_db_session(self):
        """
        Crea y devuelve una conexión a la base de datos MySQL.
        """
        # Database connection parameters
        db_host = config['Newco_host']
        db_user = config['Newco_db_user']
        db_password = config['Newco_password']
        db_name = config['Newco_db_name']
        
        # Try to connect to the database
        try:
            connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
            
            return connection
        
        except mysql.connector.Error as error:

            print(f"Error trying to connect to NewCo DB: {error}")
            return None
        except Exception as e:
          
            print(f"Error general: {e}")
            return None