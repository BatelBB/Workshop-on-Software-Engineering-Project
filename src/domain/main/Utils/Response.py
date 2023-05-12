from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class Response(Generic[T]):
    """
    A class to encapsulate the response of a function or method call, including the result and a description.
    """
    def __init__(self, result: Optional[T] = None, description: str = ""):
        """
        Constructs a new 'Response' object.

        :param result: The result of the function or method call, defaults to None
        :param description: A description of the response, defaults to an empty string
        """
        self._result = result
        self._description = description
        self._success = self._result is not None

    @property
    def result(self) -> Optional[T]:
        """
        Returns the result of the function or method call.
        """
        return self._result

    @property
    def description(self) -> str:
        """
        Returns the description of the response.
        """
        return self._description

    @property
    def success(self) -> bool:
        """
        Returns a boolean indicating whether the function or method call was successful.
        """
        return self._success
