class DataModuleRegistry:
    _tables: dict[type, tuple[str, type]] = {}

    @classmethod
    def register(cls, snapshot_class: type, table_name: str) -> None:
        cls._tables[snapshot_class] = (table_name, snapshot_class)

    @classmethod
    def getTableInfo(cls, snapshot_class: type) -> tuple[str, type] | None:
        return cls._tables.get(snapshot_class)

    @classmethod
    def findByTableName(cls, table_name: str) -> type | None:
        for snapshot_class, (name, _) in cls._tables.items():
            if name == table_name:
                return snapshot_class
        return None

    @classmethod
    def listRegistered(cls) -> list[tuple[str, type]]:
        return [(name, cls) for cls, (name, cls) in cls._tables.items()]
