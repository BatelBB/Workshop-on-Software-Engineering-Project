from typing import TypeVar, Iterable, Optional, Callable

T = TypeVar('T')


def count_if(src: Iterable[T], cond: Optional[Callable[[T], bool]] = None):
    if cond is None:
        cond = lambda _: True

    return sum(1 for i in src if cond(i))
