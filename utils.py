import abc

UDP_MAX_SIZE = 10000
COMMANDS = ('connect:', 'disconnect:', 'end_session:', 'help:',)
HELP_TEXT = """
connect: <client_username> - connect to member
disconnect: to disconnect from member
end_session: - disconnect from server
help: - show this message
"""


class AbstractMessage(metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def get_payload(self):
        pass

    def get_username(self):
        pass

    def get_hashed_message(self):
        pass

    def get_client_id(self):
        pass


class Message(AbstractMessage):
    def __init__(self, payload, username, hashed_message, client_id=""):
        self.payload = payload
        self.username = username
        self.hashed_message = hashed_message
        self.client_id = client_id

    def get_payload(self):
        return self.payload

    def get_username(self):
        return self.username

    def get_hashed_message(self):
        return self.hashed_message

    def get_client_id(self):
        return self.client_id
