from abc import ABC, abstractmethod


class ProcessCallback(ABC):
    def __init__(self, runner):
        self._runner = runner

   # here is the run method that will be called by the robo
    @abstractmethod
    async def run(self):
        pass

    def get_config_value(self, v):
        return self._runner.get_config_value(v)

    def get_app_dir(self):
        return self._runner.get_app_dir()
