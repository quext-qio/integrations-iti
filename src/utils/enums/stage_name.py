from enum import Enum

class StageName(Enum):
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"
    RC = "rc"
    QA = "qa"

    # Returns the custom domain config depend of the Stage
    def get_api_domain_config(self):
        if self == StageName.DEV:
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "dev.quext.io",
                "custom_domain_name" : "integrations-api.dev.quext.io",
            }
        elif self == StageName.QA:
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "dev.quext.io",
                "custom_domain_name" : "integrations-api-qa.dev.quext.io",
            }
        elif self == StageName.STAGE:
            raise Exception("Custom Domain Name not implemented for 'stage' yet") 
        elif self == StageName.RC:
            raise Exception("Custom Domain Name not implemented for 'rc' yet")
        elif self == StageName.PROD:
            raise Exception("Custom Domain Name not implemented for 'prod' yet")
        else:
            raise ValueError(f"Unknown stage: {self.value}")
        
    # Returns the API Key depending of the Stage
    def get_api_key(self):
        if self == StageName.DEV:
            return "dev-api-key"
        elif self == StageName.QA:
            return "qa-api-key"
        elif self == StageName.STAGE:
            return "stage-api-key"
        elif self == StageName.RC:
            return "rc-api-key"
        elif self == StageName.PROD:
            return "prod-api-key"
        else:
            raise ValueError(f"Unknown stage: {self.value}")
