from enum import Enum

# TODO: Validate the values in this enum as same of IPS service names
class ServiceType(Enum):
    ENTRATA = "entrata"
    FUNNEL = "funnel"
    REALPAGE = "realpage"
    RESMAN = "resman"
    YARDI = "yardi"
    REALPAGEILM = "realpageilm"