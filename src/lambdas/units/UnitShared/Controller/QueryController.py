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
    __dir_path = Path('/UnitShared/SQL/')

    @staticmethod
    def read_query(path, cache_name, cache_key, cache_dur):
        '''
        Read the query from SQL file and return it as a string
        '''
        output = QueryController.__cache_obj.get_from_cache(cache_name, cache_key)
        if not output:
            with open(str(QueryController.__dir_path / path), 'r') as f:
                logging.info(str(QueryController.__dir_path / path))
                output = f.read()
            QueryController.__cache_obj.update_cache(cache_name, cache_key, output, cache_dur)
        return output
    
    

    def get_db_session():
        """
        Crea y devuelve una conexión a la base de datos MySQL.
        """
        # Parámetros de conexión a la base de datos
        db_host = 'localhost'
        db_user = 'ingrid-oktara'
        db_password = 'jAVi2PUs2y1dyTJwL2twx8vsyMuh'
        db_name = 'envDev'
        
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