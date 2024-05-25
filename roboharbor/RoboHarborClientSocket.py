
class RoboHarborClientSocket:
    _robo_id = None
    _harbor = None
    _secret = None

    def __init__(self, harbor, secret, robo_id):
        self._harbor = harbor
        self._secret = secret
        self._robo_id = robo_id