from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from pathlib import Path

class DatabaseType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"

@dataclass
class DatabaseConfig:
    db_type: DatabaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = field(default="password", repr=False)
    file_path: Optional[Path] = None
    # Use a field to store additional parameters to avoid directly modifying __init__
    extra_params: dict = field(default_factory=dict)