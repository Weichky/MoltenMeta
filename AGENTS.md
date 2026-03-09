# AGENTS.md - AI Agent Guidelines for MoltenMeta

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Coding Conventions](#coding-conventions)
4. [Architecture](#architecture)
5. [Database Schema](#database-schema)
6. [Guidelines for AI Agents](#guidelines-for-ai-agents)
7. [Running & Testing](#running--testing)
8. [Platform Notes](#platform-notes)

---

## Project Overview

- **Name**: MoltenMeta
- **Language**: Python 3.14+, C++ (algorithm)
- **Architecture**: Clean Architecture with layered structure

### Implementation Status

| Status | Features |
|--------|----------|
| ✅ Completed | Core application shell with PySide6 + Qt-Advanced-Docking-System |
| ✅ Completed | Two-phase initialization (bootstrap → initApp) |
| ✅ Completed | Dual SQLite databases (core settings + user data) |
| ✅ Completed | Repository pattern with multi-dialect support (SQLite/PostgreSQL) |
| ✅ Completed | Domain snapshots (frozen dataclasses) |
| ✅ Completed | Theme system with light/dark mode support |
| ✅ Completed | Internationalization (i18n) framework |
| ✅ Completed | Home page, Settings page, Database page |
| ✅ Completed | Data import (CSV) |
| ✅ Completed | Settings persistence and hot-reload |
| 🚧 In Progress | Analysis and simulation pages |
| 🚧 In Progress | C++ algorithm engine integration |

---

## Project Structure

```
src/
├── algorithm/       # Algorithm engine (C++ / Python)
│   └── python/       # Python bindings
├── application/    # Application services and use cases
├── core/          # Core utilities (config, logging)
├── db/            # Database layer (adapters, repositories)
├── domain/        # Domain entities and business logic
├── gui/           # UI layer (PySide6 widgets)
│   ├── pages/     # Page widgets
│   ├── sidebar/   # Sidebar components
│   ├── menubar/   # Menu bar components
│   └── appearance/# Theme and styling
└── i18n/          # Internationalization
```

---

## Coding Conventions

### Naming Conventions

| Type | Convention | Examples |
|------|------------|----------|
| Classes | PascalCase | `MainWindow`, `CoreDbService`, `SettingsSnapshot` |
| Functions / Methods | camelCase | `_loadSettings`, `fromRow`, `toRecord` |
| Variables / Objects | snake_case | `log_service`, `database_service`, `settings` |
| Private Members | `_` prefix | `_settings_repo`, `_logger`, `_db_service` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_CONNECTIONS`, `DEFAULT_TIMEOUT` |
| File Names | snake_case | `core_db_service.py`, `snapshot_base.py` |

### Import Conventions

**Directory-level `__init__.py` Exports**

When files in the same directory have the same name conflict (e.g., `core/log/log.py` contains `Logger` class), export the class in the directory's `__init__.py` so it can be imported directly:

```python
# Good
from core.log import Logger

# Avoid
from core.log.log import Logger
```

**Service Import Pattern**

Use dependency injection via `AppContext` instead of global getter functions:

```python
# Wrong
from core.log import getLogService
logger = getLogService().getLogger(__name__)

# Correct
class SomeService:
    def __init__(self, log_service: LogService):
        self._logger = log_service.getLogger(__name__)
```

**Consistent Module Imports**

Prefer importing from the module level rather than relative imports:

```python
# Good
from core.log import LogService

# Avoid
from ..core.log.log import LogService
```

### Type Hints

Use Python 3.14 union syntax:

```python
def example(param: int | None) -> str | None: ...
```

---

## Architecture

### Clean Architecture Principles

```
┌─────────────────────────────────────────────────────────┐
│  UI Layer (gui/)                                        │
│  - PySide6 widgets, pages, components                   │
├─────────────────────────────────────────────────────────┤
│  Application Layer (application/)                       │
│  - Services, use cases                                  │
├─────────────────────────────────────────────────────────┤
│  Domain Layer (domain/)                                 │
│  - Entities, business logic, snapshots                  │
├─────────────────────────────────────────────────────────┤
│  Infrastructure Layer (db/, core/)                      │
│  - Repositories, adapters, utilities                    │
└─────────────────────────────────────────────────────────┘
```

### Two-Phase Initialization

```
┌────────────────────┐     ┌────────────────────┐
│     bootstrap()    │────▶│     initApp()      │
├────────────────────┤     ├────────────────────┤
│ LogService         │     │ CoreDbService      │
│ I18nService        │     │ Load settings      │
│ ThemeService       │     │ Update AppContext  │
│ (no Settings yet)  │     │                    │
└────────────────────┘     └────────────────────┘
```

**Bootstrap Flow:**

```python
# bootstrap(): Creates services, Settings NOT passed to AppContext
context = bootstrap(app)  # AppContext has settings=None

# initApp(): Load settings, update context
db_manager = _createCoreDbManager()
core_db_service = CoreDbService(app, context.log, db_manager)
context.core_db = core_db_service
context.settings = core_db_service.settings  # Update with real instance
```

### Dual Database Architecture

| Database | File | Purpose |
|----------|------|---------|
| Core | `core.mmdb` (runtime path) | App settings, configuration |
| User | (configurable path) | User data, imported materials |

### GUI Structure

Each page follows the pattern:

| File | Purpose |
|------|---------|
| `ui.py` | Qt UI setup (from Qt Designer) |
| `widget.py` | Custom widget logic |
| `controller.py` | Page controller (optional) |

**Signal/Slot Connections:**

```python
self.sidebar.ui.homeButton.clicked.connect(
    self.workspace.controller.showHome
)
```

### Internationalization (i18n)

Qt's translation scanner only recognizes string literals, not variables.

**Correct:**
```python
self.title.setText(self.tr("Welcome"))
self.save_button.setText(self.tr("Save"))
```

**Incorrect (will NOT be detected by lupdate):**
```python
msg = "Save"
self.save_button.setText(self.tr(msg))
```

**For dynamic text:**
```python
ok_text = self.tr("OK")
cancel_text = self.tr("Cancel")
self.message_box.setText(ok_text + " " + cancel_text)
```

**Using QCoreApplication.translate in controller:**
```python
def _translate(context: str, text: str) -> str:
    return QCoreApplication.translate(context, text)

# Correct - static string literal
msg = _translate("Context", "Error")

# Incorrect - won't be detected
error_text = "Error"
msg = _translate("Context", error_text)
```

> **Note:** If using `_translate()`, also update `scripts/lupdate.sh` to detect the pattern.

### Repository Pattern

- Repository classes in `db/user/repo/`
- Methods: `findAll()`, `findById()`, `save()`, `delete()`
- Repositories accept injected `DatabaseManager` via constructor

---

## Database Schema

The user database follows a layered domain-driven design:

### Layer Overview

```
Language Layer  ──▶  Ontology Layer  ──▶  Concept Layer  ──▶  Fact Layer
(sym, units)        (elements, sys)     (properties,      (property_values,
                                               methods,            conditions)
                                               conditions)
```

### Infrastructure Layer

```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section TEXT NOT NULL,
    key     TEXT NOT NULL,
    value   TEXT NOT NULL,
    UNIQUE(section, key)
);
```

### Language Layer

```sql
CREATE TABLE symbols (
    id        INTEGER PRIMARY KEY,
    symbol    TEXT NOT NULL,  -- e.g. T, P, ρ, Cp
    name      TEXT,
    category  TEXT             -- property / condition / constant / other
);

CREATE TABLE units (
    id        INTEGER PRIMARY KEY,
    symbol_id INTEGER NOT NULL,

    FOREIGN KEY (symbol_id)
        REFERENCES symbols(id)
        ON DELETE RESTRICT
);
```

### Ontology Layer (Stable Entities)

```sql
-- Chemical elements
CREATE TABLE elements (
    id            INTEGER PRIMARY KEY,
    symbol_id     INTEGER NOT NULL,
    atomic_mass   REAL,
    melting_point REAL,
    boiling_point REAL,
    liquid_range  REAL,

    FOREIGN KEY (symbol_id)
        REFERENCES symbols(id)
        ON DELETE RESTRICT
);

-- Material systems
CREATE TABLE systems (
    id           INTEGER PRIMARY KEY,
    label        TEXT NOT NULL,
    n_component  INTEGER
);

-- Composition
CREATE TABLE system_compositions (
    system_id   INTEGER NOT NULL,
    element_id  INTEGER NOT NULL,
    fraction    REAL    NOT NULL,

    PRIMARY KEY (system_id, element_id),

    FOREIGN KEY (system_id)
        REFERENCES systems(id)
        ON DELETE CASCADE,

    FOREIGN KEY (element_id)
        REFERENCES elements(id)
        ON DELETE RESTRICT
);
```

### Concept Layer

```sql
CREATE TABLE properties (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,
    symbol_id INTEGER NOT NULL,
    unit_id   INTEGER NOT NULL,
    category  TEXT,

    FOREIGN KEY (symbol_id)
        REFERENCES symbols(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (unit_id)
        REFERENCES units(id)
        ON DELETE RESTRICT
);

CREATE TABLE methods (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    type     TEXT,
    detail   TEXT
);
```

### Fact Layer

```sql
CREATE TABLE property_values (
    id           INTEGER PRIMARY KEY,
    system_id    INTEGER NOT NULL,
    property_id  INTEGER NOT NULL,
    method_id    INTEGER,
    value        REAL    NOT NULL,

    FOREIGN KEY (system_id)
        REFERENCES systems(id)
        ON DELETE CASCADE,

    FOREIGN KEY (property_id)
        REFERENCES properties(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (method_id)
        REFERENCES methods(id)
        ON DELETE SET NULL
);

CREATE TABLE property_value_conditions (
    id                  INTEGER PRIMARY KEY,
    property_value_id   INTEGER NOT NULL,
    symbol_id           INTEGER NOT NULL,
    unit_id             INTEGER NOT NULL,
    value               REAL    NOT NULL,
    name                TEXT,

    FOREIGN KEY (property_value_id)
        REFERENCES property_values(id)
        ON DELETE CASCADE,

    FOREIGN KEY (symbol_id)
        REFERENCES symbols(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (unit_id)
        REFERENCES units(id)
        ON DELETE RESTRICT
);
```

### Provenance Layer

```sql
CREATE TABLE meta (
    value_id     INTEGER PRIMARY KEY,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by   TEXT,
    source_file  TEXT,

    FOREIGN KEY (value_id)
        REFERENCES property_values(id)
        ON DELETE CASCADE
);
```

---

## Guidelines for AI Agents

1. **Follow Clean Architecture**: Keep domain, application, and infrastructure layers separate
2. **Use frozen dataclasses**: For immutable domain objects (snapshots)
3. **Private by default**: Use underscore prefix for internal implementation
4. **Type hints everywhere**: Enable better code analysis
5. **Single responsibility**: Each class/function should have one purpose
6. **Dependency injection**: Pass dependencies via constructors
7. **No comments unless requested**: Avoid adding explanatory comments
8. **Preserve existing comments**: Do not modify or delete existing comments unless necessary
9. **Minimize feature addition**: Do not add new features unless explicitly requested or required
10. **Avoid coupling**: Minimize inter-module dependencies to maintain loose coupling
11. **Preserve dependencies**: Do not break existing dependencies when making changes

---

## Running & Testing

### Running the Application

```bash
uv run python src/main.py --runtime-path ./runtime
```

### Testing Commands

| Command | Purpose |
|---------|---------|
| `ruff check src/` | Lint code |
| `ruff format src/` | Format code |

---

## Platform Notes

### Linux

- **X11 recommended**: Wayland sessions have known issues with Qt-Advanced-Docking-System
- Dock dragging may be broken or unresponsive under Wayland
- Switch to X11 session (e.g., "GNOME on Xorg") for stable behavior
