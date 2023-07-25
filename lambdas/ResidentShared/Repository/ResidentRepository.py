from pydantic import NoneBytes
from DataPushPullShared.Utilities.Entities import Person, Addres, Resident
from MessageBusShared.Model.MessageModel import SourceAction, PayloadPart, Header, Message
from MessageBusShared.Utilities.MessageBusUtils import MessageBusUtils, MessageBusConstants
from VendorShared.Model.ServiceRequest import ServiceRequest
from sqlalchemy import and_, update, literal_column

class ResidentRespository:

    def __init__(self, session, customer_id, community_id, service_request:ServiceRequest=None):
        self.service_request = service_request
        self.session = session
        self.customer_id = customer_id
        self.community_id = community_id
        self.messagebus_utils = MessageBusUtils()

    def get_person(self, external_id:Person.external_id):
        where_filter = and_(
            Person.customer_id==self.customer_id,
            Person.community_id==self.community_id,
            Person.external_id==external_id
        )
        result = self.session.query(Person).filter(where_filter).first()
        return result
    
    def save_person(self, person_obj:Person):
        self.session.add(person_obj)
        self.session.commit()
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.PERSON,
                entity_id=str(person_obj.person_id),
                source_action=SourceAction.ADD
                ),
            payload={ k:v for k,v in vars(person_obj).items() if not k.startswith('_') } 
        )
        return person_obj.person_id
    
    def update_person(self, person_id:Person.person_id, update_dict:dict):
        stmt = update(Person).where(Person.person_id==person_id).values(update_dict).returning(
            literal_column('*')
        )
        result = self.session.execute(stmt)
        self.session.commit()
        updated_row = {key:val for row in result for key,val in dict(row).items()}
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.PERSON,
                entity_id=str(person_id),
                source_action=SourceAction.UPDATE
            ),
            payload=updated_row
        )
        return result
    
    def get_resident(self, person_id:Resident.person_id):
        where_filter = and_(
            Resident.customer_id==self.customer_id,
            Resident.community_id==self.community_id,
            Resident.person_id==person_id
        )
        result = self.session.query(Resident).filter(where_filter).first()
        return result
    
    def save_resident(self, resident_obj:Resident):
        self.session.add(resident_obj)
        self.session.commit()
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.RESIDENT,
                entity_id=str(resident_obj.resident_id),
                source_action=SourceAction.ADD
                ),
            payload={ k:v for k,v in vars(resident_obj).items() if not k.startswith('_') } )
        return resident_obj.resident_id
    
    def update_resident(self, resident_id:Resident.resident_id, update_dict:dict):
        stmt = update(Resident).where(Resident.resident_id==resident_id).values(update_dict).returning(
            literal_column('*')
        )
        result = self.session.execute(stmt)
        self.session.commit()
        updated_row = {key:val for row in result for key,val in dict(row).items()}
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.RESIDENT,
                entity_id=str(resident_id),
                source_action=SourceAction.UPDATE
            ),
            payload=updated_row
        )
        return result

    def get_address(self, person_id:Addres.person_id):
        where_filter = and_(
            Addres.customer_id==self.customer_id,
            Addres.community_id==self.community_id,
            Addres.person_id==person_id
        )
        result = self.session.query(Addres).filter(where_filter).first()
        return result
    
    def save_address(self, address_obj:Addres):
        self.session.add(address_obj)
        self.session.commit()
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.ADDRESS,
                entity_id=str(address_obj.address_id),
                source_action=SourceAction.ADD                
            ),
            payload={ k:v for k,v in vars(address_obj).items() if not k.startswith('_') } 
        )
        return address_obj.address_id
    
    def update_address(self, address_id:Addres.address_id, update_dict:dict, address_obj:Addres=None):
        stmt = update(Addres).where(Addres.address_id==address_id).values(update_dict).returning(
            literal_column('*')
        )
        result = self.session.execute(stmt)
        self.session.commit()
        updated_row = {key:val for row in result for key,val in dict(row).items()}
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.ADDRESS,
                entity_id=str(address_id),
                source_action=SourceAction.UPDATE
            ),
            payload=updated_row
        )
        return result
