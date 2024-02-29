import os


class EnvReader:
    instance = None

    def __init__(self):
        self.ips_host = os.environ["IPS_HOST"]
        self.api_key = os.environ['API_KEY']
        self.consumer_id = os.environ['CONSUMER_ID']
        self.current_env = os.environ['CURRENT_ENV']

    @staticmethod
    def get_instance():
        if EnvReader.instance is None:
            EnvReader.instance = EnvReader()
        return EnvReader.instance

    def get_ips_envs(self):
        environment_variables = {'ips_host': self.ips_host,
                                 'api_key': self.api_key,
                                 'consumer_id': self.consumer_id}

        return environment_variables

