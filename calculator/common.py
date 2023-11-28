from typing import Tuple
from typing import Union


def parse_int(number_str: str) -> Union[int, Tuple[int, int]]:
    base = 10
    if number_str.startswith('0b'):
        base = 2
    if number_str.startswith('0o'):
        base = 8
    if number_str.startswith('0x'):
        base = 16
    return int(number_str, base)
