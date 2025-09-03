
# TUI MVVM Demo (LayoutService + RedrawManager + Stores)

Demostración mínima en **Python + curses** que implementa:
- `LayoutService`: fuente única de geometrías (rects).
- `RedrawManager`: cola de vistas sucias, hace `noutrefresh()` por vista y **un** `doupdate()` por frame.
- Stores (slices): `FooterStore`, `LogsStore`, `PromptStore`.
- ViewModels por vista (`FooterVM`, `LogsVM`, etc.) que se suscriben al store y **solo** invalidan vistas.
- Views (`FooterView`, `LogsView`, `TitleView`, `PromptView`) que dibujan y **no** llaman a `doupdate()`.

## Ejecutar
```bash
python3 run.py
```
Teclas:
- `a`: agrega una línea a **Logs**.
- `f`: cambia el texto del **Footer**.
- `TAB`: enfoca el **Prompt** (no es un input completo, pero muestra el flujo).
- `q`: salir.

Redimensiona la terminal para ver cómo el layout recalcula y el RedrawManager repinta solo lo necesario.

> Nota: `curses` requiere TTY; ejecuta en una terminal real (no en notebooks).
