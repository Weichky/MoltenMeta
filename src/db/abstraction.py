from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum


class DatabaseType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class DatabaseDialect(ABC):
    """Abstract base class for database-specific SQL dialects"""

    @abstractmethod
    def getPlaceholder(self) -> str:
        """Get parameter placeholder for this database"""
        pass

    @abstractmethod
    def getAutoincrementType(self) -> str:
        """Get auto increment column type"""
        pass

    @abstractmethod
    def getPrimaryKeyType(self) -> str:
        """Get primary key column type"""
        pass

    @abstractmethod
    def getTextType(self) -> str:
        """Get text column type"""
        pass

    @abstractmethod
    def getRealType(self) -> str:
        """Get real/float column type"""
        pass

    @abstractmethod
    def getIntegerType(self) -> str:
        """Get integer column type"""
        pass

    @abstractmethod
    def getDatetimeType(self) -> str:
        """Get datetime column type"""
        pass

    @abstractmethod
    def supportsInsertOrReplace(self) -> bool:
        """Check if database supports INSERT OR REPLACE"""
        pass

    @abstractmethod
    def getUpsertSyntax(self, table: str, columns: List[str]) -> str:
        """Get upsert (insert or update) SQL syntax"""
        pass

    @abstractmethod
    def getLastIdSyntax(self) -> str:
        """Get SQL to retrieve last inserted ID"""
        pass


class DatabaseConnection(ABC):
    """Abstract base class for database connections"""

    @abstractmethod
    def connect(self) -> None:
        """Establish database connection"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close database connection"""
        pass

    @abstractmethod
    def execute(self, sql: str, params: Optional[List[Any]] = None) -> "DatabaseCursor":
        """Execute SQL query"""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit transaction"""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rollback transaction"""
        pass

    @abstractmethod
    def getDialect(self) -> DatabaseDialect:
        """Get database dialect"""
        pass


class DatabaseCursor(ABC):
    """Abstract base class for database cursor"""

    @abstractmethod
    def fetchone(self) -> Optional[Dict[str, Any]]:
        """Fetch one row"""
        pass

    @abstractmethod
    def fetchall(self) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        pass

    @property
    @abstractmethod
    def rowCount(self) -> int:
        """Get number of affected rows"""
        pass

    @property
    @abstractmethod
    def lastRowId(self) -> Optional[int]:
        """Get last inserted row ID"""
        pass


class DatabaseConfig:
    """Database configuration"""

    def __init__(
        self,
        db_type: DatabaseType,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        file_path: Optional[str] = None,
        **kwargs,
    ):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.file_path = file_path
        self.kwargs = kwargs
