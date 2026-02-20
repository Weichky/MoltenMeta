from typing import Any, Dict, List

from ..abstraction import (
    DatabaseDialect,
    DatabaseConnection,
    DatabaseCursor,
)

from catalog import DatabaseConnInfo

from core.log import LogService

# PostgreSQL imports - these will be needed only when PostgreSQL is used
try:
    import psycopg2
    import psycopg2.extras

    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class PostgreSQLDialect(DatabaseDialect):
    """PostgreSQL-specific SQL dialect"""

    def getPlaceholder(self) -> str:
        return "%s"

    def getAutoincrementType(self) -> str:
        return "SERIAL PRIMARY KEY"

    def getPrimaryKeyType(self) -> str:
        return "INTEGER PRIMARY KEY"

    def getTextType(self) -> str:
        return "TEXT"

    def getRealType(self) -> str:
        return "DOUBLE PRECISION"

    def getIntegerType(self) -> str:
        return "INTEGER"

    def getDatetimeType(self) -> str:
        return "TIMESTAMP"

    def supportsInsertOrReplace(self) -> bool:
        return False

    def getUpsertSyntax(self, table: str, columns: List[str]) -> str:
        """PostgreSQL ON CONFLICT syntax for upsert"""
        placeholders = ", ".join([self.getPlaceholder() for _ in columns])
        update_clause = ", ".join(
            [f"{col} = EXCLUDED.{col}" for col in columns if col != "id"]
        )
        return f"""
        INSERT INTO {table} ({", ".join(columns)}) 
        VALUES ({placeholders}) 
        ON CONFLICT (id) 
        DO UPDATE SET {update_clause}
        """

    def getLastIdSyntax(self) -> str:
        return "SELECT lastval()"


class PostgreSQLCursor(DatabaseCursor):
    """PostgreSQL cursor wrapper"""

    def __init__(self, cursor):
        self._cursor = cursor

    def fetchone(self) -> Dict[str, Any] | None:
        row = self._cursor.fetchone()
        if row:
            return dict(row)
        return None

    def fetchall(self) -> List[Dict[str, Any]]:
        rows = self._cursor.fetchall()
        return [dict(row) for row in rows]

    @property
    def rowCount(self) -> int:
        return self._cursor.rowcount

    @property
    def lastRowId(self) -> int | None:
        # PostgreSQL doesn't have lastrowid, need to use RETURNING or lastval()
        return None


class PostgreSQLConnection(DatabaseConnInfo):
    """PostgreSQL connection implementation"""

    def __init__(self, config: DatabaseConnInfo, log_service: LogService):
        if not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "psycopg2 is required for PostgreSQL support. Install with: pip install psycopg2-binary"
            )

        self.config = config
        self._connection = None
        self._dialect = PostgreSQLDialect()
        self._logger = log_service.getLogger(__name__)

    def connect(self) -> None:
        if not all([self.config.host, self.config.database, self.config.username]):
            raise ValueError(
                "PostgreSQL requires host, database, and username in config"
            )

        connection_string = (
            f"host={self.config.host} "
            f"port={self.config.port or 5432} "
            f"dbname={self.config.database} "
            f"user={self.config.username}"
        )

        if self.config.password:
            connection_string += f" password={self.config.password}"

        self._connection = psycopg2.connect(connection_string)
        # Enable dictionary-like cursor
        self._connection.cursor_factory = psycopg2.extras.RealDictCursor

        self._logger.info(
            f"Connected to PostgreSQL database at {self.config.host}:{self.config.port or 5432}/{self.config.database}"
        )

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None
            self._logger.info("Closed PostgreSQL connection")

    def execute(self, sql: str, params: List[Any] | None = None) -> DatabaseCursor:
        if not self._connection:
            raise RuntimeError("Database connection not established")

        cursor = self._connection.cursor()
        cursor.execute(sql, params)
        return PostgreSQLCursor(cursor)

    def commit(self) -> None:
        if self._connection:
            self._connection.commit()

    def rollback(self) -> None:
        if self._connection:
            self._connection.rollback()

    def getDialect(self) -> DatabaseDialect:
        return self._dialect

    def executeWithLastId(
        self, sql: str, params: List[Any] | None = None
    ) -> DatabaseCursor:
        """Execute SQL and return cursor with ability to get last inserted ID"""
        if not self._connection:
            raise RuntimeError("Database connection not established")

        cursor = self._connection.cursor()

        # For PostgreSQL, we need to use RETURNING clause to get the ID
        if "INSERT" in sql.upper() and "RETURNING" not in sql.upper():
            # Add RETURNING clause if not present
            sql += " RETURNING id"

        cursor.execute(sql, params)
        return PostgreSQLCursor(cursor)
