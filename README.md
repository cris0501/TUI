# TUI - Terminal User Interface Application

Una aplicación TUI implementada con una arquitectura message-driven basada en curses, siguiendo principios estrictos de separación de responsabilidades y flujo controlado por eventos.

## 🏗️ Arquitectura

Este proyecto implementa una arquitectura imperativa controlada por eventos con un Message Loop central y un Event Bus pasivo. A diferencia de las arquitecturas reactivas, esta implementación utiliza un flujo explícito donde cada componente tiene responsabilidades bien definidas y sin cruces.

### Principios Arquitectónicos Fundamentales

#### 🎯 Message Loop (ML) - Orquestador Central
- **Es el único componente que:**
  - Orquesta el ciclo de ejecución (tick)
  - Decide cuándo se procesan eventos
  - Invoca handlers
- **NO contiene lógica de negocio**
- **Controla el flujo global de la aplicación**

#### 📋 Event Bus (EB) - Registro Pasivo
- **Es solo un registro de handlers**
- **No ejecuta lógica**
- **No tiene estado de runtime**
- **Métodos principales:** `register()`, `get_handlers()`

#### 🎨 Render Queue (RQ) - Desacoplamiento Visual
- **Todo redraw se encola en la RenderQueue**
- **Solo un Renderer central ejecuta llamadas a curses**
- **Los widgets nunca acceden directamente a curses**

#### 💾 Estado Explícito, No Reactivo
- **No hay reactividad automática**
- **El estado es mutado de forma explícita**
- **El redraw ocurre solo si el Message Loop lo decide**

#### 📨 Eventos como Mensajes, No como Flujos
- **Un evento representa:**
  - Una intención
  - Un input
  - Un cambio ya ocurrido
- **Un evento no es un caso de uso completo**

## 📁 Estructura del Proyecto

```
tui/
├── app.py                  # Entry point principal
│
├── core/                   # Núcleo del sistema
│   ├── message_loop.py     # Orquestador principal
│   ├── event_bus.py        # Registro pasivo de handlers
│   ├── events.py           # Definición de eventos (dataclasses)
│   └── context.py          # Dependencias compartidas
│
├── state/                  # Gestión de estado
│   ├── app_state.py        # Estado global mínimo
│   └── render_queue.py     # Cola de redraws
│
├── ui/                     # Interfaz de usuario
│   ├── layout.py           # Construcción de ventanas
│   ├── renderer.py         # Único acceso a curses
│   └── widgets/            # Componentes UI
│       ├── base.py         # Contrato de widgets
│       ├── title.py        # Widget de título
│       ├── logs.py         # Widget de logs
│       ├── prompt.py       # Widget de entrada
│       └── footer.py       # Widget de pie
│
├── handlers/               # Procesadores de eventos
│   ├── input_handlers.py   # Teclado / mouse
│   ├── ui_handlers.py      # Reacciones visuales
│   └── domain_handlers.py  # Cambios de estado / lógica
│
└── services/               # Servicios externos
    ├── data_service.py     # IO, DB, HTTP, persistencia
    └── clock.py            # Fuente de ticks temporales
```

## 🔄 Flujo de Ejecución

### Diagrama ASCII del Flujo Completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FLUJO DE EJECUCIÓN TUI                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐     1.     ┌──────────────┐     2.     ┌─────────────────┐
│   Usuario   │ ────────► │  Input/Curses │ ────────► │  Message Loop   │
│             │           │              │           │                 │
│ - Teclado   │           │ - get_wch()  │           │ - tick()        │
│ - Mouse     │           │ - getch()    │           │ - process_input │
│ - Resize    │           │ - Events     │           │ - event_queue   │
└─────────────┘           └──────────────┘           └─────────────────┘
                                                                  │
                                                                  │ 3.
                                                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        MESSAGE LOOP TICK                               │
