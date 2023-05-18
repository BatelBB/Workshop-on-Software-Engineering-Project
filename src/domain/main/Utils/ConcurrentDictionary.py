import threading
from typing import TypeVar, Generic

Key = TypeVar('Key')
Value = TypeVar('Value')


class ConcurrentDictionary(Generic[Key, Value]):
    def __init__(self):
        self.lock = threading.RLock()
        self.dictionary: dict[Key, Value] = dict()

    def __str__(self):
        with self.lock:
            for _, value in self.dictionary:
                return value

    def is_empty(self) -> bool:
        return len(self.dictionary) == 0

    def to_string_keys(self) -> str:
        output: str = str()
        for key, _ in self.dictionary.items():
            output += f'{key}, '
        return output[0: len(output) - 2]

    def to_string_values(self) -> str:
        output: str = str()
        for _, value in self.dictionary.items():
            output += f'{value}, '
        return output[0: len(output) - 2]

    def insert(self, key: Key, value: Value) -> Value:
        with self.lock:
            previous_value = self.delete(key)
            self.dictionary[key] = value
            return previous_value

    def delete(self, key: Key) -> Value:
        with self.lock:
            previous_value = self.dictionary.pop(key, None)
            return previous_value

    def get(self, key: Key) -> Value:
        with self.lock:
            if key in self.dictionary:
                return self.dictionary[key]
            return None

    def get_all(self) -> dict[Key, Value]:
        return self.dictionary

    def get_all_keys(self) -> list[Key]:
        return list(self.dictionary.keys())

    def get_all_values(self) -> list[Value]:
        return list(self.dictionary.values())

    def update(self, key: Key, new_value: Value):
        with self.lock:
            self.dictionary[key] = new_value

    def list_keys(self):
        with self.lock:
            return list(self.dictionary.keys())

    def list_entries(self):
        with self.lock:
            return list(self.dictionary.items())