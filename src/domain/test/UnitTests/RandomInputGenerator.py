import random
import string


def get_random_string(length=41) -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def get_random_price(start=5, end=555) -> float:
    return random.uniform(start, end)


def get_random_quantity(start=5, end=555) -> int:
    return random.randint(start, end)


def get_random_user() -> tuple[str, str]:
    return get_random_string(), get_random_string()


def get_random_product() -> tuple[str, str, float, int, list]:
    return get_random_string(), get_random_string(), get_random_price(), get_random_quantity(), []
