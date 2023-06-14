
from typing import TypeVar, Iterator

T = TypeVar('T')


class MultipleFoundException(Exception):
    ...


class NoneFoundException(Exception):
    ...


def single(iterable: Iterator[T]) -> T:
    found = False
    ret: T = None
    for it in iterable:
        if not found:
            ret, found = it, True
        else:
            raise MultipleFoundException("single: multiple found")
    if not found:
        raise NoneFoundException("single: none found")
    return ret


def single_or_default(iterable: Iterator[T], default: T) -> T:
    found = False
    ret: T = None
    for it in iterable:
        if not found:
            ret, found = it, True
        else:
            raise MultipleFoundException("single: multiple found")
    if not found:
        return default
    return ret
