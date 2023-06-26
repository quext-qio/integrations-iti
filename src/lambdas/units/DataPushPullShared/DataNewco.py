import logging
from contextlib import closing
from Utils.Constants.NewcoConstants import NewcoConstants
from UnitShared.Controller.QueryController import QueryController

class DataNewco:

    db_object = QueryController() 

    def get_unit_availability(self, ips_response, event):
        """
        Get Unit and Price information
        """
        try:
            parameters = (ips_response[NewcoConstants.PLATFORMDATA][NewcoConstants.COMMUNITYID], )
            with closing(self.db_object.get_db_session()) as session:
                cursor = session.cursor()
                # Get the property details data...
                property_data = self.get_property_data(cursor, parameters)
                # Get the apartment models data...
                models_data = self.get_models_data(cursor, parameters)
                # Get the units data
                units_data = self.get_units_data(cursor, parameters, event)

            return property_data, models_data, units_data , 200
        
        except Exception as e:
            logging.error(f"An error occurred while retrieving unit availability: {str(e)}")
            return 500, f"An error occurred while retrieving unit availability: {str(e)}"


    def get_property_data(self, cursor, parameters):
        """
        Get property information
        """
        path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_PROPERTY_QUERY
        output = self.db_object.read_query(path, NewcoConstants.NEWCO_QUERY_CACHE, NewcoConstants.NEWCO_PROPERTY_QUERY, 0.0)
        
        cursor.execute(output, parameters)
        row = cursor.fetchone()
        property_data =  dict(zip(cursor.column_names, row)) if row else {}
        print(property_data)
        return property_data

    def get_models_data(self, cursor, parameters):
        """
        Get models information
        """
        base_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_BASE_QUERY
        newco_units_base_query = self.db_object.read_query(base_query_path, NewcoConstants.NEWCO_QUERY_CACHE, NewcoConstants.NEWCO_BASE_QUERY, 0.0)
        model_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_MODELS_QUERY
        newco_units_models_query = self.db_object.read_query(model_query_path, NewcoConstants.NEWCO_QUERY_CACHE, NewcoConstants.NEWCO_MODELS_QUERY, 0.0)
        output = newco_units_base_query + newco_units_models_query
        cursor.execute(output, parameters)
        rows = cursor.fetchall()
        
        # Fetch the column names
        column_names = cursor.column_names
        
        # Process each row and convert to dictionary
        models_data = []
        for row in rows:
            model_dict = dict(zip(column_names, row))
            models_data.append(model_dict)
        return models_data

    def get_units_data(self, cursor, parameters, event):
        """
        Get units information
        """
        base_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_BASE_QUERY
        newco_units_base_query = self.db_object.read_query(base_query_path, NewcoConstants.NEWCO_QUERY_CACHE, NewcoConstants.NEWCO_BASE_QUERY, 0.0)
        units_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_UNITS_QUERY
        newco_units_units_query = self.db_object.read_query(units_query_path, NewcoConstants.NEWCO_QUERY_CACHE, NewcoConstants.NEWCO_UNITS_QUERY, 0.0)
        output = newco_units_base_query + newco_units_units_query
        if NewcoConstants.AVAILABLE in event and event[NewcoConstants.AVAILABLE]:
            output += NewcoConstants.IS_AVAILABLE
        # Consume any remaining rows
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Fetch the column names
        column_names = cursor.column_names
        print(column_names)
        # Process each row and convert to dictionary
        units_data = []
        for row in rows:
            unit_dict = dict(zip(column_names, row))
            units_data.append(unit_dict)
        
        # Close the cursor and connection
        cursor.close()
        print(units_data)
        return units_data
