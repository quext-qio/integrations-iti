from enum import Enum

class StageName(Enum):
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"
    RC = "rc"
    QA = "qa"

    def get_api_domain_config(self):
        if self == StageName.DEV:
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "integrations-api.dev.quext.io",
                "custom_domain_name" : "dev.quext.io",
            }
        elif self == StageName.QA:
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "integrations-api-qa.dev.quext.io",
                "custom_domain_name" : "dev.quext.io",
            }
        elif self == StageName.STAGE:
            raise Exception("Custom Domain Name not implemented for 'stage' yet") 
        elif self == StageName.RC:
            raise Exception("Custom Domain Name not implemented for 'rc' yet")
        elif self == StageName.PROD:
            raise Exception("Custom Domain Name not implemented for 'prod' yet")
        else:
            raise ValueError(f"Unknown stage: {self.value}")