│                                                                         │
│  ┌─────────────┐    4.    ┌──────────────┐    5.    ┌─────────────┐  │
│  │Event Queue  │ ───────► │ Event Bus    │ ───────► │  Handlers   │  │
│  │             │          │              │          │             │  │
│  │- Input      │          │- register()  │          │- Input      │  │
│  │- Tick       │          │- get_handlers│          │- UI         │  │
│  │- System     │          │              │          │- Domain     │  │
│  └─────────────┘          └──────────────┘          └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                                                  │
                                                                  │ 6.
                                                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           HANDLERS PROCESSING                            │
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│  │  Input Handlers │    │   UI Handlers    │    │ Domain Handlers │    │
│  │                 │    │                 │    │                 │    │
│  │- Key -> Events   │    │- State Updates  │    │- Business Logic│    │
│  │- Char Processing │    │- Render Queue   │    │- Command Process│    │
│  │- Special Keys   │    │- Visual Changes │    │- Data Operations│    │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
        │                         │                         │
        │ 7a.                     │ 7b.                     │ 7c.
        ▼                         ▼                         ▼
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Events    │         │ Render      │         │   State     │
│   Queue     │         │ Queue       │         │  Updates    │
│             │         │             │         │             │
│- New Events │         │- Render     │         │- AppState   │
│- Mutations  │         │  Requests   │         │- Prompts    │
│- System     │         │- Widget IDs │         │- Logs       │
└─────────────┘         └─────────────┘         └─────────────┘
                                                        │
                                                        │ 8.
                                                        ▼
                                              ┌─────────────────┐
                                              │   AppState      │
                                              │                 │
                                              │- PromptState    │
                                              │- LogsState      │
                                              │- FooterState    │
                                              │- TitleState     │
                                              │- UIState        │
                                              └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          RENDERING CYCLE                                │
│                                                                         │
│     9.         ┌─────────────────┐        10.        ┌─────────────┐   │
│  Render     ◄───│  Render Queue   │──────────────► │  Renderer   │   │
│  Decision        │                 │                │             │   │
│   Check          │- RenderRequests │                │- curses     │   │
│                  │- Widget IDs     │                │- subwindows │   │
│                  │- Priority       │                │- draw()     │   │
│                  └─────────────────┘                └─────────────┘   │
│                                                           │            │
│                                                           │ 11.        │
│                                                           ▼            │
│                                               ┌─────────────────┐   │
│                                               │   Widgets       │   │
│                                               │                 │   │
│                                               │- get_data()     │   │
│                                               │- title.py       │   │
│                                               │- logs.py        │   │
│                                               │- prompt.py      │   │
│                                               │- footer.py      │   │
│                                               └─────────────────┘   │
│                                                           │            │
│                                                           │ 12.        │
│                                                           ▼            │
│                                               ┌─────────────────┐   │
│                                               │ curses.draw()   │   │
│                                               │                 │   │
│                                               │- stdscr         │   │
│                                               │- subwins        │   │
│                                               │- refresh()      │   │
│                                               │- doupdate()     │   │
│                                               └─────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                                                        │
                                                                        │ 13.
                                                                        ▼
                                                              ┌─────────────┐
                                                              │   Screen    │
                                                              │  Display    │
                                                              │             │
                                                              │- Title      │
                                                              │- Logs       │
                                                              │- Prompt     │
                                                              │- Footer     │
                                                              └─────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        SERVICIOS EXTERNOS                                │
│                                                                         │
│     14.               ┌─────────────────┐      15.       ┌─────────────┐ │
│  Data               ◄───│ Data Service    │──────────────► │ Persistence │ │
│  Operations            │                 │              │             │ │
│  - Config             │- load_config()  │              │- JSON Files │ │
│  - Save               │- save_config()  │              │- State Data │ │
│  - Logs               │- save_logs()    │              │- History    │ │
│                       │- load_state()   │              │             │ │
│                       └─────────────────┘              └─────────────┘ │
│                                                           │             │
│     16.                    │                          │             │
│  Time                     ▼                          ▼             │
│  Services          ┌─────────────────┐        ┌─────────────┐        │
│                     │ Clock Service   │        │ System      │        │
│                     │                 │        │ Services    │        │
│                     │- ticks          │        │             │        │
│                     │- timestamps     │        │- OS Calls   │        │
│                     │- uptime         │        │- File IO    │        │
│                     └─────────────────┘        └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          CONTROL DE FLUJO                                │
│                                                                         │
│     LOOP CONTROL          MESSAGE LOOP          EVENT HANDLING         │
│     ────────────          ────────────          ──────────────         │
│                                                                         │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────────┐       │
│  │  Main Loop  │◄────►│Message Loop │◄────►│  Event System   │       │
│  │             │      │             │      │                 │       │
│  │- curses     │      │- tick()     │      │- Event Types    │       │
│  │- wrapper    │      │- queue      │      │- Handlers       │       │
│  │- while()    │      │- process    │      │- Dispatch       │       │
│  │- cleanup   │      │- events     │      │- State Mgmt     │       │
│  └─────────────┘      └─────────────┘      └─────────────────┘       │
│         │                   │                       │                 │
│         │ 17.               │ 18.                   │ 19.             │
│         ▼                   ▼                       ▼                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐           │
│  │   app.py    │    │  context.py │    │  events.py      │           │
│  │             │    │             │    │                 │           │
│  │- initialize │    │- Dependencies│    │- DataClasses    │           │
│  │- run()      │    │- DI Container│    │- Event Types    │           │
│  │- main()     │    │- Global State│    │- Payloads       │           │
│  │- cleanup()  │    │- Services    │    │- Validation     │           │
│  └─────────────┘    └─────────────┘    └─────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Descripción Detallada del Flujo

