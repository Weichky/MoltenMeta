from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class DatabaseType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"

@dataclass
class DatabaseConnInfo:
    db_type: DatabaseType
    host: str | None = None
    port: int | None = None
    database: str | None = None
    username: str | None = None
    password: str | None = field(default="password", repr=False)
    file_path: Path | None = None
    # Use a field to store additional parameters to avoid directly modifying __init__
    connect_args: dict = field(default_factory=dict)