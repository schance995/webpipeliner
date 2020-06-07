class User():
    def __init__(self):
        self._auth = False
        self._name = ''

    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, value):
        self._auth = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
