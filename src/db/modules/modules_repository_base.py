from db.base_repository import BaseRepository


class ModulesRepositoryBase(BaseRepository):
    def __init__(self, connection, dialect):
        super().__init__(connection, dialect)

    def getTableName(self) -> str:
        raise NotImplementedError("Subclass must implement getTableName()")

    def getEntityClass(self) -> type:
        raise NotImplementedError("Subclass must implement getEntityClass()")

    def createTable(self) -> None:
        sql = self._getCreateTableSql()
        self.connection.execute(sql)
        self.connection.commit()
