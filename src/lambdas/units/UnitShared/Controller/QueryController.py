import logging
from pathlib import Path
from UnitShared.Controller.CacheManager import CacheManager
import mysql.connector

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
        # Parámetros de conexión a la base de datos
        db_host = 'newco-prod-readonly2.czlebpbzjy34.us-east-2.rds.amazonaws.com'
        db_user = 'zato'
        db_password = 'TyN2!m-db8D7-yua49yycL8h'
        db_name = 'forge'
        
        # Intenta establecer la conexión a la base de datos
        try:
            connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
            
            return connection
        
        except mysql.connector.Error as error:

            print(f"Error al conectar a la base de datos: {error}")
            return None
        except Exception as e:
          
            print(f"Error general: {e}")
            return None