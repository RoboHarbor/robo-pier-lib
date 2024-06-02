import os
import time
import json
import orjson
from robo_pier_lib.ProcessCallback import ProcessCallback
from robo_pier_lib.roboharbor.RoboHarborClientSocket import RoboHarborClientSocket, IRoboHarborClientSocketCallback
import subprocess
import logging
import sys
import glob, os.path


class RoboRunner(IRoboHarborClientSocketCallback):
    _client : RoboHarborClientSocket = None
    _app_directory: str = "app"

    def __init__(self, client, process_c, only_test_checkout=False):
        self._client = client
        self._only_test_checkout = only_test_checkout
        self._process_cb = process_c
        self._app_directory = "app"
        self._client.registerCallback(self)

    async def runTheProcess(self):

        await self.sendRobotStartInfo()

        d = self._process_cb(self)
        await d.run()
        return d

    async def sendRobotStartInfo(self):
        await self._client.sendMessageWithoutResponse("robotStartInfo", {
            "gitCommit": self.getLocalGitCommit(),
            "robotContent": self.getRobotFileContent(),
            "gitRemoteCommit": self.getRemoteGitCommit(self.robot),
        })

    async def on_registered(self, robot):
        self.robot = robot
        if not self._only_test_checkout:
            try:
                # lets checkout the source
                try:
                    self.fetchSource()
                except Exception as e:
                    raise e

                # run the process
                await self.runTheProcess()
            except Exception as global_exception:
                print("Error: ", str(global_exception))
                sys.exit(1)
            sys.exit(0)


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
        self.removeAppFiles()
        subprocess.run(f"mkdir "+self._app_directory, shell=True, check=True)

        ret = None
        # check if there is a ssh key set
        if "credentials" in source:
            credentials = source["credentials"]
            if "sshKey" in credentials:
                ssh = credentials["sshKey"]
                if len(ssh) > 30:
                    try:
                        random_ssh_key_file = "/tmp/ssh_key"+str(time.time())
                        # write with utf8 encoding
                        with open(random_ssh_key_file, "w", encoding="utf-8") as f:
                            f.write(ssh)
                        subprocess.run(f"chmod 600 "+random_ssh_key_file, shell=True, check=True)
                        # checkout with GIT_SSH_COMMAND=\"ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no\"

                        ret = subprocess.run(f"ssh-agent bash -c 'ssh-add "+random_ssh_key_file+"; GIT_SSH_COMMAND=\"ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no\" "
                                                                                                "git clone --branch " + branch + " "
                                                                                                + url + " "
                                                                                                "" + self._app_directory + "'",
                                             shell=True, check=True
                                             )

                    except Exception as e:
                        raise e
                    finally:
                        os.remove(random_ssh_key_file)


        if ret is None:
            # checkout
            ret = subprocess.run(f"git clone --branch {branch} {url} "+self._app_directory, shell=True, check=True,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.STDOUT
                             )
        if ret.returncode == 0:
            print(f"git clone --branch {branch} {url} app was successful")

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

    def removeAppFiles(self):
        # remove the app directory
        try:
            ret = subprocess.run("rm -rf " + self._app_directory, shell=True, check=True)
        except Exception as e:
            pass

    def getRobotFileContent(self):
        try:
            # check if the file ".robot" exists and return its content
            files = glob.glob(self._app_directory + "/.robot")
            if len(files) == 0:
                return None
            with open(files[0], "r") as f:
                j = f.read()
                return orjson.loads(j)

        except Exception as e:
            raise e

        return None

    def getAppFiles(self):
        # get all the files in the app directory
        try:
            files = os.listdir(self._app_directory)
            return files
        except Exception as e:
            return []

    def getRemoteGitCommit(self, robot):
        git_commit_remote = None
        try:
            # get the remote newest git commit
            ret = subprocess.run(
                "cd " + self._app_directory + " && git ls-remote origin -h refs/heads/" + robot["source"]["branch"],
                shell=True, check=True, stdout=subprocess.PIPE)
            git_commit_remote = ret.stdout.decode('utf-8').split("\t")[0].replace("\n", "").replace("\r", "").replace("\t", "")
        except Exception as e:
            logging.error("Error in getting remote git commit: %s", e)
        return git_commit_remote

    def getLocalGitCommit(self):
        try:
            ret = subprocess.run("cd "+self._app_directory+" && git rev-parse HEAD", shell=True, check=True, stdout=subprocess.PIPE)
            return ret.stdout.decode('utf-8').replace("\n", "").replace("\r", "").replace("\t", "")
        except Exception as e:
            return None

    def validate_robot(self, robot):
        self.robot = robot
        try:
            data = {}
            self.fetchSource()
            files = self.getAppFiles()
            data['files'] = files
            robotContent = None
            try:
                robotContent = self.getRobotFileContent()
            except Exception as e:
                data['robotContentError'] = str(e)

            data['robotContent'] = robotContent
            data['git_commit'] = self.getLocalGitCommit()
            # get the remote git commit
            data['git_commit_remote'] = self.getRemoteGitCommit(robot)


            return data
        except Exception as e:
            raise e
        finally:
            self.removeAppFiles()

    #############################
    # IRoboHarborClientSocketCallback
    #############################

    def get_config_value(self, v):
        if self.robot is None:
            return None
        if 'image' not in self.robot:
            return None
        if 'config' not in self.robot['image']:
            return None
        if 'attributes' not in self.robot['image']['config']:
            return None
        if v not in self.robot['image']['config']['attributes']:
            return None


        if v not in self.robot['image']['config']['attributes']:
            return None

        return self.robot['image']['config']['attributes'][v]

    def get_app_dir(self):
        return self._app_directory









