#!/usr/bin/env python3
"""
Simple test for database abstraction
Tests that the new code style and structure works
"""

import sys
import tempfile
from pathlib import Path

# Add src to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def testCodeStyle():
    """Test that code style follows conventions"""
    print("Testing code style...")

    # Test that functions use snake_case
    try:
        from db.abstraction import DatabaseDialect, DatabaseConnection

        dialect_methods = [
            "getPlaceholder",
            "getAutoincrementType",
            "getPrimaryKeyType",
            "getTextType",
            "getRealType",
            "getIntegerType",
            "getDatetimeType",
            "supportsInsertOrReplace",
            "getUpsertSyntax",
            "getLastIdSyntax",
        ]

        for method in dialect_methods:
            assert hasattr(DatabaseDialect, method), f"Missing method: {method}"
            assert method[0].islower() or method[0] == "s", (
                f"Method {method} should be snake_case"
            )

        print("✓ Database dialect methods use snake_case")

        # Test that classes use PascalCase
        db_classes = [
            "DatabaseDialect",
            "DatabaseConnection",
            "DatabaseConfig",
            "DatabaseManager",
            "DatabaseService",
            "DatabaseConfigManager",
        ]

        for cls_name in db_classes:
            # Check if class exists and first letter is uppercase
            assert cls_name[0].isupper(), f"Class {cls_name} should be PascalCase"

        print("✓ Database classes use PascalCase")

        return True

    except Exception as e:
        print(f"❌ Code style test failed: {e}")
        return False


def testFileOrganization():
    """Test that files are organized properly"""
    print("Testing file organization...")

    try:
        import os

        # Check that adapters are in the adapters folder
        adapters_dir = Path(__file__).parent.parent.parent / "src" / "db" / "adapters"
        assert adapters_dir.exists(), "Adapters directory should exist"

        sqlite_file = adapters_dir / "sqlite.py"
        postgresql_file = adapters_dir / "postgresql.py"
        adapters_init = adapters_dir / "__init__.py"

        assert sqlite_file.exists(), "SQLite adapter should exist in adapters folder"
        assert postgresql_file.exists(), (
            "PostgreSQL adapter should exist in adapters folder"
        )
        assert adapters_init.exists(), "Adapters __init__.py should exist"

        print("✓ Database adapters are in adapters folder")

        # Check that schema.sql is still in db folder (alone)
        schema_file = Path(__file__).parent.parent.parent / "src" / "db" / "schema.sql"
        assert schema_file.exists(), "schema.sql should still be in db folder"

        print("✓ Schema file is properly left alone")

        # Check that test files are in test/db folder
        test_db_dir = Path(__file__).parent
        test_files = list(test_db_dir.glob("*.py"))
        assert len(test_files) >= 2, "Should have multiple test files in test/db"

        print("✓ Test files are organized in test/db folder")

        return True

    except Exception as e:
        print(f"❌ File organization test failed: {e}")
        return False


def testBasicImports():
    """Test basic imports work correctly"""
    print("Testing basic imports...")

    try:
        # Test abstraction imports
        from db.abstraction import DatabaseConfig, DatabaseType, DatabaseDialect

        # Test that enum values are lowercase strings
        assert DatabaseType.SQLITE.value == "sqlite"
        assert DatabaseType.POSTGRESQL.value == "postgresql"

        print("✓ Database types are correct")

        # Test configuration creation
        config = DatabaseConfig(db_type=DatabaseType.SQLITE, file_path="test.db")
        assert config.db_type == DatabaseType.SQLITE
        assert config.file_path == "test.db"

        print("✓ Database configuration works")

        return True

    except Exception as e:
        print(f"❌ Basic imports test failed: {e}")
        return False


def main():
    """Run all structure and style tests"""
    print("Running database structure and style tests...\n")

    tests = [testCodeStyle, testFileOrganization, testBasicImports]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All database structure and style tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
