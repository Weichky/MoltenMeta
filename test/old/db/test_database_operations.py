#!/usr/bin/env python3
"""
Database operations test for MoltenMeta
Tests basic database operations without GUI or other dependencies
"""

import sys
import os
import tempfile
import logging
from pathlib import Path

# Add src to path so we can import modules
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent / "src"
sys.path.insert(0, str(src_dir))


def test_database_operations():
    """Test basic database repository operations"""
    print("Testing database operations...")

    # Set up basic logging first
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
            # Import after setting up path
            from db.db_service import getDatabaseService, DatabaseService
            from db.repo.repositories import (
                ElementRepository,
                SystemRepository,
                PropertyRepository,
                MethodRepository,
            )
            from domain.snapshot.snapshots import (
                ElementSnapshot,
                SystemSnapshot,
                PropertySnapshot,
                MethodSnapshot,
            )

            print("✓ All imports successful")

            # Test database service
            service = DatabaseService()
            service.configureDatabase()
            print("✓ Database service configured")

            # Test element repository
            element_repo = ElementRepository()
            element_repo.createTable()
            print("✓ Elements table created")

            # Test element insertion
            element = ElementSnapshot(
                symbol="Fe",
                atomic_mass=55.845,
                atomic_radius=1.26,
                melting_point=1811.0,
                melt_density=7.0,
            )
            element_id = element_repo.insert(element)
            print(f"✓ Element inserted with ID: {element_id}")

            # Test element retrieval
            found_element = element_repo.findById(element_id)
            assert found_element is not None
            assert found_element.symbol == "Fe"
            print(f"✓ Element retrieved: {found_element.symbol}")

            # Test element search by symbol
            fe_element = element_repo.findBySymbol("Fe")
            assert fe_element is not None
            assert fe_element.symbol == "Fe"
            print(f"✓ Element found by symbol: {fe_element.symbol}")

            # Test system repository
            system_repo = SystemRepository()
            system_repo.createTable()
            print("✓ Systems table created")

            system = SystemSnapshot(component="Fe-Cr", n_component=2)
            system_id = system_repo.insert(system)
            print(f"✓ System inserted with ID: {system_id}")

            # Test property repository
            property_repo = PropertyRepository()
            property_repo.createTable()
            print("✓ Properties table created")

            prop = PropertySnapshot(
                name="Density", symbol="ρ", unit="g/cm³", category="Physical"
            )
            prop_id = property_repo.insert(prop)
            print(f"✓ Property inserted with ID: {prop_id}")

            # Test method repository
            method_repo = MethodRepository()
            method_repo.createTable()
            print("✓ Methods table created")

            method = MethodSnapshot(
                name="Experimental", type="measurement", detail="Direct measurement"
            )
            method_id = method_repo.insert(method)
            print(f"✓ Method inserted with ID: {method_id}")

            # Test count operations
            element_count = element_repo.count()
            system_count = system_repo.count()
            property_count = property_repo.count()
            method_count = method_repo.count()

            print(f"✓ Element count: {element_count}")
            print(f"✓ System count: {system_count}")
            print(f"✓ Property count: {property_count}")
            print(f"✓ Method count: {method_count}")

            # Test find all operations
            all_elements = element_repo.findAll()
            all_systems = system_repo.findAll()

            assert len(all_elements) == 1
            assert len(all_systems) == 1
            print("✓ Find all operations successful")

            # Test update operation
            element.atomic_mass = 55.846  # Small change
            updated = element_repo.update(element)
            assert updated == True
            print("✓ Element update successful")

            # Test delete operation
            deleted = property_repo.delete(prop_id)
            assert deleted == True
            print("✓ Property deletion successful")

            # Close connection
            service.close()
            print("✓ Database service closed")

            print("\n🎉 All database operations tests passed!")
            return True

        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback

            traceback.print_exc()
            return False

        finally:
            # Restore original functions
            core.platform.getRuntimePath = original_get_runtime_path
            core.log.log_service._log_service = original_log_service


if __name__ == "__main__":
    success = test_database_operations()
    sys.exit(0 if success else 1)
