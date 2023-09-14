import os
from config.config import config

def singleton(class_):
    """Generic method to use as decorator for create unique instance of specific class
    Args:
        class_ (class): type of class
    Returns:
        class: new class if not exist else same value of current class
    """
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class EngrainJob():
    """This class is a Singleton
       It will manage when Engrain Job should execute
       Only in production env will start by default
    """
    def __init__(self):
        """Init method to initialize the first values
        """
        self.run = True if config['current_env'] == 'prod' else False
        self.job_last_run = ""
        self.job_currently_executing = False
        self.job_schedule = "Not available"

    def is_running(self):
        """Method to show current state
        Returns:
            bool: True if job has permisions to run else False
        """
        return self.run

    def stop(self):
        """Method to disallow the job execute
        Returns:
            bool: current state (False)
        """
        self.run = False
        return self.is_running()

    def start(self):
        """Method to allow the job execute
        Returns:
            bool: current state (True)
        """
        self.run = True
        return self.is_running()

    def last_execution(self, time):
        """Method to save information about last execution
        Args:
            time (str): date and time of last execution
        Returns:
           str : date and time saved
        """
        self.job_last_run = time
        return self.job_last_run

    def currently_executing(self, status):
        """Method to manage if job is currently running
        Args:
            status (bool): True if running else False
        Returns:
            bool: information saved
        """
        self.job_currently_executing = status
        return self.job_currently_executing

    def get_status(self):
        """Method to return information about Job status
        Returns:
            dict: current status of job
        """
        data = {
            "job_enabled": f"{self.run}",
            "job_schedule": f"{self.job_schedule}",
            "job_last_run": f"{self.job_last_run}",
            "job_currently_executing": f"{self.job_currently_executing}",
        },
        return data