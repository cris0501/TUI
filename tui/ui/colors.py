import curses

# Color indices (usando rango alto para no pisar los 0-15 estándar)
_BG      = 16
_FG      = 17
_COMMENT = 18
_CYAN    = 19
_GREEN   = 20
_ORANGE  = 21
_PINK    = 22
_PURPLE  = 23
_RED     = 24
_YELLOW  = 25

# Pares nombrados (usar estos en los widgets)
PAIR_DEFAULT = 1  # texto normal
PAIR_TITLE   = 2  # nombre de la app  — cyan
PAIR_STATUS  = 3  # estado derecha    — green
PAIR_FOOTER  = 4  # atajos de teclado — comment/gris
PAIR_ACCENT  = 5  # resaltado fuerte  — pink
PAIR_WARN    = 6  # advertencias      — orange
PAIR_ERROR   = 7  # errores           — red
PAIR_PROMPT  = 8  # línea de entrada  — purple


def init_colors() -> None:
    curses.start_color()
    curses.use_default_colors()

    if curses.can_change_color() and curses.COLORS >= 256:
        # curses.init_color(_BG,       157, 165, 212)
        curses.init_color(_BG,       0, 0, 0)
        curses.init_color(_FG,       973, 973, 949)
        curses.init_color(_COMMENT,  384, 447, 643)
        curses.init_color(_CYAN,     545, 914, 992)
        curses.init_color(_GREEN,    314, 980, 482)
        curses.init_color(_ORANGE,  1000, 722, 424)
        curses.init_color(_PINK,    1000, 475, 776)
        curses.init_color(_PURPLE,   741, 576, 976)
        curses.init_color(_RED,     1000, 333, 333)
        curses.init_color(_YELLOW,   945, 980, 549)
        bg = _BG
    else:
        bg = -1

    curses.init_pair(PAIR_DEFAULT, _FG,      bg)
    curses.init_pair(PAIR_TITLE,   _CYAN,    bg)
    curses.init_pair(PAIR_STATUS,  _GREEN,   bg)
    curses.init_pair(PAIR_FOOTER,  _COMMENT, bg)
    curses.init_pair(PAIR_ACCENT,  _PINK,    bg)
    curses.init_pair(PAIR_WARN,    _ORANGE,  bg)
    curses.init_pair(PAIR_ERROR,   _RED,     bg)
    curses.init_pair(PAIR_PROMPT,  _PURPLE,  bg)
