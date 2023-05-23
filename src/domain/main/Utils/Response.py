from typing import TypeVar, Generic

Result = TypeVar('Result')


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

