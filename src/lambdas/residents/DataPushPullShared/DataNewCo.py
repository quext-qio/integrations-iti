#from urllib.parse import urlencode
#import xml.etree.ElementTree as etree
from contextlib import closing
from Utils.Utilities import Utilities
from datetime import datetime
from ResidentsShared.Controller.QueryController import QueryController
import os, logging
from Utils.Constants.Constants import Constants

class DataNewco:
    db_object = QueryController() 

    def get_resident_data(self, ips, input):
            errors = []
            property_id = ips[Constants.PLATFORMDATA][Constants.COMMUNITYID]
            movein = input.get('moveIn', None)
            moveout = input.get('moveOut', None)
            try:
                  parameters = (property_id, property_id, )
                  with closing(self.db_object.get_db_session()) as session:
                        cursor = session.cursor()
                        # Get the property details data...
                        
                        path = Constants.QUERY_PATH + Constants.NEWCO_RESIDENTS_QUERY
                        newcoResidentsQuery = self.db_object.read_query(path, Constants.NEWCO_QUERY_CACHE, Constants.NEWCO_PROPERTY_QUERY, 0.0)

                        if movein != None:         
                              newcoResidentsQuery += "AND STR_TO_DATE(moveInDate, '%Y-%m-%d') >= %s"
                              parameters += (movein, )

                        if moveout != None:
                              newcoResidentsQuery += "AND (STR_TO_DATE(moveOutDate, '%Y-%m-%d') <= %s OR moveOutDate IS NULL) "
                              parameters += (moveout, )

                        newcoResidentsQuery += "ORDER BY unitId"
                        cursor.execute(newcoResidentsQuery, parameters)
                        rows = cursor.fetchall()
                        
                        # Fetch the column names
                        column_names = cursor.column_names
                        # Process each row and convert to dictionary
                        residents = []
                        for row in rows:
                              unit_dict = dict(zip(column_names, row))
                              residents.append(unit_dict)
                        
                        # Close the cursor and connection
                        cursor.close()

                        return errors, residents
                        
            except Exception as e:
                  logging.error(f"An error occurred while retrieving unit availability: {str(e)}")
                  return [], [{"error":f"An error occurred while retrieving unit availability: {str(e)}"}]


            