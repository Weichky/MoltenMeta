# AGENTS.md - AI Agent Guidelines for MoltenMeta

## Project Overview

- **Name**: MoltenMeta
- **Type**: Desktop application (PySide6/Qt for Python)
- **Language**: Python 3.14+
- **Architecture**: Clean Architecture with layered structure

## Directory Structure

```
src/
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