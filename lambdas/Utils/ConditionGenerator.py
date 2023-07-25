from VendorShared.Utilities.VendorConstants import PartnerConditionConstants


class ConditionGenerator():
    """
    This class used to generate the condition based on the partner 
    for qunitvisible in the units.
    """
    @staticmethod
    def generate_condition(status: str, operator: str, source: str):
        condition = f"True if \'{status}\' {operator} {getattr(PartnerConditionConstants, source)} else False"
        return eval(condition)

