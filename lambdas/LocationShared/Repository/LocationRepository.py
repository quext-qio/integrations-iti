from DataPushPullShared.Utilities.Entities import Unit, UnitSpace
from VendorShared.Model.ServiceRequest import ServiceRequest
from sqlalchemy import and_
from MessageBusShared.Model.MessageModel import SourceAction, PayloadPart, Header, Message
from MessageBusShared.Utilities.MessageBusUtils import MessageBusUtils, MessageBusConstants
from sqlalchemy import and_, update, literal_column
import logging

class LocationRespository:

    def __init__(self, session, customer_id, community_id, service_request:ServiceRequest=None):
        self.service_request = service_request
        self.session = session
        self.customer_id = customer_id
        self.community_id = community_id
        self.messagebus_utils = MessageBusUtils()

    def get_units(self, external_id:Unit.external_id):
        where_filter = and_(
            Unit.customer_id==self.customer_id,
            Unit.community_id==self.community_id,
            Unit.external_id==external_id
        )
        result = self.session.query(Unit).filter(where_filter).first()
        return result

    def get_space_units(self, external_id:UnitSpace.external_id):
        where_filter = and_(
            UnitSpace.customer_id==self.customer_id,
            UnitSpace.community_id==self.community_id,
            UnitSpace.external_id==external_id
        )
        result = self.session.query(UnitSpace).filter(where_filter).first()
        return result

    def get_unit_by_unit_number_and_building(self, unit_number:Unit.unit_number, building:Unit.building):
        where_filter = and_(
            Unit.customer_id==self.customer_id,
            Unit.community_id==self.community_id,
            Unit.unit_number==unit_number,
            Unit.building==building
        )
        result = self.session.query(Unit).filter(where_filter).first()
        return result

    def save_unit(self, unit_obj:Unit):
        self.session.add(unit_obj)
        self.session.commit()
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.UNIT,
                entity_id=str(unit_obj.unit_id),
                source_action=SourceAction.ADD
            ), 
            payload={ k:v for k,v in vars(unit_obj).items() if not k.startswith('_') }
        )
        return unit_obj.unit_id

    def save_space_unit(self, unitspace_obj:UnitSpace):
        self.session.add(unitspace_obj)
        self.session.commit()
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.UNITSPACE,
                entity_id=str(unitspace_obj.unitspace_id),
                source_action=SourceAction.ADD
            ),
            payload={ k:v for k,v in vars(unitspace_obj).items() if not k.startswith('_') }
        )
        return unitspace_obj.unitspace_id
    
    def update_unit(self, unit_id:Unit.unit_id, update_dict:dict):
        stmt = update(Unit).where(Unit.unit_id==unit_id).values(update_dict).returning(
            literal_column('*')
        )
        result = self.session.execute(stmt)
        self.session.commit()
        updated_row = {key:val for row in result for key,val in dict(row).items()}
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.UNIT,
                entity_id=str(unit_id), 
                source_action=SourceAction.UPDATE
            ), 
            payload=updated_row
        )
        return result

    def update_space_unit(self, unitspace_id:UnitSpace.unitspace_id, update_dict:dict):
        stmt = update(UnitSpace).where(UnitSpace.unitspace_id==unitspace_id).values(update_dict).returning(
            literal_column('*')
        )
        result = self.session.execute(stmt)
        self.session.commit()
        updated_row = {key:val for row in result for key,val in dict(row).items()}
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.UNITSPACE,
                entity_id=str(unitspace_id),
                source_action=SourceAction.UPDATE
            ),
            payload=updated_row
        )
        return result