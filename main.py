# tui_basic.py
import curses, time
from typing import List, Dict

class SimpleTUI:
    def __init__(self):
        self.project = "MiProyecto"
        self.status  = "IDLE"       # ó "Loading"
        self.menu: List[Dict] = []  # [{ "title": "...", "id": 1 }, ...]
        self.lines: List[str] = []
        self.buf = ""               # prompt buffer
        self.scroll = 0

    # --- API pública ---
    def set_project(self, name: str):
        self.project = name

    def set_status(self, status: str):
        self.status = status

    def set_menu(self, items: List[Dict]):
        """items: [{'id':1,'title':'Refrescar'}, ...]"""
        self.menu = items

    def append_log(self, *msgs: str):
        self.lines.extend(msgs)
        if len(self.lines) > 10000:
            self.lines = self.lines[-5000:]

    # --- Loop principal ---
    def run(self):
        curses.wrapper(self._main)

    # --- Internos de render ---
    def _draw_status(self, stdscr, width):
        # Línea 0: "Proyecto" a la izq, "STATUS" a la der.
        stdscr.move(0, 0)
        stdscr.clrtoeol()
        left = f"{self.project}"
        right = f"{self.status}"
        stdscr.addnstr(0, 0, left, max(0, width - 1), curses.A_BOLD)
        stdscr.addnstr(0, max(0, width - len(right) - 1), right, len(right), curses.A_DIM)

    def _draw_footer(self, stdscr, y_start, width):
        # 2 líneas de footer con menú (F1..F9); separador arriba
        stdscr.hline(y_start, 0, curses.ACS_HLINE, width)
        labels = [f"[F{i+1}] {item.get('title','')}" for i, item in enumerate(self.menu[:9])]
        # Particiona labels en dos líneas respetando ancho
        line1, line2 = "", ""
        for lab in labels:
            if not line1 or len(line1) + len(lab) + 2 <= width - 2: # Empty label or len string
                line1 = (lab if not line1 else line1 + "  " + lab)
            elif not line2 or len(line2) + len(lab) + 2 <= width - 2:
                line2 = (lab if not line2 else line2 + "  " + lab)
            else:
                # Si tampoco cabe en line2, recorta y añade "…"
                if len(line2) < width - 3:
                    line2 = line2[:max(0, width - 5)] + "…"
                break
        stdscr.addnstr(y_start + 1, 1, line1, width - 2, curses.A_BOLD)
        stdscr.addnstr(y_start + 2, 1, line2, width - 2, curses.A_BOLD)

    def _draw_prompt(self, stdscr, y, width):
        # Línea de prompt (una línea), resaltada
        stdscr.move(y, 0)
        stdscr.clrtoeol()
        prompt = f"> {self.buf}"
        stdscr.addnstr(y, 0, prompt[-(width-1):], width, curses.A_REVERSE)

    def _draw_log(self, stdscr, top, height, width):
        # Muestra logs con posible scroll; deja la última línea libre para el prompt
        view_h = max(0, height - 1)
        if view_h <= 0:
            return
        start = max(0, len(self.lines) - view_h - self.scroll)
        end   = len(self.lines) - self.scroll if self.scroll == 0 else len(self.lines) - self.scroll
        view  = self.lines[start:end]
        y = top
        for line in view:
            # Cortar por ancho
            for chunk_start in range(0, len(line), width):
                if y >= top + view_h: break
                chunk = line[chunk_start:chunk_start+width]
                stdscr.move(y, 0); stdscr.clrtoeol()
                stdscr.addnstr(y, 0, chunk, width)
                y += 1
            if y >= top + view_h: break

    # --- Entrada/loop curses ---
    def _main(self, stdscr):
        curses.curs_set(0)         # cursor visible en prompt
        stdscr.keypad(True)
        stdscr.nodelay(True)
        curses.use_default_colors()

        last_draw = 0.0
        fps = 30.0
        frame = 1.0 / fps

        # Demo inicial
        self.append_log("Bienvenido a la TUI", "Escribe 'help' y Enter")
        if not self.menu:
            self.set_menu([
                {"id":1, "title":"Refrescar"},
                {"id":2, "title":"Abrir"},
                {"id":3, "title":"Eliminar"},
            ])


        while True:
            # Tamaño actual y layout:
            H, W = stdscr.getmaxyx()
            status_h  = 1
            footer_h  = 2
            prompt_h  = 1
            # Orden de arriba a abajo:
            # 0: status
            # logs: [1 .. logs_bottom-1]
            # prompt: at logs_bottom
            # footer: [logs_bottom+1 .. H-1]
            logs_top = status_h + 1
            logs_bottom = H - footer_h - prompt_h - 2 # índice de la fila del prompt
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
                # self.append_log(f"H: {H}", f"W: {W}")
                stdscr.erase()
                # status
                self._draw_status(stdscr, W)
                # logs
                self._draw_log(stdscr, logs_top, logs_bottom - logs_top, W)
                # prompt (en logs_bottom)
                self._draw_prompt(stdscr, logs_bottom + 1, W)
                # footer (2 líneas, debajo del prompt + separador)
                self._draw_footer(stdscr, logs_bottom + 2, W)
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
    tui.set_menu([
        {"id":1, "title":"Refrescar"},
        {"id":2, "title":"Abrir"},
        {"id":3, "title":"Eliminar"},
        {"id":4, "title":"Exportar"},
        {"id":5, "title":"Ayuda"},
    ])
    tui.run()
