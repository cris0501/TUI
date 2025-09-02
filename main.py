# tui_basic.py
import curses, time
from typing import List, Dict
from footer import Footer
from promp import Promp
from logs import Logs
from title import Title

class SimpleTUI:
    def __init__(self):
        self.project = "MiProyecto"
        self.status  = "IDLE"       # ó "Loading"
        self.menu: List[Dict] = []  # [{ "title": "...", "id": 1 }, ...]
        self.lines: List[str] = []
        self.buf = ""               # prompt buffer
        self.scroll = 0
        
        self.title = None
        self.logs = None
        self.promp = None
        self.footer = None

    # --- API pública ---
    def set_project(self, name: str):
        self.project = name

    def set_status(self, status: str):
        self.status = status

    def set_menu(self, items: List[Dict]):
        """items: [{'id':1,'title':'Refrescar'}, ...]"""
        self.menu = items
        self.footer.set_content(items)

    def append_log(self, *msgs: str):
        self.lines.extend(msgs)
        if len(self.lines) > 10000:
            self.lines = self.lines[-5000:]

    # --- Loop principal ---
    def run(self):
        curses.wrapper(self._main)

    # --- Entrada/loop curses ---
    def _main(self, stdscr):
        curses.curs_set(0)         # cursor visible en prompt
        stdscr.keypad(True)
        stdscr.nodelay(True)
        curses.use_default_colors()

        last_draw = 0.0
        fps = 30.0
        frame = 1.0 / fps
        
        self.title = Title(stdscr)
        self.title.set_project(self.project)
        self.title.set_status(self.status)

        self.logs = Logs(stdscr)
        self.promp = Promp(stdscr)
        self.footer = Footer(stdscr)

        # Demo inicial
        self.append_log("Bienvenido a la TUI", "Escribe 'help' y Enter")
        if not self.menu:
            self.set_menu([
                {"id":1, "title":"Refrescar"},
                {"id":2, "title":"Abrir"},
                {"id":3, "title":"Eliminar"},
            ])

        status_h  = 1
        footer_h  = 2
        prompt_h  = 1
        logs_top = status_h + 1

        while True:
            # Tamaño actual y layout:
            H, W = stdscr.getmaxyx()
            logs_bottom = H - footer_h - prompt_h - 1

            self.title.set_metadata({'width':W, 'height':1, 'y_pos':0})
            self.logs.set_metadata({'width':W, 'height':logs_bottom, 'y_pos':1})
            self.promp.set_metadata({'width':W, 'height':1, 'y_pos':logs_bottom})
            self.footer.set_metadata({'width':W, 'height':2, 'y_pos':logs_bottom+1})
            
            if logs_bottom <= logs_top:
                logs_bottom = logs_top  # evita negativos

            # Entrada
            key = stdscr.getch()
            if key != -1:
                # Salida rápida
                if key in (3, 4):  # Ctrl+C / Ctrl+D
                    break
                # Scroll
                elif key == curses.KEY_PPAGE:
                    self.scroll = min(self.scroll + 1, max(0, len(self.lines) - (logs_bottom - logs_top)))
                elif key == curses.KEY_NPAGE:
                    self.scroll = max(0, self.scroll - 1)
                # Backspace
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    if self.buf: self.buf = self.buf[:-1]
                # Enter: ejecutar comando (demo)
                elif key in (10, 13):
                    cmd = self.buf.strip()
                    self.buf = ""
                    self.scroll = 0
                    if cmd:
                        self.append_log(f"> {cmd}")
                        self._handle_command(cmd)
                # Funciones (F1..F9): atajos de menú
                elif curses.KEY_F1 <= key <= curses.KEY_F9:
                    idx = key - curses.KEY_F1  # 0..8
                    if idx < len(self.menu):
                        self._handle_menu(self.menu[idx])
                # Texto visible
                elif 32 <= key <= 126:
                    self.buf += chr(key)

            # Render a ~60 FPS
            now = time.time()
            if now - last_draw >= frame:
                stdscr.erase()

                self.title._draw_()
                self.logs._draw_(self.lines, self.scroll)
                self.promp._draw_(self.buf)
                
                self.footer._draw_()

                stdscr.refresh()
                last_draw = now

            time.sleep(0.005)

    # --- Demo de handlers (sustituye por tu lógica real) ---
    def _handle_menu(self, item: Dict):
        title = item.get("title", f"#{item.get('id','')}")
        self.append_log(f"[MENU] {title}")
        # Simula acción de 'Loading'
        self.set_status("Loading")
        # (en real: lanza tarea y al terminar, cambia a IDLE)
        # aquí, demo corta:
        self.set_status("IDLE")

    def _handle_command(self, cmd: str):
        if cmd == "help":
            self.append_log("Comandos: help, ping, load, clear, exit")
        elif cmd == "ping":
            self.append_log("pong")
        elif cmd == "load":
            self.set_status("Loading")
            self.append_log("Cargando...")
            # simulado
            time.sleep(0.2)
            self.set_status("IDLE")
            self.append_log("Listo.")
        elif cmd == "clear":
            self.lines.clear()
        elif cmd == "exit":
            raise SystemExit
        else:
            self.append_log(f"cmd? '{cmd}'")

# --- Ejecución directa (demo) ---
if __name__ == "__main__":
    tui = SimpleTUI()
    tui.set_project("Demo-TUI")
    tui.set_status("IDLE")
    tui.run()
