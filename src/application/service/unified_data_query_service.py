from core.log import LogService
from application.service.user_db_service import UserDbService


class UnifiedDataQueryService:
    """Business-level query service for unified data access."""

    def __init__(self, log_service: LogService, user_db_service: UserDbService):
        self._logger = log_service.getLogger(__name__)
        self._user_db = user_db_service

    def findByPropertyId(self, property_id: int) -> list[dict]:
        """Query both property_values and computation_cache for property_id."""
        results = []

        pv_list = self._user_db.property_value_repo.findByPropertyId(property_id)
        for pv in pv_list:
            results.append(
                {
                    "source_type": "property_value",
                    "id": pv.id,
                    "system_id": pv.system_id,
                    "property_id": pv.property_id,
                    "value": pv.value,
                    "method_id": pv.method_id,
                    "group_id": pv.group_id,
                }
            )

        cc_list = self._user_db.computation_cache_repo.findByPropertyId(property_id)
        for cc in cc_list:
            results.append(
                {
                    "source_type": "computation",
                    "id": cc.id,
                    "system_id": cc.system_id,
                    "property_id": cc.property_id,
                    "value": cc.value,
                    "module_id": cc.module_id,
                    "run_id": cc.run_id,
                    "parent_run_id": cc.parent_run_id,
                    "group_id": cc.group_id,
                }
            )

        return results

    def findByTag(self, tag: str) -> list[dict]:
        """Find all data by tag."""
        property_ids = self._user_db.property_tags_repo.getPropertyIdsByTag(tag)
        if not property_ids:
            return []

        results = []
        for pid in property_ids:
            results.extend(self.findByPropertyId(pid))
        return results

    def findByGroup(self, group_id: int | None) -> list[dict]:
        """Find all data in a group. group_id=None means ungrouped."""
        results = []

        if group_id is None:
            pv_list = self._user_db.property_value_repo.findAll()
            for pv in pv_list:
                if pv.group_id is None:
                    results.append(
                        {
                            "source_type": "property_value",
                            "id": pv.id,
                            "system_id": pv.system_id,
                            "property_id": pv.property_id,
                            "value": pv.value,
                            "method_id": pv.method_id,
                            "group_id": pv.group_id,
                        }
                    )

            cc_list = self._user_db.computation_cache_repo.findAll()
            for cc in cc_list:
                if cc.group_id is None:
                    results.append(
                        {
                            "source_type": "computation",
                            "id": cc.id,
                            "system_id": cc.system_id,
                            "property_id": cc.property_id,
                            "value": cc.value,
                            "module_id": cc.module_id,
                            "run_id": cc.run_id,
                            "parent_run_id": cc.parent_run_id,
                            "group_id": cc.group_id,
                        }
                    )
        else:
            pv_list = self._user_db.property_value_repo.findByGroupId(group_id)
            for pv in pv_list:
                results.append(
                    {
                        "source_type": "property_value",
                        "id": pv.id,
                        "system_id": pv.system_id,
                        "property_id": pv.property_id,
                        "value": pv.value,
                        "method_id": pv.method_id,
                        "group_id": pv.group_id,
                    }
                )

            cc_list = self._user_db.computation_cache_repo.findByGroupId(group_id)
            for cc in cc_list:
                results.append(
                    {
                        "source_type": "computation",
                        "id": cc.id,
                        "system_id": cc.system_id,
                        "property_id": cc.property_id,
                        "value": cc.value,
                        "module_id": cc.module_id,
                        "run_id": cc.run_id,
                        "parent_run_id": cc.parent_run_id,
                        "group_id": cc.group_id,
                    }
                )

        return results
