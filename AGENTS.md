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
