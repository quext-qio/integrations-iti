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
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "stage.quext.io",
                "custom_domain_name" : "integrations-api-rc.stage.quext.io",
            }
        elif self == AppEnvironment.PROD:
            return {
                "hosted_zone_id" : "Z1UJRXOUMOOFQ8",
                "domain_name_alias_target" : "quext.io",
                "custom_domain_name" : "integrations-api.quext.io",
            }
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
        
    # --------------------------------------------------------------------
    # Returns account id
    def get_account_id(self) -> str:
        if self == AppEnvironment.DEV:
            return "633546161654"
        elif self == AppEnvironment.QA:
            return "633546161654"
        elif self == AppEnvironment.STAGE:
            return "323546893515"
        elif self == AppEnvironment.RC:
            return "323546893515"
        elif self == AppEnvironment.PROD:
            return "283107020475"
        else:
            raise ValueError(f"Unknown stage [get_account_id()]: {self.value}")
        
    # --------------------------------------------------------------------
    # Returns region
    def get_region(self) -> str:
        if self == AppEnvironment.DEV:
            return "us-east-1"
        elif self == AppEnvironment.QA:
            return "us-east-1"
        elif self == AppEnvironment.STAGE:
            return "us-east-1"
        elif self == AppEnvironment.RC:
            return "us-east-1"
        elif self == AppEnvironment.PROD:
            return "us-east-1"
        else:
            raise ValueError(f"Unknown stage [get_region()]: {self.value}")
        
    # --------------------------------------------------------------------
    # Returns VPC id
    def get_vpc_id(self) -> str:
        if self == AppEnvironment.DEV:
            return "vpc-02ef368fcc88d90de"
        elif self == AppEnvironment.QA:
            return "vpc-02ef368fcc88d90de"
        elif self == AppEnvironment.STAGE:
            return "vpc-026831c28ea2b50a9"
        elif self == AppEnvironment.RC:
            return "vpc-026831c28ea2b50a9" 
        elif self == AppEnvironment.PROD:
            return "vpc-0bf8136aac8201bd0" 
        else:
            raise ValueError(f"Unknown stage [get_vpc_id()]: {self.value}")
        
    # --------------------------------------------------------------------
    # Returns Security Group id
    def get_security_group_id(self) -> str:
        if self == AppEnvironment.DEV:
            return "sg-0d2c9d0899d2d8c28"
        elif self == AppEnvironment.QA:
            return "sg-0d2c9d0899d2d8c28"
        elif self == AppEnvironment.STAGE:
            return "sg-042123e18be9316f9"
        elif self == AppEnvironment.RC:
            return "sg-042123e18be9316f9" 
        elif self == AppEnvironment.PROD:
            return "sg-0999fa42519663246"
        else:
            raise ValueError(f"Unknown stage [get_security_group_id()]: {self.value}")