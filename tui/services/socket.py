from __future__ import annotations

import json
import socket
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tui.app import TUIApp

from tui.core.events import UpdateLinksEvent, StopSocketEvent, ExecAction
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
        links = data.get("_links", [])
        actions = data.get("_actions", [])

        if links:
            links_dict = {}
            for item in links:
                if ":" in item:
                    key, title = item.split(":", 1)
                    links_dict[key.strip()] = title.strip()
            self._app.post_message(UpdateLinksEvent(links=links_dict))

        if actions:
            self.logger.info(actions)
            for act in actions:
                self._app.post_message(ExecAction(action=act))

