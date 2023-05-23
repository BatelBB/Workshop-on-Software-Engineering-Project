from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Union

T = TypeVar('T')
R = TypeVar('R')

class ServiceResponse(ABC):
    def __init__(self, data: Union[T, str, Exception]):
        self._data = data

    @property
    def data(self) -> Union[T, str, Exception]:
        return self._data

    @property
    @abstractmethod
    def success(self) -> bool:
        ...

    @property
    def is_error(self) -> bool:
        return not self.success

    