#### **Fase 1: Captura de Input**
1. **Usuario interactúa** con la terminal (teclado, mouse, resize)
2. **Curses captura** el input a través de `get_wch()`
3. **Message Loop recibe** el input crudo

#### **Fase 2: Procesamiento del Message Loop**
4. **Input Handlers** convierten el input crudo en eventos estandarizados
5. **Eventos se encolan** en la cola de mensajes del Message Loop
6. **Message Loop.tick()** procesa todos los eventos pendientes

#### **Fase 3: Dispatch de Eventos**
7. **Event Bus** proporciona los handlers registrados para cada tipo de evento
8. **Handlers se ejecutan** en orden:
   - **Input Handlers**: Procesan teclas y mouse
   - **UI Handlers**: Actualizan estado visual y encolan renders
   - **Domain Handlers**: Ejecutan lógica de negocio

#### **Fase 4: Mutación de Estado**
9. **AppState se muta** explícitamente a través de los handlers
10. **Cambios de estado** generan nuevos eventos si es necesario

#### **Fase 5: Renderizado**
11. **Render Queue** acumula solicitudes de renderizado
12. **Renderer** consume la cola y dibuja en curses
13. **Widgets proporcionan** datos sin acceso directo a curses
14. **Pantalla se actualiza** atómicamente con `doupdate()`

#### **Fase 6: Servicios Externos**
15. **Data Service** maneja persistencia y configuración
16. **Clock Service** proporciona temporización y ticks

## 🚀 Características

### Funcionalidades Principales
- **✅ Editor de texto completo** con cursor, navegación y edición
- **✅ Sistema de comandos** con `/help`, `/clear`, `/debug`, `/config`, `/exit`
- **✅ Funciones rápidas** F1-F9 para acciones comunes
- **✅ Logging completo** con timestamps opcionales
- **✅ Persistencia** de configuración y estado
- **✅ Resize dinámico** adaptativo a cambios de terminal

### Comandos Disponibles
```
/help          - Muestra ayuda completa
/clear         - Limpia los logs
/debug         - Activa/desactiva modo debug
/config [key [value]] - Gestiona configuración
/exit          - Sale de la aplicación
```

### Funciones de Teclado
```
F1 - Update     F2 - Add
F3 - Test       F4 - Config  
F5 - Help       F9 - Exit
← → ↑ ↓        - Navegación
Home/End       - Inicio/Final
Backspace/Del  - Edición
Ctrl+C         - Salida forzada
```

## 🛠️ Instalación y Ejecución

### Requisitos
- Python 3.8+
- curses (generalmente incluido en Python estándar)
- Terminal compatible con curses

### Ejecución
```bash
# Clonar o navegar al proyecto
cd /path/to/TUI

# Ejecutar la aplicación
python run_new.py

# O directamente
python -m tui.app
```

### Configuración
La configuración se guarda automáticamente en `tui_config.json`:
```json
{
  "tick_interval": 0.01,
  "max_log_lines": 500,
  "prompt_max_length": 256,
  "add_timestamps": false,
  "debug_mode": false,
  "theme": "default"
}
```

## 🏛️ Validación de Principios Arquitectónicos

