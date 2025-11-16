# TUI Framework

This project is a lightweight, modular terminal user interface (TUI) framework built in Python. It provides a clear separation of concerns through a ViewModel-driven design and a reactive core, enabling interactive terminal applications with clean state management and structured rendering.

## Overview

The framework organizes the application into four main layers:

- Views – Responsible for terminal rendering and user interaction.
- ViewModels – Manage the state and logic for each view.
- Core – Handles layout computation, event distribution, and redraw orchestration.
- Services & Utilities – Provide logging, data handling, and helper functionalities.

This structure allows developers to build terminal applications with a predictable update flow and isolated components.

## Architecture

### Views

Located under the views/ directory, each view encapsulates the presentation logic for a specific UI section. Examples include:

- title.py – Show general state of window
- logs.py – Display of application logs.
- prompt.py – Input area for user commands or text.
- footer.py – Describe and show buttons with any acction.

Views rely on their corresponding ViewModels to access state and trigger updates.

### ViewModels

Located under viewmodels/, each ViewModel defines the state, validation rules, and reactions for a single UI component. Examples include:

- title_vm.py
- logs_vm.py
- prompt_vm.py
- footer_vm.py

ViewModels communicate with the core store, subscribe to events, and update views reactively.

### Core

The core/ directory contains the foundational mechanisms:

- events.py – Event bus used for communication between components.
- store.py – Central reactive state container.
- layout.py – Layout computation for multi-section UI.
- redraw.py – Rendering engine responsible for efficiently updating the terminal.

### Services

The services/ directory offers domain-specific utilities, such as:

- log_service.py – Handles log storage and retrieval for display.

### Utilities

The utils/ directory includes support modules used across the project, such as:

- logger.py – Basic logging utility.

## Entry Point

The run.py script initializes the application and wires together the views, ViewModels, and core components.

## Features

- Modular design based on clearly separated responsibilities.
- Reactive update cycle through a centralized store.
- Event-driven interaction model.
- Layout engine designed for multi-section terminal interfaces.
- Extendable architecture for adding custom views and service modules.

## Getting Started

Requirements

- Python 3.10 or later

Running the Application

```bash
python run.py
```

## Extending the Framework

To implement new UI sections or behaviors:

1. Create a ViewModel under viewmodels/ describing the state and logic.

2. Implement a corresponding view under views/ for rendering.

3. Register new components in the entry point or main composition file.

4. Use the event bus and store to integrate reactive behaviors.

## Project Status

This framework is under active development. Future updates will focus on improving the rendering pipeline, enhancing component communication, and expanding the available UI building blocks.


---

If you want, I can also generate a more detailed architecture diagram in Markdown or PlantUML.

> Nota: `curses` requiere TTY; ejecuta en una terminal real (no en notebooks).