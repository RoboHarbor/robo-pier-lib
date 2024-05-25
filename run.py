# this script starts the robo
# it is the entry point of the application

import sys
import os

from roboharbor.RoboHarborClientSocket import RoboHarborClientSocket
from roboharbor.RoboRunner import RoboRunner

# validate all the environment variables
# if any of the environment variables are not set, the application will not start
# ROBO_HARBOR is the harbor location of the robo (url with port)
# ROBO_SECRET is the secret of the robo
# ROBO_ID is the id of the robo

if 'ROBO_HARBOR' not in os.environ:
    print('ROBO_HARBOR environment variable is not set')
    sys.exit(1)
if 'ROBO_SECRET' not in os.environ:
    print('ROBO_SECRET environment variable is not set')
    sys.exit(1)
if 'ROBO_ID' not in os.environ:
    print('ROBO_ID environment variable is not set')
    sys.exit(1)

# start
client = RoboHarborClientSocket(os.environ['ROBO_HARBOR'], os.environ['ROBO_SECRET'], os.environ['ROBO_ID'])

# start the robo
robo = RoboRunner(client)

# run the robo
robo.run()