### ✅ Restricciones Cumplidas

#### **Message Loop Central**
- ✅ Único orquestador del ciclo de ejecución
- ✅ Decide cuándo procesar eventos
- ✅ Invoca handlers explícitamente
- ✅ Sin lógica de negocio

#### **Event Bus Pasivo**
- ✅ Solo registro de handlers
- ✅ Sin ejecución de lógica
- ✅ Sin estado de runtime
- ✅ Métodos pasivos: `register()`, `get_handlers()`

#### **Renderizado Desacoplado**
- ✅ Ningún widget accede a curses directamente
- ✅ Todo redraw se encola en RenderQueue
- ✅ Solo Renderer central ejecuta llamadas a curses
- ✅ Widgets solo proporcionan datos

#### **Estado Explícito**
- ✅ No hay reactividad automática
- ✅ Estado mutado explícitamente
- ✅ Redraw solo si Message Loop lo decide
- ✅ AppState mínimo y controlado

#### **Eventos como Mensajes**
- ✅ Eventos representan intenciones o inputs
- ✅ Eventos no son casos de uso completos
- ✅ Dataclasses inmutables
- ✅ Payload explícito y tipado

## 🔧 Arquitectura Interna

### Event System
```python
# Tipos de eventos definidos
class EventType(Enum):
    KEY_PRESS = "key_press"
    PROMPT_TEXT_CHANGED = "prompt_text_changed"
    LOGS_APPEND = "logs_append"
    FOOTER_ACTION = "footer_action"
    RESIZE = "resize"
    RENDER_REQUEST = "render_request"
    TICK = "tick"
    SHUTDOWN = "shutdown"
```

### State Management
```python
# Estado explícito sin reactividad
@dataclass
class AppState:
    prompt: PromptState
    logs: LogsState  
    footer: FooterState
    title: TitleState
    ui: UIState
    running: bool = True
```

### Widget Contract
```python
# Contrato estricto para widgets
class Widget(ABC):
    def get_render_data(self, app_state) -> RenderData
    def handle_event(self, event_data) -> bool
    def can_focus(self) -> bool
    # SIN acceso a curses
```

## 📊 Comparación con Arquitecturas Reactivas

| Característica | Arquitectura Reactiva | Arquitectura Message-Driven |
|---------------|----------------------|----------------------------|
| **Flujo** | Automático, implícito | Explícito, controlado |
| **Estado** | Reactivo, observables | Mutación explícita |
| **Render** | Automático ante cambios | Encolado, decidido |
| **Acoplamiento** | Loose coupling | Desacoplamiento total |
| **Control** | Distribuido | Centralizado |
| **Debugging** | Difícil, reacciones | Predecible, lineal |

## 🧪 Testing y Validación

### Tests de Arquitectura
```python
# Validación de restricciones
def test_event_bus_pasivity():
    bus = EventBus()
    assert not bus._handlers  # No ejecuta lógica
    
def test_renderer_only_curses():
    widgets = [TitleWidget(), LogsWidget()]
    for widget in widgets:
        assert 'curses' not in widget.__dict__  # Sin acceso directo
        
def test_explicit_mutations():
    state = AppState()
    initial = state.prompt.text
    # Solo se modifica a través de eventos
```

### Tests de Flujo
```python
def test_message_loop_flow():
    # Input → Event → Handler → State → Render
    input_handler.handle_key('a')
    assert state.prompt.text == 'a'
    assert 'prompt' in render_queue.get_pending_widgets()
```

## 🤝 Contribución

### Principios a Mantener
1. **Message Loop siempre orquesta**
2. **Event Bus siempre pasivo**
3. **Widgets nunca tocan curses**
4. **Estado siempre explícito**
5. **Eventos siempre mensajes, no flujos**

### Guía de Contribución
- Seguir la estructura de carpetas estricta
- Implementar tests de arquitectura
- Documentar flujo de eventos nuevos
- Validar restricciones en PRs

## 📄 Licencia

[MIT License](LICENSE)

---

**Nota Importante**: Esta arquitectura está diseñada específicamente para seguir principios message-driven estrictos. No es una arquitectura reactiva tradicional, sino un sistema controlado explícitamente donde cada componente tiene responsabilidades bien definidas y sin cruces.