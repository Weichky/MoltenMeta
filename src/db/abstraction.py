# Manual rewriting is urgently needed

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum

from pathlib import Path

class DatabaseDialect(ABC):
    """Abstract base class for database-specific SQL dialects"""

    @abstractmethod
    def getPlaceholder(self) -> str:
        """Get parameter placeholder for this database"""
        ...

    @abstractmethod
    def getAutoincrementType(self) -> str:
        """Get auto increment column type"""
        ...

    @abstractmethod
    def getPrimaryKeyType(self) -> str:
        """Get primary key column type"""
        ...

    @abstractmethod
    def getTextType(self) -> str:
        """Get text column type"""
        ...

    @abstractmethod
    def getRealType(self) -> str:
        """Get real/float column type"""
        ...

    @abstractmethod
    def getIntegerType(self) -> str:
        """Get integer column type"""
        ...

    @abstractmethod
    def getDatetimeType(self) -> str:
        """Get datetime column type"""
        ...

    @abstractmethod
    def supportsInsertOrReplace(self) -> bool:
        """Check if database supports INSERT OR REPLACE"""
        ...

    @abstractmethod
    def getUpsertSyntax(self, table: str, columns: List[str]) -> str:
        """Get upsert (insert or update) SQL syntax"""
        ...

    @abstractmethod
    def getLastIdSyntax(self) -> str:
        """Get SQL to retrieve last inserted ID"""
        ...


class DatabaseConnection(ABC):
    """Abstract base class for database connections"""

    @abstractmethod
    def connect(self) -> None:
        """Establish database connection"""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close database connection"""
        ...

    @abstractmethod
    def execute(self, sql: str, params: Optional[List[Any]] = None) -> "DatabaseCursor":
        """Execute SQL query"""
        ...

    @abstractmethod
    def commit(self) -> None:
        """Commit transaction"""
        ...

    @abstractmethod
    def rollback(self) -> None:
        """Rollback transaction"""
        ...

    @abstractmethod
    def getDialect(self) -> DatabaseDialect:
        """Get database dialect"""
        ...


class DatabaseCursor(ABC):
    """Abstract base class for database cursor"""

    @abstractmethod
    def fetchone(self) -> Optional[Dict[str, Any]]:
        """Fetch one row"""
        ...

    @abstractmethod
    def fetchall(self) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        ...

    @property
    @abstractmethod
    def rowCount(self) -> int:
        """Get number of affected rows"""
        ...

    @property
    @abstractmethod
    def lastRowId(self) -> Optional[int]:
        """Get last inserted row ID"""
        ...