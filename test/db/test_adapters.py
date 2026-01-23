#!/usr/bin/env python3
"""
Test database adapters and abstraction layer
Tests both SQLite and PostgreSQL database adapters
"""

import sys
import os
import tempfile
from pathlib import Path

# Add src to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_sqlite_adapter():
    """Test SQLite adapter"""
    print("Testing SQLite adapter...")

    # Set up basic logging
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s](%(name)s)|%(asctime)s|%(message)s",
    )

    # Set up temporary runtime directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock runtime path
        import core.platform

        original_get_runtime_path = core.platform.getRuntimePath
        core.platform.getRuntimePath = lambda: Path(temp_dir)

        # Mock log service
        import core.log.log_service
        from PySide6.QtCore import QObject

        class MockLogService(QObject):
            def getLogger(self, name: str) -> logging.Logger:
                return logging.getLogger(name)

        original_log_service = core.log.log_service._log_service
        core.log.log_service._log_service = MockLogService(None)

        try:
            from db.abstraction import DatabaseConfig, DatabaseType
            from db.db_service import DatabaseService
            from domain.snapshot.snapshots import ElementSnapshot

            # Configure SQLite
            config = DatabaseConfig(
                db_type=DatabaseType.SQLITE, file_path=str(Path(temp_dir) / "test.db")
            )

            service = DatabaseService()
            service.configureDatabase(config)

            # Test connection
            assert service.testConnection(), "SQLite connection failed"
            print("✓ SQLite connection successful")

            # Test dialect
            manager = service.getManager()
            dialect = manager.getDialect()
            assert dialect.getPlaceholder() == "?", "SQLite placeholder should be ?"
            assert dialect.supportsInsertOrReplace(), (
                "SQLite should support INSERT OR REPLACE"
            )
            print("✓ SQLite dialect working")

            # Test basic operation
            from db.repo import ElementRepository

            element_repo = ElementRepository()
            element_repo.createTable()

            element = ElementSnapshot(
                symbol="Fe",
                atomic_mass=55.845,
                atomic_radius=1.26,
                melting_point=1811.0,
                melt_density=7.0,
            )
            element_id = element_repo.insert(element)
            assert element_id > 0, "Element insertion failed"
            print("✓ SQLite element insertion successful")

            service.close()
            print("✓ SQLite test completed")
            return True

        except Exception as e:
            print(f"❌ SQLite test failed: {e}")
            import traceback

            traceback.print_exc()
            return False

        finally:
            # Restore original functions
            core.platform.getRuntimePath = original_get_runtime_path
            core.log.log_service._log_service = original_log_service


def test_postgresql_adapter():
    """Test PostgreSQL adapter (only if psycopg2 is available)"""
    print("Testing PostgreSQL adapter...")

    try:
        import psycopg2

        print("✓ psycopg2 available")
    except ImportError:
        print("⚠️  psycopg2 not available, skipping PostgreSQL tests")
        return True

    # Set up basic logging
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)s](%(name)s)|%(asctime)s|%(message)s",
    )

    # Mock runtime path
    import core.platform

    original_get_runtime_path = core.platform.getRuntimePath
    core.platform.getRuntimePath = lambda: Path("/tmp")

    # Mock log service
    import core.log.log_service
    from PySide6.QtCore import QObject

    class MockLogService(QObject):
        def getLogger(self, name: str) -> logging.Logger:
            return logging.getLogger(name)

    original_log_service = core.log.log_service._log_service
    core.log.log_service._log_service = MockLogService(None)

    try:
        from db.abstraction import DatabaseConfig, DatabaseType
        from db.adapters.postgresql import PostgreSQLDialect, PostgreSQLConnection

        # Test dialect
        dialect = PostgreSQLDialect()
        assert dialect.getPlaceholder() == "%s", "PostgreSQL placeholder should be %s"
        assert not dialect.supportsInsertOrReplace(), (
            "PostgreSQL should not support INSERT OR REPLACE"
        )
        print("✓ PostgreSQL dialect working")

        # Test connection (will fail without real database, but should validate config)
        config = DatabaseConfig(
            db_type=DatabaseType.POSTGRESQL,
            host="localhost",
            database="testdb",
            username="testuser",
        )

        connection = PostgreSQLConnection(config)
        print("✓ PostgreSQL connection object created")

        # Test upsert syntax
        upsert_sql = dialect.getUpsertSyntax("test_table", ["id", "name"])
        assert "ON CONFLICT" in upsert_sql, "PostgreSQL upsert should use ON CONFLICT"
        print("✓ PostgreSQL upsert syntax working")

        print("✓ PostgreSQL test completed (no real connection required)")
        return True

    except Exception as e:
        print(f"❌ PostgreSQL test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Restore original functions
        core.platform.getRuntimePath = original_get_runtime_path
        core.log.log_service._log_service = original_log_service


def test_database_configuration():
    """Test database configuration system"""
    print("Testing database configuration system...")

    try:
        from db.abstraction import DatabaseConfig, DatabaseType
        from db.db_service import DatabaseConfigManager

        # Test environment config loading
        os.environ["MOLTENMETA_DB_TYPE"] = "postgresql"
        os.environ["MOLTENMETA_DB_HOST"] = "testhost"
        os.environ["MOLTENMETA_DB_PORT"] = "5433"

        config = DatabaseConfigManager.loadFromEnvironment()
        assert config.db_type == DatabaseType.POSTGRESQL
        assert config.host == "testhost"
        assert config.port == 5433
        print("✓ Environment configuration loading working")

        # Test default SQLite config
        del os.environ["MOLTENMETA_DB_TYPE"]
        config = DatabaseConfigManager.loadFromEnvironment()
        assert config.db_type == DatabaseType.SQLITE
        print("✓ Default SQLite configuration working")

        return True

    except Exception as e:
        print(f"❌ Database configuration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_database_service():
    """Test high-level database service"""
    print("Testing database service...")

    try:
        # Mock log service first
        import core.log.log_service
        from PySide6.QtCore import QObject

        class MockLogService(QObject):
            def getLogger(self, name: str):
                import logging

                return logging.getLogger(name)

        original_log_service = core.log.log_service._log_service
        core.log.log_service._log_service = MockLogService(None)

        from db.db_service import DatabaseService, getDatabaseService

        # Test service creation
        service = DatabaseService()
        assert service is not None, "DatabaseService should be created"
        print("✓ Database service creation working")

        # Test global service
        global_service = getDatabaseService()
        assert global_service is not None, "Global database service should be available"
        print("✓ Global database service working")

        return True

    except Exception as e:
        print(f"❌ Database service test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Restore original log service
        try:
            core.log.log_service._log_service = original_log_service
        except:
            pass


def main():
    """Run all database adapter tests"""
    print("Running database adapter tests...\n")

    tests = [
        test_database_configuration,
        test_database_service,
        test_sqlite_adapter,
        test_postgresql_adapter,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All database adapter tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
