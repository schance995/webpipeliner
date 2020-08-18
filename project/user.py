class User():
    def __init__(self):
        self._auth = False
        self._name = ''
        self._basics = False
        self._details = False

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

    @property
    def basics(self):
        return self._basics

    @basics.setter
    def basics(self, value):
        self._basics = value

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value
