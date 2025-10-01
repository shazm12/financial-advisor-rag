from typing import Dict
import uuid

from app.utils.decorators.singleton import singleton
from app.utils.retreiver import Retreiver


@singleton
class SessionManager:
    def __init__(self):
        self.sessions = {}

    def create_sesssion(self, session_id: str = None):
        session_id = session_id or str(uuid.uuid4())
        self.sessions[session_id] = {}
        return session_id

    def get_session_retreivers_by_id(self, session_id: str):
        return self.sessions[session_id]

    def get_all_sessions(self):
        return self.sessions.items()

    def session_exists(self, session_id: str):
        return session_id in self.sessions

    def add_retreivers_to_session(
        self, session_id: str, retreivers: Dict[str, Retreiver]
    ):
        self.sessions[session_id] = retreivers

    def delete_session_by_id(self, session_id: str):
        del self.sessions[session_id]
