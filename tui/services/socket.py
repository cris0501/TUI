from __future__ import annotations

import json
import socket
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tui.app import TUIApp

from tui.core.events import UpdateActionsEvent, StopSocketEvent
from tui.utils import Logger


class SocketService:
    def __init__(self, app: "TUIApp", host: str, port: int) -> None:
        self._app = app
        self._host = host
        self._port = port
        self._running = False
        self._server_socket: socket.socket | None = None
        self.logger = Logger()

    def stop(self) -> None:
        self._running = False
        if self._server_socket:
            self._server_socket.close()
            self._app.post_message(StopSocketEvent())

    def run(self) -> None:
        """Blocking run — called via run_worker(..., thread=True)."""
        self._running = True
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self._host, self._port))
        self._server_socket.listen()

        while self._running:
            try:
                conn, addr = self._server_socket.accept()
                with conn:
                    data = conn.recv(4096)
                    if not data:
                        continue
                    try:
                        payload = json.loads(data.decode("utf-8"))
                        self._handle_payload(payload)
                    except Exception as e:
                        self.logger.error(f"Error procesando socket data: {e}")
            except OSError:
                break

    def _handle_payload(self, data: dict) -> None:
        actions = data.get("actions", [])
        if actions:
            actions_dict = {}
            for item in actions:
                if ":" in item:
                    key, title = item.split(":", 1)
                    actions_dict[key.strip()] = title.strip()
            self._app.post_message(UpdateActionsEvent(actions=actions_dict))

