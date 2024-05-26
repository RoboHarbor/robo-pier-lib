# this script starts the robo
# it is the entry point of the application

import sys
import os
import time
from threading import Thread

from robo_pier_lib.roboharbor.RoboHarborClientSocket import RoboHarborClientSocket
from robo_pier_lib.roboharbor.RoboRunner import RoboRunner

def startRobot(process_cb):
    # validate all the environment variables
    # if any of the environment variables are not set, the application will not start
    # ROBO_HARBOR is the harbor location of the robo (url with port)
    # ROBO_SECRET is the secret of the robo
    # ROBO_ID is the id of the robo
    only_test_checkout = False
    if 'ROBO_HARBOR' not in os.environ:
        print('ROBO_HARBOR environment variable is not set')
        sys.exit(1)
    if 'ROBO_SECRET' not in os.environ:
        print('ROBO_SECRET environment variable is not set')
        sys.exit(1)
    if 'ROBO_ID' not in os.environ:
        print('ROBO_ID environment variable is not set')
        sys.exit(1)
    if 'POD_NAME' not in os.environ:
        print('POD_NAME environment variable is not set')
        sys.exit(1)
    if 'ONLY_TEST_CHECKOUT' in os.environ:
        only_test_checkout = True

    # start
    client = RoboHarborClientSocket(os.environ['ROBO_HARBOR'],
                                    os.environ['ROBO_SECRET'],
                                    os.environ['ROBO_ID'],
                                    os.environ['POD_NAME'],
                                    only_test_checkout=only_test_checkout)
    thread = Thread(target=client.run)
    thread.start()

    time.sleep(1)

    # start the robo
    robo = RoboRunner(client, process_cb,
                      only_test_checkout=only_test_checkout)

    # run the robo
    return robo
