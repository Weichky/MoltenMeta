from PySide6.QtCore import QObject, Signal

from db.user.repo import (
    ElementsRepository,
    SymbolsRepository,
    SystemsRepository,
    SystemCompositionsRepository,
    PropertiesRepository,
    MethodsRepository,
    PropertyValuesRepository,
    MetaRepository,
    UnitsRepository,
    PropertyValueConditionsRepository,
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

        self._symbol_repo = SymbolsRepository(log_service, db_manager)
        self._unit_repo = UnitsRepository(log_service, db_manager)
        self._element_repo = ElementsRepository(log_service, db_manager)
        self._system_repo = SystemsRepository(log_service, db_manager)
        self._system_composition_repo = SystemCompositionsRepository(
            log_service, db_manager
        )
        self._property_repo = PropertiesRepository(log_service, db_manager)
        self._method_repo = MethodsRepository(log_service, db_manager)
        self._property_value_repo = PropertyValuesRepository(log_service, db_manager)
        self._meta_repo = MetaRepository(log_service, db_manager)
        self._property_value_condition_repo = PropertyValueConditionsRepository(
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
    def element_repo(self) -> ElementsRepository:
        return self._element_repo

    @property
    def symbol_repo(self) -> SymbolsRepository:
        return self._symbol_repo

    @property
    def unit_repo(self) -> UnitsRepository:
        return self._unit_repo

    @property
    def system_repo(self) -> SystemsRepository:
        return self._system_repo

    @property
    def system_composition_repo(self) -> SystemCompositionsRepository:
        return self._system_composition_repo

    @property
    def property_repo(self) -> PropertiesRepository:
        return self._property_repo

    @property
    def method_repo(self) -> MethodsRepository:
        return self._method_repo

    @property
    def property_value_repo(self) -> PropertyValuesRepository:
        return self._property_value_repo

    @property
    def meta_repo(self) -> MetaRepository:
        return self._meta_repo

    @property
    def property_value_condition_repo(self) -> PropertyValueConditionsRepository:
        return self._property_value_condition_repo
