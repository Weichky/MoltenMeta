from PySide6.QtCore import QObject, Signal

from db.user.repo import (
    ElementRepository,
    SymbolRepository,
    SystemRepository,
    SystemCompositionRepository,
    PropertyRepository,
    MethodRepository,
    PropertyValueRepository,
    MetaRepository,
    UnitRepository,
    ConditionRepository,
    PropertyValueConditionRepository,
)

from db import DatabaseManager

from core.log import LogService

from db.seeds.symbols_seed import loadDefaultSymbols, loadSymbolsFromCsvFile
from db.seeds.elements_seed import loadDefaultElements, loadElementsFromCsvFile


class UserDbService(QObject):
    dataImported = Signal(int)

    def __init__(
        self,
        app,
        log_service: LogService,
        db_manager: DatabaseManager,
    ):
        super().__init__(app)
        self._log_service = log_service
        self._logger = log_service.getLogger(__name__)
        self._db_manager = db_manager

        self._symbol_repo = SymbolRepository(log_service, db_manager)
        self._unit_repo = UnitRepository(log_service, db_manager)
        self._element_repo = ElementRepository(log_service, db_manager)
        self._system_repo = SystemRepository(log_service, db_manager)
        self._system_composition_repo = SystemCompositionRepository(
            log_service, db_manager
        )
        self._property_repo = PropertyRepository(log_service, db_manager)
        self._method_repo = MethodRepository(log_service, db_manager)
        self._property_value_repo = PropertyValueRepository(log_service, db_manager)
        self._meta_repo = MetaRepository(log_service, db_manager)
        self._condition_repo = ConditionRepository(log_service, db_manager)
        self._property_value_condition_repo = PropertyValueConditionRepository(
            log_service, db_manager
        )

        self._initTables()

    def _initTables(self) -> None:
        self._symbol_repo.createTable()
        self._unit_repo.createTable()
        self._element_repo.createTable()
        self._system_repo.createTable()
        self._system_composition_repo.createTable()
        self._property_repo.createTable()
        self._method_repo.createTable()
        self._property_value_repo.createTable()
        self._meta_repo.createTable()
        self._condition_repo.createTable()
        self._property_value_condition_repo.createTable()

        if self._symbol_repo.count() == 0:
            defaults = loadDefaultSymbols()
            self._symbol_repo.upsert(defaults)

        if self._element_repo.count() == 0:
            defaults = loadDefaultElements()
            for elem in defaults:
                self._element_repo.insert(elem)

    def importSymbolsFromCsv(self, file_path: str) -> int:
        snapshots = loadSymbolsFromCsvFile(file_path)
        self._symbol_repo.upsert(snapshots)
        count = len(snapshots)
        self._logger.info(f"Imported {count} symbols from {file_path}")
        self.dataImported.emit(count)
        return count

    def importElementsFromCsv(self, file_path: str) -> int:
        snapshots = loadElementsFromCsvFile(file_path)
        for elem in snapshots:
            self._element_repo.insert(elem)
        count = len(snapshots)
        self._logger.info(f"Imported {count} elements from {file_path}")
        self.dataImported.emit(count)
        return count

    @property
    def element_repo(self) -> ElementRepository:
        return self._element_repo

    @property
    def symbol_repo(self) -> SymbolRepository:
        return self._symbol_repo

    @property
    def unit_repo(self) -> UnitRepository:
        return self._unit_repo

    @property
    def system_repo(self) -> SystemRepository:
        return self._system_repo

    @property
    def system_composition_repo(self) -> SystemCompositionRepository:
        return self._system_composition_repo

    @property
    def property_repo(self) -> PropertyRepository:
        return self._property_repo

    @property
    def method_repo(self) -> MethodRepository:
        return self._method_repo

    @property
    def property_value_repo(self) -> PropertyValueRepository:
        return self._property_value_repo

    @property
    def meta_repo(self) -> MetaRepository:
        return self._meta_repo

    @property
    def condition_repo(self) -> ConditionRepository:
        return self._condition_repo

    @property
    def property_value_condition_repo(self) -> PropertyValueConditionRepository:
        return self._property_value_condition_repo
