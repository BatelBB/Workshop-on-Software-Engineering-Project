from abc import ABC, abstractmethod
from functools import wraps
from typing import TypeVar, Generic, Union, Callable

from domain.bussiness_layer_exception import BusinessLayerException
from domain.main.Utils.Logger import Logger


T = TypeVar('T')
R = TypeVar('R')


class ServiceResponse(ABC, Generic[T]):
    @property
    @abstractmethod
    def data(self) -> T:
        """
        :return: data if success. Throws BusinessLayerException if not.
        """
        ...

    @property
    @abstractmethod
    def success(self) -> bool:
        ...

    @property
    @abstractmethod
    def error(self) -> Exception:
        """
        returns error message / exception if is error. Throws otherwise.
        """
        ...

    @property
    def is_error(self) -> bool:
        """
        :return: false is successful, true otherwise.
        """
        return not self.success

    @abstractmethod
    def data_or(self, other: R) -> Union[T, R]:
        """
        returns data if success, returns argument otherwise.
        """
        ...

    @abstractmethod
    def data_or_compute(self, alternative_factory: Callable[[], R]) -> Union[T, R]:
        """
        returns data if success, evaluates and returns argument otherwise.
        """
        ...


class _ResponseOK(ServiceResponse, Generic[T]):
    def __init__(self, data: T):
        self._data = data

    @property
    def data(self) -> T:
        return self._data

    @property
    def success(self) -> bool:
        return True

    @property
    def error(self) -> Exception:
        raise Exception("Tried to retrieve error, but response was succesful")

    def data_or(self, other: R) -> Union[T, R]:
        return self._data

    def data_or_compute(self, alternative_factory: Callable[[], R]) -> Union[T, R]:
        return self._data

    def __str__(self):
        return f"Response[OK, {self._data}]"

    def __repr__(self):
        return str(self)


class _ResponseError(ServiceResponse, Generic[T]):
    def __init__(self, err: Union[str, Exception]):
        self._error = err if isinstance(err, BusinessLayerException) else BusinessLayerException(err)

    @property
    def data(self) -> T:
        raise self._error

    @property
    def success(self) -> bool:
        return False

    @property
    def error(self) -> Exception:
        return self._error

    def data_or(self, other: R) -> Union[T, R]:
        return other

    def data_or_compute(self, alternative_factory: Callable[[], R]) -> Union[T, R]:
        return alternative_factory()

    def __str__(self):
        return f"Response[Error, {self._error}]"

    def __repr__(self):
        return str(self)


def ok(result: T) -> ServiceResponse[T]:
    return _ResponseOK(result)


def error(err: Union[str, Exception]) -> ServiceResponse[T]:
    return _ResponseError(err)


def _repr_args(*args):
    return ', '.join(map(repr, args))


def _repr_kwargs(**kwargs):
    return ', '.join(f"{k}={repr(v)}" for k, v in kwargs.items())


def returns_responses(fn: Callable, logged: bool = True):
    """
    decorate a function that throws to create a function that returns responses.
    example:

    .. highlight: python
    .. code-block:: python
        @returns_responses
        def foo(i):
            if not instanceof(i, int):
                raise BusinessLayerException("not a number")
            if i == 0:
                return ok("zero")
            return "not zero"

        foo(0) => OKResponse("zero")
        foo(1) => OKResponse("not zero")
        foo("x") => ErrorResponse("not a number")

    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            fn_res = fn(*args, **kwargs)
            response = fn_res if isinstance(fn_res, ServiceResponse) else ok(fn_res)
        except Exception as e:
            response = error(e)

        if logged:
            args_part = _repr_args(*args)
            kwargs_part = _repr_kwargs(**kwargs)
            msg = f"{fn.__name__}(\t{args_part}, {kwargs_part}\t) => {response}"
            Logger().post(msg, severity=Logger.Severity.INFO if response.success else Logger.Severity.ERROR)
        return response

    return wrapper
