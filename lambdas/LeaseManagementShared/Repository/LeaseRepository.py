from DataPushPullShared.Utilities.Entities import Lease, LeaseInterval, RentableItem
from MessageBusShared.Model.MessageModel import SourceAction, PayloadPart, Header, Message
from MessageBusShared.Utilities.MessageBusUtils import MessageBusUtils, MessageBusConstants
from VendorShared.Model.ServiceRequest import ServiceRequest
from sqlalchemy import and_, update, literal_column
import time
import logging


class LeaseRespository:

    def __init__(self, session, customer_id, community_id, service_request:ServiceRequest=None):
        self.service_request = service_request
        self.session = session
        self.customer_id = customer_id
        self.community_id = community_id
        self.messagebus_utils = MessageBusUtils()

    def get_lease(self, external_id:Lease.external_id, person_id:Lease.person_id):
        where_filter = and_(
            Lease.customer_id==self.customer_id,
            Lease.community_id==self.community_id,
            Lease.external_id==external_id,
            Lease.person_id==person_id
        )
        result = self.session.query(Lease).filter(where_filter).first()
        return result
    
    def save_lease(self, lease_obj:Lease):
        self.session.add(lease_obj)
        self.session.commit()   
        start = time.time()
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.LEASE,
                entity_id=str(lease_obj.lease_id),
                source_action=SourceAction.ADD
            ),
            payload={ k:v for k,v in vars(lease_obj).items() if not k.startswith('_') } 
        )
        logging.info(f"{ time.time()- start} secs")
        return lease_obj.lease_id
    
    def update_lease(self, lease_id:Lease.lease_id, update_dict:dict):
        stmt = update(Lease).where(Lease.lease_id==lease_id).values(update_dict).returning(
            literal_column('*')
        )
        result = self.session.execute(stmt)
        self.session.commit()
        updated_row = {key:val for row in result for key,val in dict(row).items()}
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.LEASE,
                entity_id=str(lease_id),
                source_action=SourceAction.UPDATE
            ),
            payload=updated_row
        )
        return result
    
    def get_lease_interval(self, lease_id:LeaseInterval.lease_id, external_id:LeaseInterval.external_id ):
        where_filter = and_(
            LeaseInterval.customer_id==self.customer_id,
            LeaseInterval.community_id==self.community_id,
            LeaseInterval.lease_id==lease_id,
            LeaseInterval.external_id==external_id
        )
        result = self.session.query(LeaseInterval).filter(where_filter).first()
        return result
    
    def save_lease_interval(self, lease_int_obj:LeaseInterval):
        self.session.add(lease_int_obj)
        self.session.commit()
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.LEASEINTERVAL,
                entity_id=str(lease_int_obj.lease_interval_id),
                source_action=SourceAction.ADD
            ),
            payload={ k:v for k,v in vars(lease_int_obj).items() if not k.startswith('_') } 
        )
        return lease_int_obj.lease_interval_id
    
    def update_lease_interval(self, lease_interval_id:LeaseInterval.lease_interval_id, update_dict:dict):
        stmt = update(LeaseInterval).where(LeaseInterval.lease_interval_id==lease_interval_id).values(update_dict).returning(
            literal_column('*')
        )
        result = self.session.execute(stmt)
        self.session.commit()
        updated_row = {key:val for row in result for key,val in dict(row).items()}
        self.messagebus_utils.send_event(
            self.service_request,
            Header(
                entity_type=MessageBusConstants.LEASEINTERVAL,
                entity_id=str(lease_interval_id),
                source_action=SourceAction.UPDATE
            ),
            payload=updated_row
        )
        return result