from typing import TypeVar, Generic, Union, Callable

Result = TypeVar('Result')
T = TypeVar('T')

class BusinessLayerException(Exception):
    pass


class Response(Generic[Result]):
    def __init__(self, result: Result, description: str = ""):
        self.result = result
        self.description = description
        # TODO make success a boolean argument instead of using 'result is not None'.
        self.success = result is not None

    def __str__(self):
        return f'Request result is: {self.result}\nDescription: {self.description}'

    def get_or_throw(self) -> Result:
        if self.success:
            return self.result
        raise BusinessLayerException(self.description)

    def get_or(self, other: T) -> Union[T, Result]:
        return self.result if self.success else other

    def get_or_compute(self, alternative_provider: Callable[[], T]) -> Union[T, Result]:
        return self.result if self.result else alternative_provider()
