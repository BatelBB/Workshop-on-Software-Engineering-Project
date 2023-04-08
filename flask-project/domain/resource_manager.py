from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')
TCreateDto = TypeVar('TCreateDto')
TUpdateDto = TypeVar('TUpdateDto')


class IResourceManager(ABC, Generic[T, TCreateDto, TUpdateDto]):   # abstract class IResourceManager<T>
    @abstractmethod
    def create(self, dto: TCreateDto) -> T:
        ...

    @abstractmethod
    def update(self, thing: T, update: TUpdateDto) -> T:
        ...

    @abstractmethod
    def delete(self, thing: T):
        ...

    def get_all(self):
        ...

    def get_one(self, search_params):
        ...
