from typing import TypeVar, Generic

Result = TypeVar('Result')


class Response(Generic[Result]):

    def __init__(self, result: Result, description: str = ""):
        self.result = result
        self.description = description

    def __str__(self):
        return f'Request result is: {self.result}\nDescription: {self.description}'

    def is_succeed(self):
        return self.result
