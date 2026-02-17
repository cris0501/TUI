import socket
import json
import threading
from tui.core.context import Context
from tui.core.events import (UpdateActionsEvent, LogAppendEvent)
from tui.utils import Logger

class SocketService:
    def __init__(self, ctx: Context, host: str = '127.0.0.1', port: int = 5000):
        self._ctx = ctx
        self._host = host
        self._port = port
        self._running = False
        self._thread: threading.Thread | None = None
        self._server_socket = None
        self.logger = Logger()

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._server_socket:
            self._server_socket.close()

    def _run(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self._host, self._port))
        self._server_socket.listen()
        
        while self._running:
            conn, addr = self._server_socket.accept()
            with conn:
                data = conn.recv(4096)
                if not data:
                    continue
                
                try:
                    payload = json.loads(data.decode('utf-8'))
                    self._handle_payload(payload)
                except Exception as e:
                    print(f"Error procesando socket data: {e}")

    def _handle_payload(self, data: dict):
        event_type = data.get('event_type')
        payload = data.get('payload', [])
        actions = data.get('actions', [])

        if event_type == 'update_actions':
            # Hateoas: ["F1:Save", "F2:Delete", "ESC:Back"]
            actions_dict = {}
            for item in actions:
                if ":" in item:
                    key, title = item.split(":", 1)
                    actions_dict[key.strip()] = title.strip()

            self._ctx.post(UpdateActionsEvent(actions=actions_dict))
