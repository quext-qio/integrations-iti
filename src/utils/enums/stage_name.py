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
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "stage.quext.io",
                "custom_domain_name" : "integrations-api.stage.quext.io",
            }
        elif self == StageName.RC:
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "stage.quext.io",
                "custom_domain_name" : "integrations-api-rc.stage.quext.io",
            }
        elif self == StageName.PROD:
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "quext.io",
                "custom_domain_name" : "integrations-api.quext.io",
            }
        else:
            raise ValueError(f"Unknown stage: {self.value}")
