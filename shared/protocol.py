"""
Protocole de communication entre le serveur et les clients
"""
import json

class Protocol:
    # Types de messages
    REGISTER = "REGISTER"
    REGISTER_OK = "REGISTER_OK"
    LIST_PLAYERS = "LIST_PLAYERS"
    CHALLENGE = "CHALLENGE"
    CHALLENGE_RECEIVED = "CHALLENGE_RECEIVED"
    CHALLENGE_ACCEPTED = "CHALLENGE_ACCEPTED"
    CHALLENGE_REFUSED = "CHALLENGE_REFUSED"
    GAME_START = "GAME_START"
    PLAY_MOVE = "PLAY_MOVE"
    GAME_UPDATE = "GAME_UPDATE"
    GAME_OVER = "GAME_OVER"
    DISCONNECT = "DISCONNECT"
    ERROR = "ERROR"
    
    @staticmethod
    def encode(msg_type, data=None):
        """Encode un message en JSON"""
        message = {"type": msg_type, "data": data}
        return json.dumps(message).encode('utf-8') + b'\n'
    
    @staticmethod
    def decode(raw_message):
        """Décode un message JSON"""
        try:
            message = json.loads(raw_message.decode('utf-8'))
            return message.get("type"), message.get("data")
        except:
            return None, None