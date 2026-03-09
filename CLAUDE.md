# CLAUDE.md - Claude Code Project Context

## Project Overview

MoltenMeta is a desktop application for liquid metal property database and predictive modeling. See @README.md for details.

## Running the Application

```bash
uv run python src/main.py --runtime-path ./runtime
```

## Testing & Linting

```bash
# Lint
uv run ruff check src/

# Format
uv run ruff format src/
```

## Code Style

This project uses non-standard naming conventions:

- **Functions/methods**: camelCase (not snake_case)
- **Classes**: PascalCase
- **Variables**: snake_case
- **Private members**: single underscore prefix

See @AGENTS.md for full naming conventions.

## Architecture

- **Two-phase initialization**: `bootstrap()` → `initApp()`
- **Dual databases**: Core (settings) + User (data)
- **Dependency injection** via `AppContext`

See @AGENTS.md for detailed architecture documentation.

## Common Issues

- **Linux**: Use X11 session, not Wayland (Qt-Advanced-Docking-System incompatibility)
