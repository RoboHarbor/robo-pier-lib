import os

from roboharbor.RoboHarborClientSocket import RoboHarborClientSocket
import subprocess
import sys


class RoboRunner:
    _client : RoboHarborClientSocket = None
    def __init__(self, client):
        self._client = client


    def run(self):
        # we run a shell command and wait for it to finish
        # we want to read stdout and stderr



        process = subprocess.Popen("python ../test.py ", shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, bufsize=0, text=True)

        while True:
            line = process.stdout.readline()
            if process.poll() != None:
                break
            if line != '':
                sys.stdout.write(line)
                sys.stdout.flush()
        rc = process.poll()
        print("aaa finished with return code: " + str(rc))




