from typing import Callable


class DataSourceRegistry:
    _factories: dict[str, Callable] = {}

    @classmethod
    def register(cls, tag: str, factory: Callable) -> None:
        cls._factories[tag] = factory

    @classmethod
    def getFactory(cls, tag: str) -> Callable | None:
        return cls._factories.get(tag)

    @classmethod
    def create(cls, tag: str, *args, **kwargs):
        factory = cls._factories.get(tag)
        if factory is None:
            return None
        return factory(*args, **kwargs)

    @classmethod
    def findByTag(
        cls,
        required_tags: list[str],
        accepted_tags: list[str],
        module_service=None,
    ) -> list:
        candidates = []
        seen = set()

        for tag in required_tags:
            if tag == "Any":
                for t, factory in cls._factories.items():
                    source = factory(module_service) if module_service else factory()
                    if id(source) not in seen:
                        candidates.append(source)
                        seen.add(id(source))
            else:
                factory = cls._factories.get(tag)
                if factory is not None:
                    source = factory(module_service) if module_service else factory()
                    if id(source) not in seen:
                        candidates.append(source)
                        seen.add(id(source))

        if "Any" in accepted_tags:
            return candidates

        filtered = []
        for source in candidates:
            source_tags = getattr(source, "tags", [])
            if any(tag in accepted_tags for tag in source_tags):
                filtered.append(source)

        return filtered
