from abc import ABC, abstractmethod


class ProcessCallback(ABC):
    def __init__(self, runner):
        self._runner = runner

   # here is the run method that will be called by the robo
    @abstractmethod
    def run(self):
        pass

    def get_config_value(self, v):
        return None

