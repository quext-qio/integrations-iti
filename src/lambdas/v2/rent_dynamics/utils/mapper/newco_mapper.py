import json
from decimal import Decimal
from contextlib import closing
from controller.query_controller import QueryController
from datetime import date, datetime


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError

class NewCoMapper:
    global db_object 
    db_object = QueryController() 

    @staticmethod
    def get_chargeCodes_RentDynamics(params: dict):
        try:
            with closing(db_object.get_db_session()) as session:
                cursor = session.cursor(dictionary=True)
                path = "newco_queries/get_charge_codes.sql"
                output = db_object.read_query(path, "rent_dynamics", "charge_codes", 0.0)
                cursor.execute(output, params)
                
                # Fetch all rows
                result = cursor.fetchall()
                for item in result:
                    decimal_value = item['amount']
                    item['amount'] = float(decimal_value)
                
                # TODO: Map the data to the expected format

                return True, result
        
        except Exception as e:
            print(f"An error occurred while retrieving data of get charge codes from the database: {str(e)}")
            return False, [{"message":f"An error occurred while retrieving data of get charge codes from the database: {str(e)}"}]

    @staticmethod
    def get_customer_events_RentDynamics(params: dict):
        try:
            with closing(db_object.get_db_session()) as session:
                cursor = session.cursor(dictionary=True)
                path = "newco_queries/get_customer_events.sql"
                output = db_object.read_query(path, "rent_dynamics", "customer_events", 0.0)
                cursor.execute(output, params)
                
                # Fetch all rows
                result = cursor.fetchall()    
                for item in result:
                    # Convert dates to string (created_at)
                    item_created_at = item['created_at']
                    if item_created_at is not None:
                        item['created_at'] = item_created_at.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Convert dates to string (date)
                    item_date = item['date']
                    if item_date is not None:
                        item['date'] = item_date.strftime("%Y-%m-%d %H:%M:%S")


                # TODO: Map the data to the expected format

                return True, result
        
        except Exception as e:
            print(f"An error occurred while retrieving data of get get customer events from the database: {str(e)}")
            return False, [{"message":f"An error occurred while retrieving data of get get customer events from the database: {str(e)}"}]
        
    
    @staticmethod
    def get_residents_RentDynamics(params: dict):
        try:
            with closing(db_object.get_db_session()) as session:
                cursor = session.cursor(dictionary=True)
                path = "newco_queries/get_residents.sql"
                output = db_object.read_query(path, "rent_dynamics", "get_residents", 0.0)
                cursor.execute(output, params)
                
                # Fetch all rows
                result = cursor.fetchall()    

                for item in result:
                    for key, value in item.items():
                        if isinstance(value, (date, datetime)):
                            item[key] = value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value.strftime("%Y-%m-%d")
                    
                # TODO: Map the data to the expected format
                return True, result
        
        except Exception as e:
            print(f"An error occurred while retrieving data of get Residents from the database: {str(e)}")
            return False, [{"message":f"An error occurred while retrieving data of get residents from the database: {str(e)}"}]
        
    @staticmethod
    def get_units_and_floorplans_RentDynamics(params: dict):
        try:
            with closing(db_object.get_db_session()) as session:
                cursor = session.cursor(dictionary=True)
                path = "newco_queries/get_units_and_floorplans.sql"
                output = db_object.read_query(path, "rent_dynamics", "get_units_and_floorplans", 0.0)
                cursor.execute(output, params)
                
                # Fetch all rows
                result = cursor.fetchall()    
               
                for item in result:
                    for key, value in item.items():
                        if isinstance(value, (date, datetime)):
                            item[key] = value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value.strftime("%Y-%m-%d")
                    
                # TODO: Map the data to the expected format
                return True, result
        
        except Exception as e:
            print(f"An error occurred while retrieving data of get Units and floorplans from the database: {str(e)}")
            return False, [{"message":f"An error occurred while retrieving data of get Units and floorplans from the database: {str(e)}"}]
        

    @staticmethod
    def get_transactions_RentDynamics(params: dict):
        try:
            with closing(db_object.get_db_session()) as session:
                cursor = session.cursor(dictionary=True)
                path = "newco_queries/get_transactions.sql"
                output = db_object.read_query(path, "rent_dynamics", "get_transactions", 0.0)
                cursor.execute(output, params)
                
                # Fetch all rows
                result = cursor.fetchall()    
                for item in result:
                    decimal_value = item['amount']
                    item['amount'] = float(decimal_value)
                    for key, value in item.items():
                        if isinstance(value, (date, datetime)):
                            item[key] = value.strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else value.strftime("%Y-%m-%d")
                    
                # TODO: Map the data to the expected format
                return True, result
        
        except Exception as e:
            print(f"An error occurred while retrieving data of get transactions from the database: {str(e)}")
            return False, [{"message":f"An error occurred while retrieving data of get transactions from the database: {str(e)}"}]
        

        

    