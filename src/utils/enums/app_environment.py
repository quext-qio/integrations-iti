import os
from enum import Enum

class AppEnvironment(Enum):
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"
    RC = "rc"
    QA = "qa"

    # --------------------------------------------------------------------
    # Returns the custom domain config depend of the Stage
    def get_api_domain_config(self) -> dict:
        if self == AppEnvironment.DEV:
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "dev.quext.io",
                "custom_domain_name" : "integrations-api.dev.quext.io",
            }
        elif self == AppEnvironment.QA:
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "dev.quext.io",
                "custom_domain_name" : "integrations-api-qa.dev.quext.io",
            }
        elif self == AppEnvironment.STAGE:
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "stage.quext.io",
                "custom_domain_name" : "integrations-api.stage.quext.io",
            }
        elif self == AppEnvironment.RC:
            #TODO: Update this values to RC
            # return {
            #     "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
            #     "domain_name_alias_target" : "stage.quext.io",
            #     "custom_domain_name" : "integrations-api-rc.stage.quext.io",
            # }
            raise NotImplementedError("RC is not implemented yet.")
        elif self == AppEnvironment.PROD:
            # return {
            #     "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
            #     "domain_name_alias_target" : "quext.io",
            #     "custom_domain_name" : "integrations-api.quext.io",
            # }
            raise NotImplementedError("PROD is not implemented yet.")
        else:
            raise ValueError(f"Unknown stage [get_api_domain_config()]: {self.value}")


    # --------------------------------------------------------------------
    # Returns the name of the parameter store associated with the stage
    def get_parameter_store_name(self) -> str:
        if self == AppEnvironment.DEV:
            return "/dev/integrations/hub"
        elif self == AppEnvironment.QA:
            return "/dev/integrations/hub"
        elif self == AppEnvironment.STAGE:
            return "/stage/integrations/hub"
        elif self == AppEnvironment.RC:
            return "/stage/integrations/hub"
        elif self == AppEnvironment.PROD:
            return "/prod/integrations/hub"
        else:
            raise ValueError(f"Unknown stage [get_parameter_store_name()]: {self.value}")
        
    # --------------------------------------------------------------------
    # Returns name of the stage
    def get_stage_name(self) -> str:
        if self == AppEnvironment.DEV:
            return "dev"
        elif self == AppEnvironment.QA:
            return "qa"
        elif self == AppEnvironment.STAGE:
            return "stage"
        elif self == AppEnvironment.RC:
            return "rc"
        elif self == AppEnvironment.PROD:
            return "prod"
        else:
            raise ValueError(f"Unknown stage [get_stage_name()]: {self.value}")
        
    # --------------------------------------------------------------------
    # Returns stage by name
    @staticmethod
    def get_current_stage() -> "AppEnvironment":
        stage_name = os.getenv('STAGE', 'dev')
        if stage_name == "dev":
            return AppEnvironment.DEV
        elif stage_name == "qa":
            return AppEnvironment.QA
        elif stage_name == "stage":
            return AppEnvironment.STAGE
        elif stage_name == "rc":
            return AppEnvironment.RC
        elif stage_name == "prod":
            return AppEnvironment.PROD
        else:
            raise ValueError(f"Unknown stage [get_current_stage()]: {stage_name}")