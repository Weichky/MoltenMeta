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
    def findByTag(cls, tag: str, module_service=None):
        factory = cls._factories.get(tag)
        if factory is None:
            return []
        if module_service is not None:
            return [factory(module_service)]
        return [factory()]
