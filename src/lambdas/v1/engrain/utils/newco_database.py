from config.config import config
import mysql.connector

class NewcoDatabase:
    @staticmethod
    def get_db_session() -> mysql.connector.connection.MySQLConnection:
        """
        Creates and returns a connection to the MySQL database.
        
        Returns:
            A MySQL database connection object.
        
        Raises:
            Exception: If there is an error trying to connect to the NewCo DB.
            Exception: If there is a general error.
        """
        try:
            # Database connection parameters
            db_host = config['newco_host']
            db_user = config['newco_db_user']
            db_password = config['newco_password']
            db_name = config['newco_db_name']
            
            # Try to connect to the database
            connection = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
            
            return connection
        
        except mysql.connector.Error as error:
            raise Exception(f"Error trying to connect to NewCo DB: {error}")
        
        except Exception as e:
            raise Exception(f"General error: {e}")
