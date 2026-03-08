# AGENTS.md - AI Agent Guidelines for MoltenMeta

## Project Overview

- **Name**: MoltenMeta
- **Language**: Python 3.14+, C++ (algorithm)
- **Architecture**: Clean Architecture with layered structure

### Implementation Status

**Completed:**
- Core application shell with PySide6 + Qt-Advanced-Docking-System
- Two-phase initialization (bootstrap → initApp)
- Dual SQLite databases (core settings + user data)
- Repository pattern with multi-dialect support (SQLite/PostgreSQL)
- Domain snapshots (frozen dataclasses)
- Theme system with light/dark mode support
- Internationalization (i18n) framework
- Home page, Settings page, Database page
- Data import (CSV)
- Settings persistence and hot-reload

**In Progress:**
- Analysis and simulation pages
- C++ algorithm engine integration

## Directory Structure

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

## Naming Conventions

### Classes
- **PascalCase**
- Examples: `MainWindow`, `CoreDbService`, `SettingsSnapshot`, `DatabaseService`

### Functions and Methods
- **camelCase**
- Examples: `_loadSettings`, `fromRow`, `toRecord`, `getLogger`

### Variables and Objects
- **snake_case**
- Examples: `log_service`, `database_service`, `settings`, `app_context`

### Private Members
- **Single underscore prefix** (`_`)
- Examples: `_settings_repo`, `_logger`, `_db_service`

### Constants
- **SCREAMING_SNAKE_CASE**
- Examples: `MAX_CONNECTIONS`, `DEFAULT_TIMEOUT`

### File Names
- **snake_case**
- Examples: `core_db_service.py`, `snapshot_base.py`, `main_window.py`

## Code Patterns

### Type Hints
Use Python 3.14 union syntax:
```python
def example(param: int | None) -> str | None: ...
```

### GUI Structure
Each page follows the pattern:
- `ui.py` - Qt UI setup (from Qt Designer)
- `widget.py` - Custom widget logic
- `controller.py` - Page controller (optional)

### Signal/Slot Connections
```python
self.sidebar.ui.homeButton.clicked.connect(
    self.workspace.controller.showHome
)
```

### Internationalization (i18n)
Qt's translation scanner only recognizes string literals, not variables. This is a known limitation.

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

**For dynamic text**, use static strings concatenated at runtime:
```python
ok_text = self.tr("OK")
cancel_text = self.tr("Cancel")
self.message_box.setText(ok_text + " " + cancel_text)
```

**Using QCoreApplication.translate in controller** (requires lupdate script support):
```python
def _translate(context: str, text: str) -> str:
    return QCoreApplication.translate(context, text)

# Correct - static string literal
msg = _translate("Context", "Error")

# Incorrect - won't be detected
error_text = "Error"
msg = _translate("Context", error_text)
```

Note: If using `_translate()`, also update `scripts/lupdate.sh` to detect the pattern.

### Repository Pattern
- Repository classes in `db/user/repo/`
- Methods: `findAll()`, `findById()`, `save()`, `delete()`

## Testing Commands

- **Lint**: `ruff check src/`
- **Format**: `ruff format src/`

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

## Running the Application

Use `uv` to run the application with required arguments:

```bash
uv run python src/main.py --runtime-path ./runtime
```

## Platform Notes

### Linux
- **X11 recommended**: Wayland sessions have known issues with Qt-Advanced-Docking-System
- Dock dragging may be broken or unresponsive under Wayland
- Switch to X11 session (e.g., "GNOME on Xorg") for stable behavior

## Import Conventions

### Directory-level `__init__.py` Exports
When files in the same directory have the same name conflict (e.g., `core/log/log.py` contains `Logger` class), export the class in the directory's `__init__.py` so it can be imported directly (e.g., `from core.log import Logger`).

### Service Import Pattern
Use dependency injection via `AppContext` instead of global getter functions like `getLogService()`, `getSettings()`, etc. Services should be passed through constructor injection.

Example:
```python
# Instead of:
from core.log import getLogService
logger = getLogService().getLogger(__name__)

# Use:
class SomeService:
    def __init__(self, log_service: LogService):
        self._logger = log_service.getLogger(__name__)
```

### Consistent Module Imports
Prefer importing from the module level (e.g., `from core.log import LogService`) rather than relative imports (e.g., `from ..core.log.log import LogService`).

## Settings & Database Architecture

### Architecture Principles
1. **Settings is the single source of truth** for all runtime configuration
2. **Two-phase initialization**:
   - **bootstrap()**: Creates core services (LogService, I18nService, ThemeService) without Settings
   - **initApp()**: Creates CoreDbService, loads settings from core database, then updates AppContext
