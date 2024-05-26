import asyncio
import json
import time
from abc import abstractmethod

import websockets

from robo_pier_lib.roboharbor.WebsocketThread import WebsocketThread

class IRoboHarborClientSocketCallback:
    @abstractmethod
    def on_registered(self, robot):
        pass

    @abstractmethod
    def on_robot_changed(self, robot):
        pass

    @abstractmethod
    def validate_robot(self, robot):
        pass

class RoboHarborClientSocket(WebsocketThread):
    _robo_id = None
    _harbor = None
    _secret = None
    _received_messages = []
    _callback : IRoboHarborClientSocketCallback = None

    def __init__(self, harbor, secret, robo_id, pod_name, only_test_checkout=False):
        if harbor.startswith('http'):
            harbor = harbor.replace('http', 'ws')
        elif harbor.startswith('https'):
            harbor = harbor.replace('https', 'wss')
        else:
            harbor = f'ws://{harbor}'
        super().__init__(harbor, None)
        self.received_message = False

        self._pod_name = pod_name
        self._harbor = harbor
        self._secret = secret
        self._robo_id = robo_id
        self._only_test_checkout = only_test_checkout

    def random_response_id(self):
        # random response id
        return str(time.time())

    def answer(self, response_id, response):
        r = response
        r['responseId'] = response_id
        r['isResponse'] = True
        self.send(json.dumps(r))

    def _message_received(self, response_id):
        for msg in self._received_messages:
            if 'responseId' in msg and msg['responseId'] == response_id and 'response' in msg and msg['response'] is not None:
                return msg['response']
        return False

    async def _wait_till_response(self, response_id):
        tick = asyncio.get_event_loop().time()
        while not self._message_received(response_id):
            if asyncio.get_event_loop().time() - tick > 30:
                raise TimeoutError('Timed out waiting for message')
            await asyncio.sleep(0.5)
        return self._message_received(response_id)

    async def sendMessageAndAwaitResponse(self, message_type, message):
        response_id = self.random_response_id()
        msg = {'type': message_type, 'responseId': response_id, 'message': message}
        self.send(json.dumps(msg))
        self._received_messages.append(msg)
        resp = await self._wait_till_response(response_id)
        if 'error' in resp:
            raise Exception(resp['error'])
        return resp


    async def _on_registered(self):
        try:
            # get all robot details
            if not self._only_test_checkout:
                self.robot = await self.sendMessageAndAwaitResponse("getRobotDetails", {"roboId": self._robo_id})
                self._callback.on_registered(self.robot)

        except Exception as e:
            print(e)
            self.robot = None

    def _validate_robot(self, msg):
        self.robot = msg['robot']
        try:
            self._callback.validate_robot(self.robot)
            self.answer(msg['responseId'], {'success': True})
        except Exception as e:
            self.answer(msg['responseId'], {'success': False, 'error': str(e)})
            return

    def registerCallback(self, callback: IRoboHarborClientSocketCallback):
        self._callback = callback

    async def handle_message(self, message: str):
        msg = json.loads(message)
        print(msg)

        if 'isResponse' in msg and msg['isResponse']:
            for r in self._received_messages:
                if 'responseId' in r and r['responseId'] == msg['responseId']:
                    r['response'] = msg
                    return

        if 'type' in msg and msg['type'] == 'initMessage':
            self.send(json.dumps({'type': 'REGISTER_ROBOT', 'robotId': self._robo_id, ''
                                  'secret': self._secret, 'socketId': self._pod_name,
                                  'pod': self._pod_name}))
        if 'type' in msg and msg['type'] == 'registered':
            await self._on_registered()
        if 'type' in msg and msg['type'] == 'getRobotDetails':
            self._callback.on_robot_changed(msg['robot'])
        if 'type' in msg and msg['type'] == 'validateRobotDetails':
            self._validate_robot(msg)