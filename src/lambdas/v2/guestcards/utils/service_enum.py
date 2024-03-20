from enum import Enum

# Validate the values in this enum are the same of IPS service names
class ServiceType(Enum):
    ENTRATA = "entrata"
    FUNNEL = "funnel"
    REALPAGE = "realpage"
    RESMAN = "resman"
    YARDI = "yardi"
    SPHEREXX = "spherexx"
    MRI = "mri"

class PartnerSystem(Enum):
    REALPAGE_ILM = "ilm"
    REALPAGE_L2L = "l2l"
    REALPAGE_ONESITE = "onesite"