3. **Two SQLite databases**:
   - **Core database**: Stores app settings (`core.mmdb` in runtime path)
   - **User database**: Stores user data (separate file, path from settings)
4. **No circular dependencies**: Database path for core db must come from args/defaults, not settings
5. **AppContext should not be mutated after init**: Settings are set once during initApp(), not passed as class

### Bootstrap Flow
```python
# bootstrap(): Creates services, Settings NOT passed to AppContext
context = bootstrap(app)  # AppContext has settings=None

# initApp(): Load settings, update context
db_manager = _createCoreDbManager()
core_db_service = CoreDbService(app, context.log, db_manager)
context.core_db = core_db_service
context.settings = core_db_service.settings  # Update with real instance
```

### Repository Pattern
- Repositories accept injected `DatabaseManager` via constructor
- If no manager is provided, they create a default one (for backwards compatibility)

## Database Schema

The user database follows a layered domain-driven design:

### Infrastructure Layer
```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section TEXT NOT NULL,          -- Logical section, e.g. app / logging / locale
    key     TEXT NOT NULL,           -- Configuration key
    value   TEXT NOT NULL,           -- Serialized value (type resolved in upper layers)
    UNIQUE(section, key)
);
```

### Language Layer
```sql
CREATE TABLE symbols (
    id        INTEGER PRIMARY KEY,
    symbol    TEXT NOT NULL,         -- e.g. T, P, ρ, Cp
    name      TEXT,                  -- Human-readable meaning
    category  TEXT                   -- property / condition / constant / other
);

CREATE TABLE units (
    id        INTEGER PRIMARY KEY,
    symbol_id     INTEGER NOT NULL,  -- Reference to language-layer symbol (v T, ρ, Cp, ...)
);
```

### Ontology Layer (Stable Entities)
```sql
-- Chemical elements as stable reference entities
CREATE TABLE elements (
    id            INTEGER PRIMARY KEY,
    symbol_id     INTEGER NOT NULL,  -- Reference to language-layer symbol (Fe, Al, ...)
    atomic_mass   REAL,
    atomic_radius REAL,
    melting_point REAL,
    melt_density  REAL,

    FOREIGN KEY (symbol_id)
        REFERENCES symbols(id)
        ON DELETE RESTRICT
);

-- Material systems (alloys, compounds, etc.)
CREATE TABLE systems (
    id           INTEGER PRIMARY KEY,
    label        TEXT NOT NULL,      -- Human-facing identifier (e.g. Fe-C alloy)
    n_component  INTEGER             -- Cached component count (denormalized)
);

-- Composition as a first-class fact
CREATE TABLE system_composition (
    system_id   INTEGER NOT NULL,
    element_id  INTEGER NOT NULL,
    fraction    REAL    NOT NULL,    -- Molar or atomic fraction

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
-- Physical / thermodynamic / mechanical quantities
CREATE TABLE properties (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,  -- e.g. density, heat_capacity
    symbol_id INTEGER NOT NULL,       -- Reference to shared symbol (ρ, Cp, ...)
    unit_id   INTEGER NOT NULL,         -- Reference to shared symbol (kg/m3, J/kg/K, ...)
    category  TEXT,                  -- Optional grouping (thermal, mechanical, ...)

    FOREIGN KEY (symbol_id)
        REFERENCES symbols(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (unit_id)
        REFERENCES units(id)
        ON DELETE RESTRICT
);

-- Measurement or calculation methods
CREATE TABLE methods (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,           -- e.g. experiment, DFT, MD
    type     TEXT,                    -- Experimental / computational / empirical
    detail   TEXT                     -- Free-form description
);

-- Generalized conditions (independent variables)
CREATE TABLE conditions (
    id        INTEGER PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,   -- temperature, pressure, magnetic_field
    symbol_id INTEGER,                -- T, P, H, ...
    unit_id   INTEGER NOT NULL,

    FOREIGN KEY (symbol_id)
        REFERENCES symbols(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (unit_id)
        REFERENCES units(id)
        ON DELETE RESTRICT
);
```

### Fact Layer
```sql
-- Observed or computed property values
CREATE TABLE property_values (
    id           INTEGER PRIMARY KEY,
    system_id    INTEGER NOT NULL,
    property_id  INTEGER NOT NULL,
    method_id    INTEGER,
    value        REAL    NOT NULL,    -- Observed / computed value

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

-- Contextual conditions attached to a property value
CREATE TABLE property_value_conditions (
    value_id     INTEGER NOT NULL,
    condition_id INTEGER NOT NULL,
    value        REAL    NOT NULL,

    PRIMARY KEY (value_id, condition_id),

    FOREIGN KEY (value_id)
        REFERENCES property_values(id)
        ON DELETE CASCADE,

    FOREIGN KEY (condition_id)
        REFERENCES conditions(id)
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