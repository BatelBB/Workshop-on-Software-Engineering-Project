from typing import Callable

def dicebear(seed: str, style: str) -> str:
    return f"https://api.dicebear.com/6.x/{style}/png?seed={seed.upper()}"


def dicebear_user(seed: str) -> str:
    return dicebear(seed, 'bottts')


def dicebear_product(seed: str) -> str:
    return dicebear(seed, "icons")

def dicebear_shop(shop: str) -> str:
    return dicebear(shop, "thumbs")


dicebear_methods = {
    m.__qualname__: m
    for m in (dicebear, dicebear_user, dicebear_shop, dicebear_product, dicebear_shop)
}

dicebear_methods["dicebear_store"] = dicebear_shop