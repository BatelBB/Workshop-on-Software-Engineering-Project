from typing import TypeVar, Generic

Result = TypeVar('Result')


class Response(Generic[Result]):

    def __init__(self, result: Result, description: str = ""):
        self.result = result
        self.description = description
        # TODO make success a boolean argument instead of using 'result is not None'.
        if self.result is None:
            self.success = False
        elif not self.result:
            self.success = False
        else:
            self.success = True


    def __str__(self):
        return f'Request result is: {self.result}\nDescription: {self.description}'

