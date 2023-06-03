from typing import TypeVar, Any, Callable, Optional

T = TypeVar('T')


def tap(value: T, callback: Callable[[T], Any]) -> T:
    callback(value)
    return value


def tap_print(value: T, print_name: Optional[str] = None):
    return tap(value, lambda x: print(f"tap_print[{print_name or ''}]", value))
