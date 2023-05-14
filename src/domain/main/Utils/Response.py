from typing import TypeVar, Generic

Result = TypeVar('Result')


class Response(Generic[Result]):

    def __init__(self, result: Result = None, description: str = ""):
        self.result = result
        self.description = description
        if self.result is None:
            self.success = False
        else:
            self.success = True

    def __str__(self):
        return f'Request result is: {self.result}\nDescription: {self.description}'

