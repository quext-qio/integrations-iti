import logging
from contextlib import closing
from Utils.Constants.NewcoConstants import NewcoConstants
from UnitShared.Controller.QueryController import QueryController

class DataNewco:

    db_object = QueryController() 

    def get_unit_availability(self, ips_response):
        """
        Get Unit and Price information
        """
        try:
            parameters = {NewcoConstants.NEWCO_PROPERTY_ID: ips_response[NewcoConstants.PLATFORMDATA][NewcoConstants.COMMUNITYID]}

            with closing(self.db_object.get_db_session()) as session:
                # Get the property details data...
                property_data = self.get_property_data(session, parameters)
                # Get the apartment models data...
                models_data = self.get_models_data(session, parameters)
                # Get the units data
                units_data = self.get_units_data(session, parameters)

            return property_data, models_data, units_data ,200
        
        except Exception as e:
            logging.error(f"An error occurred while retrieving unit availability: {str(e)}")
            return 500, f"An error occurred while retrieving unit availability: {str(e)}"


    def get_property_data(self, session, parameters):
        """
        Get property information
        """
        path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_PROPERTY_QUERY
        output = self.db_object.read_query(path, NewcoConstants.NEWCO_QUERY_CACHE, NewcoConstants.NEWCO_PROPERTY_QUERY, 0.0)
        result = session.execute(output, parameters)
        property_data = {}
        for row in result:
            property_data = dict(row.items())
        return property_data

    def get_models_data(self, session, parameters):
        """
        Get models information
        """
        base_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_BASE_QUERY
        newco_units_base_query = self.db_object.read_query(base_query_path, NewcoConstants.NEWCO_QUERY_CACHE, NewcoConstants.NEWCO_BASE_QUERY, 0.0)
        model_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_MODELS_QUERY
        newco_units_models_query = self.db_object.read_query(model_query_path, NewcoConstants.NEWCO_QUERY_CACHE, NewcoConstants.NEWCO_MODELS_QUERY, 0.0)
        output = newco_units_base_query + newco_units_models_query
        result = session.execute(output, parameters)
        models_data = []
        for row in result:
            model_data = dict(row.items())
            models_data.append(model_data)
        return models_data

    def get_units_data(self, session, parameters):
        """
        Get units information
        """
        base_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_BASE_QUERY
        newco_units_base_query = self.db_object.read_query(base_query_path, NewcoConstants.NEWCO_QUERY_CACHE, NewcoConstants.NEWCO_BASE_QUERY, 0.0)
        units_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_UNITS_QUERY
        newco_units_units_query = self.db_object.read_query(units_query_path, NewcoConstants.NEWCO_QUERY_CACHE, NewcoConstants.NEWCO_UNITS_QUERY, 0.0)
        output = newco_units_base_query + newco_units_units_query
        if NewcoConstants.AVAILABLE in self.get_request_payload() and self.get_request_payload()[NewcoConstants.AVAILABLE]:
            output += NewcoConstants.IS_AVAILABLE
        result = session.execute(output, parameters)
        units_data = []
        for row in result:
            unit_data = dict(row.items())
            units_data.append(unit_data)
        return units_data
