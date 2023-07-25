from datetime import datetime
from enum import Enum
from json import JSONEncoder
import uuid
from pydantic import BaseModel


class MessageTopic(Enum):
    RESIDENT = 1
    LOCATION = 2
    LEASE = 3


class SourceAction(Enum):
    ADD = 1
    UPDATE = 2
    DELETE = 3


class PayloadPart(Enum):
    BEGIN = 1
    TRANSIT = 2
    COMPLETE = 3


class Header(BaseModel):
    message_id: str = None
    message_version: float = 1.0
    timestamp: datetime = datetime.now()
    total_pages: int = 1
    page_no: int = 1
    payload_part: PayloadPart = PayloadPart.COMPLETE
    payload_type: str = "application/json"
    entity_type: str = None
    entity_id: str = None
    partition_key: bytes = None
    source_action: SourceAction = None
    source: str = 'SYNC_SERVICE'

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.message_id = str(uuid.uuid4())
        self.partition_key = bytes(self.entity_id,'utf-8')


class Message(BaseModel):
    header: Header = None
    payload: object = None

    def __init__(self, header: Header, payload: object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header = header
        self.payload = payload


class MessageEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, Enum):
            return o.name
        else:
            return str(o)
