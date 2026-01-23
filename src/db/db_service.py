#!/usr/bin/env python3
"""
Database configuration and management for MoltenMeta
Supports both SQLite and PostgreSQL databases
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from .abstraction import DatabaseConfig, DatabaseType
from .repo.base_repository import DatabaseManager
from core.platform import getRuntimePath
from core.log import getLogService


class DatabaseConfigManager:
    """Manages database configuration from environment variables or config files"""

    DEFAULT_CONFIG_FILE = "db_config.json"

    @classmethod
    def loadFromEnvironment(cls) -> DatabaseConfig:
        """Load database configuration from environment variables"""

        # Check for database type in environment
        db_type_str = os.getenv("MOLTENMETA_DB_TYPE", "sqlite").lower()

        if db_type_str == "postgresql":
            return DatabaseConfig(
                db_type=DatabaseType.POSTGRESQL,
                host=os.getenv("MOLTENMETA_DB_HOST", "localhost"),
                port=int(os.getenv("MOLTENMETA_DB_PORT", "5432")),
                database=os.getenv("MOLTENMETA_DB_NAME", "moltenmeta"),
                username=os.getenv("MOLTENMETA_DB_USER", "moltenmeta"),
                password=os.getenv("MOLTENMETA_DB_PASSWORD"),
            )
        else:
            # Default to SQLite
            runtime_path = getRuntimePath()
            if runtime_path:
                db_path = runtime_path / "moltenmeta.db"
            else:
                db_path = Path("moltenmeta.db")

            return DatabaseConfig(db_type=DatabaseType.SQLITE, file_path=str(db_path))

    @classmethod
    def loadFromFile(
        cls, config_path: Optional[Path] = None
    ) -> Optional[DatabaseConfig]:
        """Load database configuration from JSON file"""

        if config_path is None:
            runtime_path = getRuntimePath()
            if runtime_path:
                config_path = runtime_path / cls.DEFAULT_CONFIG_FILE
            else:
                config_path = Path(cls.DEFAULT_CONFIG_FILE)

        if not config_path.exists():
            return None

        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)

            db_type_str = config_data.get("type", "sqlite").lower()

            if db_type_str == "postgresql":
                return DatabaseConfig(
                    db_type=DatabaseType.POSTGRESQL,
                    host=config_data.get("host", "localhost"),
                    port=config_data.get("port", 5432),
                    database=config_data.get("database", "moltenmeta"),
                    username=config_data.get("username", "moltenmeta"),
                    password=config_data.get("password"),
                )
            else:
                return DatabaseConfig(
                    db_type=DatabaseType.SQLITE,
                    file_path=config_data.get("file_path", "moltenmeta.db"),
                )

        except Exception as e:
            logger = getLogService().getLogger(__name__)
            logger.error(f"Failed to load database config from {config_path}: {e}")
            return None

    @classmethod
    def saveToFile(
        cls, config: DatabaseConfig, config_path: Optional[Path] = None
    ) -> None:
        """Save database configuration to JSON file"""

        if config_path is None:
            runtime_path = getRuntimePath()
            if runtime_path:
                config_path = runtime_path / cls.DEFAULT_CONFIG_FILE
            else:
                config_path = Path(cls.DEFAULT_CONFIG_FILE)

        config_data = {"type": config.db_type.value}

        if config.db_type == DatabaseType.POSTGRESQL:
            if config.host is not None:
                config_data["host"] = config.host
            if config.port is not None:
                config_data["port"] = str(config.port)
            if config.database is not None:
                config_data["database"] = config.database
            if config.username is not None:
                config_data["username"] = config.username
            if config.password is not None:
                config_data["password"] = config.password
        else:
            config_data["file_path"] = config.file_path or "moltenmeta.db"

        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)


class DatabaseService:
    """High-level database service for application use"""

    def __init__(self):
        self._manager = DatabaseManager()
        self._logger = getLogService().getLogger(__name__)

    def configureDatabase(self, config: Optional[DatabaseConfig] = None) -> None:
        """Configure database with provided config or auto-detect"""

        if config is None:
            # Try to load from file first
            config = DatabaseConfigManager.loadFromFile()

            # If no file config, try environment variables
            if config is None:
                config = DatabaseConfigManager.loadFromEnvironment()

        self._manager.configure(config)
        self._logger.info(f"Database configured with type: {config.db_type.value}")

    def getManager(self) -> DatabaseManager:
        """Get underlying database manager"""
        return self._manager

    def testConnection(self) -> bool:
        """Test database connection"""
        try:
            connection = self._manager.getConnection()
            cursor = connection.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            self._logger.error(f"Database connection test failed: {e}")
            return False

    def close(self) -> None:
        """Close database connection"""
        self._manager.close()


# Global database service instance
_database_service: Optional[DatabaseService] = None


def getDatabaseService() -> DatabaseService:
    """Get global database service instance"""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service


def initializeDatabase(config: Optional[DatabaseConfig] = None) -> None:
    """Initialize database system"""
    service = getDatabaseService()
    service.configureDatabase(config)

    # Test connection
    if not service.testConnection():
        raise RuntimeError("Failed to connect to database")


def closeDatabase() -> None:
    """Close database system"""
    global _database_service
    if _database_service:
        _database_service.close()
        _database_service = None
