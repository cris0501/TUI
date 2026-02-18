# TUI

A lightweight Terminal UI framework built with Python and curses.

## The Story

This started as a small management interface for my other project, [DepInc](https://github.com/cris0501/DepInc). What was supposed to be a simple tool to control the service ended up growing into something that deserved its own space. So here we are.

## What It Is

TUI is a minimal but functional terminal UI framework. It won't change your life, but it might save you a few hours if you ever need to build something that runs in the terminal and actually feels like an app — not just print statements everywhere.

It follows an event-driven architecture with a clean separation between:
- **UI** (widgets, layout, rendering)
- **Event handling** (input translation, domain logic)
- **State** (mutable application state, render queue)

Current features:
- Log viewer panel with scrolling
- Text input prompt with cursor navigation
- Status bar and action footer (F1-F3)
- Socket server to receive remote commands and update actions dynamically
- Clock service for time-based events

## Run It

```bash
python -m tui.app
```

Requirements: Python 3.10+, curses module, and a real TTY (no Jupyter notebooks).

## Structure

```
tui/
├── core/          # Event bus, message loop, context
├── handlers/      # Input, domain, and UI handlers
├── state/         # App state and render queue
├── ui/            # Layout, renderer, widgets
└── services/      # Clock, socket
```

The message loop drains events from a thread-safe queue (~60 FPS), dispatches through an event bus, and redraws only the widgets that actually changed. Clean and efficient.

## Where It's Going

- Turn the socket server into a client
- Support Unix domain sockets — if it's a local socket, it's the manager; if TCP, it's a client
- Add floating popup windows for certain actions
- Evolve into a tiny framework with basic DTOs/models (nothing fancy, just practical)

It's a personal project. Not revolutionary, but it's got personality and it's fun to work on.
