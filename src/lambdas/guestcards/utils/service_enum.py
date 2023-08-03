from enum import Enum

# Validate the values in this enum are the same of IPS service names
class ServiceType(Enum):
    ENTRATA = "entrata"
    FUNNEL = "funnel"
    REALPAGE = "realpage"
    RESMAN = "resman"
    YARDI = "yardi"
    REALPAGEILM = "realpage_ilm"
    REALPAGEL2L = "realpage_l2l"
