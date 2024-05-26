import os

from robo_pier_lib.ProcessCallback import ProcessCallback
from robo_pier_lib.roboharbor.RoboHarborClientSocket import RoboHarborClientSocket, IRoboHarborClientSocketCallback
import subprocess
import sys


class RoboRunner(IRoboHarborClientSocketCallback):
    _client : RoboHarborClientSocket = None
    def __init__(self, client, process_c, only_test_checkout=False):
        self._client = client
        self._only_test_checkout = only_test_checkout
        self._process_cb = process_c
        self._client.registerCallback(self)

    def runTheProcess(self):
        d = self._process_cb(self)
        d.run()
        return d

    def on_registered(self, robot):
        print("on_registered", robot)
        self.robot = robot
        if not self._only_test_checkout:
            self.runTheProcess()


    def on_robot_changed(self, robot):
        self.robot = robot

    def git_clone(self, source):
        print("git_clone")
        if 'url' not in source:
            raise Exception("url not found in source")
        if 'branch' not in source:
            raise Exception("branch not found in source")
        url = source['url']
        branch = source['branch']
        ret = subprocess.run(f"rm -rf app", shell=True, check=True)
        ret = subprocess.run(f"mkdir app", shell=True, check=True)
        # checkout
        ret = subprocess.run(f"git clone --branch {branch} {url} app", shell=True, check=True,
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.STDOUT
                             )

    def fetchSource(self):
        print("fetchSource")
        if self.robot is None:
            raise Exception("robot is None")
        if 'source' not in self.robot:
            raise Exception("source not found in robot")
        source = self.robot['source']
        if 'type' not in source:
            raise Exception("type not found in source")
        if source['type'] == 'git':
            self.git_clone(source)
        else:
            raise Exception("unknown source type")



    def validate_robot(self, robot):
        print("validate_robot")
        self.robot = robot
        try:
            self.fetchSource()
        except Exception as e:
            raise e











