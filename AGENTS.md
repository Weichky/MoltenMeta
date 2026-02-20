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

### Current Issues
- **Dual System**: Config system (`core/config/`) reads from TOML files; Settings system (`domain/settings/`) should read from SQLite but isn't fully integrated
- **Bootstrap Order Problem**: Database needs runtime path from args, but settings need database
- **Duplicated Functions**: `getLanguage()`, `getLogLevel()` etc. exist in both config.py and need to use Settings
- **Repository Dependency Issue**: `SettingsRepository` creates its own `DatabaseManager` internally instead of accepting injected dependency

### Architecture Principles
1. **Settings is the single source of truth** for all runtime configuration
2. **Bootstrap sequence**:
   - Step 1: Parse args, set up logging (needs runtime path)
   - Step 2: Set up core database connection (using hardcoded/default SQLite path for core db)
   - Step 3: Load settings from core database (seed default if empty)
   - Step 4: Use settings for all subsequent configuration
3. **Two SQLite databases**:
   - **Core database**: Stores app settings (`core.mmdb` in runtime path)
   - **User database**: Stores user data (separate file, path from settings)
4. **No circular dependencies**: Database path for core db must come from args/defaults, not settings

### Implementation Plan

#### Phase 1: Fix Bootstrap & Database Initialization
1. **Modify `application/app_startup.py`**:
   - Accept runtime path as parameter (from args)
   - Create core database connection first (use default path: `{runtime_path}/data/db/core.mmdb`)
   - Initialize settings repository with the database manager
   - Seed default settings if database is empty
   - Pass settings to AppContext

2. **Modify `db/core/repo/settings_repository.py`**:
   - Accept `DatabaseManager` as constructor parameter (dependency injection)
   - Remove internal `DatabaseManager` instantiation

3. **Modify `db/base_repository.py`**:
   - Accept `DatabaseManager` as constructor parameter

#### Phase 2: Unify Config & Settings
4. **Modify `core/config/config.py`**:
   - Remove file-based config loading (`_loadConfig`)
   - Replace with settings-based functions that read from a global `Settings` instance
   - Keep function signatures the same for backward compatibility
   - Add `initializeSettings(settings: Settings)` function to set the global settings instance

5. **Modify `application/app_context.py`**:
   - Add `settings: Settings` to AppContext
   - Initialize config system with settings

#### Phase 3: Cleanup
6. **Remove or deprecate `core/fio/config_io.py`**:
   - Keep for any non-settings config (if any)
   - Or remove entirely if no longer needed

7. **Update all consumers**:
   - `gui/pages/settings_page/ui.py` - uses `core.config.getLanguage()`, `getLogLevel()`
   - These will continue to work if config.py is updated to use settings

### Key Files to Modify
- `src/application/app_startup.py` - Bootstrap sequence
- `src/application/app_context.py` - Add settings to context
- `src/db/base_repository.py` - Accept DatabaseManager injection
- `src/db/core/repo/settings_repository.py` - Accept DatabaseManager injection
- `src/core/config/config.py` - Use Settings instead of TOML files
- `src/core/fio/config_io.py` - Remove or deprecate
- `src/gui/pages/settings_page/ui.py` - Will work if config.py updated

### Database Paths
- **Core database**: `{runtime_path}/data/db/core.mmdb` (hardcoded default)
- **User database**: `{runtime_path}/data/db/{settings.database_file}` (from settings)

### Additional Implementation Notes

1. **Update `resources/default/default_settings.toml`**:
   - Add missing settings that are currently in `default_config_file.toml` (database settings)
   - The settings file should contain ALL runtime configuration

2. **Settings serialization**:
   - Use `domain.settings.serializeSettingValue()` to convert values to strings for storage
   - Already implemented in `domain/settings/serialize.py`

3. **Global Settings Instance**:
   - Use a module-level global `_settings` variable in config.py
   - Initialize via `initializeSettings(settings: Settings)` at app startup

4. **Seed Default Settings**:
   - Use `db/seeds/settings_seed.py` to load defaults from TOML
   - Seed only if settings table is empty
