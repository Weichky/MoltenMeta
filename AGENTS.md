# AGENTS.md - AI Agent Guidelines for MoltenMeta

## Skills

| Skill | Description |
|-------|-------------|
| `spec-skill` | Objective code review with weighted scoring (Correctness 40%, Readability 25%, Maintainability 20%, Performance 15%). Supports parallel subagent execution and result aggregation. |

---

## Guidelines for AI Agents

1. **Clean Architecture**: Dependency points inward — UI, Services, Use Cases, Entities. Outer layers depend on inner layers, never vice versa.
2. **Frozen dataclasses**: Use frozen dataclass for immutable data models (snapshots)
3. **Private by default**: Use `_` prefix for internal implementation
4. **Type hints**: Use Python 3.14 union syntax (`int | None`)
5. **Dependency injection**: Pass dependencies via constructors, not global getters
6. **No comments unless requested**: Avoid adding explanatory comments
7. **Minimize feature addition**: Do not add new features unless explicitly requested
8. **Preserve dependencies**: Do not break existing dependencies

## Coding Conventions

| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `MainWindow`, `CoreDbService` |
| Functions/Methods | camelCase | `_loadSettings`, `fromRow` |
| Variables | snake_case | `log_service`, `settings` |
| Private | `_` prefix | `_settings_repo` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_CONNECTIONS` |
| Files | snake_case | `core_db_service.py` |

**Import**: Use directory-level exports, avoid relative imports.
```python
# Good
from core.log import Logger
# Bad
from core.log.log import Logger
```

**Service pattern**: Use dependency injection via `AppContext`.

## Architecture

```
┌─────────────────────────────────────────┐
│            UI (gui/pages/)              │  ← Qt GUI, Matplotlib
├─────────────────────────────────────────┤
│         Application (service/)          │  ← Use Cases, Orchestration
├─────────────────────────────────────────┤
│    Modules (plugins via config.toml)    │  ← Calculation models
├─────────────────────────────────────────┤
│   Data (db/, application/settings/)     │  ← Entities (snapshots)
└─────────────────────────────────────────┘
```

**Clean Architecture Layers**:
- **Entities**: Snapshots — frozen dataclasses representing stable data structures
- **Use Cases**: Modules (Kohler, Toop, Maggianu, etc.) — calculation and analysis logic
- **Interface Adapters**: DataSource, BinaryProvider, Database adapters
- **Frameworks**: Qt GUI, Matplotlib, SQLite

**Plugin Architecture**: Modules are loaded dynamically via `config.toml` — no base class required, duck typing.

**Two-Phase Init**: `bootstrap()` creates services, `initApp()` loads settings.

**Dual DB**: `core.mmdb` for settings, user DB for data.

## Project Structure

```
src/
├── application/
│   ├── service/         # Application Services
│   └── settings/        # Settings model
├── catalog/             # Enums, constants
├── core/                # Config, log, plot, composition, element_map
├── db/                  # Database layer
│   ├── adapters/        # DB adapters (SQLite)
│   ├── core/repo/       # Core repositories
│   ├── snapshot/        # Data model snapshots
│   ├── seeds/           # Database seeds
│   └── user/repo/       # User data repositories
├── framework/           # ModuleManager, DataSource, BinaryProvider
├── gui/pages/           # UI pages (home, settings, data, simulation, analysis, table_manager)
├── i18n/
├── modules/             # Calculation modules (toop, miedema, etc.)
└── resources/           # Data, i18n, images, qtads
```

## Database Schema

Key tables: `symbols`, `units`, `elements`, `systems`, `system_compositions`, `properties`, `methods`, `property_values`, `data_groups`, `meta`

## Running & Testing

```bash
uv run python src/main.py --runtime-path ./runtime
uv run ruff check src/   # Lint
uv run ruff format src/  # Format
```

## Platform Notes

**Linux**: Use X11. Wayland has issues with Qt-Advanced-Docking-System.