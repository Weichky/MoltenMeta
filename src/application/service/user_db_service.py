import csv
from dataclasses import dataclass, field

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
    ComputationCacheRepository,
    PropertyTagsRepository,
    DataGroupsRepository,
)

from db import DatabaseManager

from core.log import LogService
from core.composition import CompositionTool, FractionType, CompositionError

from db.seeds.symbols_seed import loadDefaultSymbols, loadSymbolsFromCsvFile
from db.seeds.elements_seed import loadDefaultElements, loadElementsFromCsvFile


@dataclass
class ImportError:
    row: int
    message: str
    detail: str | None = None


@dataclass
class ImportResult:
    success: bool
    imported_count: int
    group_id: int
    group_name: str
    errors: list[ImportError] = field(default_factory=list)


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
        self._computation_cache_repo = ComputationCacheRepository(
            log_service, db_manager
        )
        self._property_tags_repo = PropertyTagsRepository(log_service, db_manager)
        self._data_groups_repo = DataGroupsRepository(log_service, db_manager)

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
        self._computation_cache_repo.createTable()
        self._property_tags_repo.createTable()
        self._data_groups_repo.createTable()

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

    def importPropertyValuesFromCsv(self, file_path: str) -> ImportResult:
        from domain import (
            PropertyValueSnapshot,
            SystemSnapshot,
            SystemCompositionSnapshot,
            MetaSnapshot,
            DataGroupSnapshot,
        )
        from datetime import datetime

        REQUIRED_COLUMNS = {"system_label", "property_name", "value"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                sample = f.read(1024)
                f.seek(0)
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t ")
                reader = csv.DictReader(f, dialect=dialect)

                if not reader.fieldnames:
                    return ImportResult(
                        success=False,
                        imported_count=0,
                        group_id=-1,
                        group_name="",
                        errors=[ImportError(row=0, message="CSV file is empty")],
                    )

                headers = {h.strip().lower() for h in reader.fieldnames}
                missing = REQUIRED_COLUMNS - headers
                if missing:
                    return ImportResult(
                        success=False,
                        imported_count=0,
                        group_id=-1,
                        group_name="",
                        errors=[
                            ImportError(
                                row=0,
                                message="Missing required columns",
                                detail=f"Missing: {', '.join(missing)}",
                            )
                        ],
                    )

                rows = list(reader)

            missing_properties = self._validatePropertyNames(rows)

            if missing_properties:
                property_errors = [
                    ImportError(
                        row=0,
                        message="Property not found in database",
                        detail=f"Missing: {', '.join(missing_properties)}",
                    )
                ]
                return ImportResult(
                    success=False,
                    imported_count=0,
                    group_id=-1,
                    group_name="",
                    errors=property_errors,
                )

            group_count = self._data_groups_repo.count()
            group_name = f"Import {group_count + 1}"
            group_snapshot = self._data_groups_repo.save(
                DataGroupSnapshot(name=group_name)
            )
            group_id = group_snapshot.id

            composition_tool = CompositionTool()
            system_cache: dict[str, int] = {}
            compo_items: list[SystemCompositionSnapshot] = []
            property_values: list[PropertyValueSnapshot] = []
            source_file = file_path.split("/")[-1]

            for row_idx, row in enumerate(rows, start=2):
                system_label = row.get("system_label", "").strip()
                property_name = row.get("property_name", "").strip()
                value_str = row.get("value", "").strip()
                method_name = row.get("method_name", "").strip() or None

                try:
                    value = float(value_str)
                except ValueError:
                    self._data_groups_repo.delete(group_id)
                    return ImportResult(
                        success=False,
                        imported_count=0,
                        group_id=group_id,
                        group_name=group_name,
                        errors=[
                            ImportError(
                                row=row_idx,
                                message="Invalid value",
                                detail=f"'{value_str}' is not a valid number",
                            )
                        ],
                    )

                try:
                    parsed = composition_tool.parseAndValidate(
                        system_label, FractionType.MOLE, max_components=10
                    )
                except CompositionError as e:
                    self._data_groups_repo.delete(group_id)
                    return ImportResult(
                        success=False,
                        imported_count=0,
                        group_id=group_id,
                        group_name=group_name,
                        errors=[
                            ImportError(
                                row=row_idx,
                                message="Failed to parse composition",
                                detail=str(e),
                            )
                        ],
                    )

                if system_label not in system_cache:
                    existing = self._system_repo.findByLabel(system_label)
                    if existing:
                        system_id = existing.id
                    else:
                        system_snapshot = self._system_repo.save(
                            SystemSnapshot(
                                label=system_label, n_component=len(parsed.elements)
                            )
                        )
                        system_id = system_snapshot.id
                        system_cache[system_label] = system_id

                        for elem_symbol, frac in zip(parsed.elements, parsed.fractions):
                            from core.element_map import symbolToId

                            elem_id = symbolToId(elem_symbol)
                            if elem_id is None:
                                self._data_groups_repo.delete(group_id)
                                return ImportResult(
                                    success=False,
                                    imported_count=0,
                                    group_id=group_id,
                                    group_name=group_name,
                                    errors=[
                                        ImportError(
                                            row=row_idx,
                                            message=f"Unknown element: {elem_symbol}",
                                            detail=None,
                                        )
                                    ],
                                )
                            compo_items.append(
                                SystemCompositionSnapshot(
                                    system_id=system_id,
                                    element_id=elem_id,
                                    fraction=frac,
                                )
                            )
                    system_cache[system_label] = system_id
                else:
                    system_id = system_cache[system_label]

                property_snapshot = self._property_repo.findByName(property_name)
                if not property_snapshot:
                    self._data_groups_repo.delete(group_id)
                    return ImportResult(
                        success=False,
                        imported_count=0,
                        group_id=group_id,
                        group_name=group_name,
                        errors=[
                            ImportError(
                                row=row_idx,
                                message=f"Property not found: {property_name}",
                                detail=None,
                            )
                        ],
                    )

                method_id = None
                if method_name:
                    method_snapshot = self._method_repo.findByName(method_name)
                    if method_snapshot:
                        method_id = method_snapshot.id

                pv = PropertyValueSnapshot(
                    system_id=system_id,
                    property_id=property_snapshot.id,
                    value=value,
                    method_id=method_id,
                    group_id=group_id,
                )
                property_values.append(pv)

            if compo_items:
                self._system_composition_repo.insertBatch(compo_items)

            conn = self._db_manager.connection
            conn.execute("BEGIN TRANSACTION")
            try:
                for pv in property_values:
                    pv_record = pv.toRecord()
                    pv_columns = [
                        k
                        for k in pv_record.keys()
                        if k != "id" or pv_record.get("id") is not None
                    ]
                    pv_values = [pv_record[k] for k in pv_columns]
                    placeholders = ", ".join(["?" for _ in pv_columns])
                    sql = f"INSERT INTO property_values ({', '.join(pv_columns)}) VALUES ({placeholders})"
                    cursor = conn.execute(sql, pv_values)
                    value_id = cursor.lastRowId

                    meta = MetaSnapshot(
                        value_id=value_id,
                        created_at=datetime.now(),
                        source_file=source_file,
                        source_type="imported",
                    )
                    meta_record = meta.toRecord()
                    meta_columns = [
                        k
                        for k in meta_record.keys()
                        if k != "id" or meta_record.get("id") is not None
                    ]
                    meta_values = [meta_record[k] for k in meta_columns]
                    meta_sql = f"INSERT INTO meta ({', '.join(meta_columns)}) VALUES ({', '.join(['?' for _ in meta_columns])})"
                    conn.execute(meta_sql, meta_values)

                conn.commit()
            except Exception as e:
                conn.execute("ROLLBACK")
                self._data_groups_repo.delete(group_id)
                return ImportResult(
                    success=False,
                    imported_count=0,
                    group_id=-1,
                    group_name="",
                    errors=[
                        ImportError(row=0, message="Database error", detail=str(e))
                    ],
                )

            self._logger.info(
                f"Imported {len(property_values)} values from {file_path}"
            )
            return ImportResult(
                success=True,
                imported_count=len(property_values),
                group_id=group_id,
                group_name=group_name,
                errors=[],
            )

        except csv.Error as e:
            return ImportResult(
                success=False,
                imported_count=0,
                group_id=-1,
                group_name="",
                errors=[ImportError(row=0, message="CSV parsing error", detail=str(e))],
            )
        except Exception as e:
            self._logger.error(f"Import failed: {e}")
            return ImportResult(
                success=False,
                imported_count=0,
                group_id=-1,
                group_name="",
                errors=[ImportError(row=0, message="Import failed", detail=str(e))],
            )

    def _validatePropertyNames(self, rows: list[dict[str, str]]) -> set[str]:
        property_names = {row.get("property_name", "").strip() for row in rows}
        missing = set()
        for name in property_names:
            if name and not self._property_repo.findByName(name):
                missing.add(name)
        return missing

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

    @property
    def computation_cache_repo(self) -> ComputationCacheRepository:
        return self._computation_cache_repo

    @property
    def property_tags_repo(self) -> PropertyTagsRepository:
        return self._property_tags_repo

    @property
    def data_groups_repo(self) -> DataGroupsRepository:
        return self._data_groups_repo

    @property
    def db_manager(self) -> DatabaseManager:
        return self._db_manager
