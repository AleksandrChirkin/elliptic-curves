from typing import Iterable
from typing import List
from typing import Union


def convert_num_to_bits_array(number: int) -> List[int]:
    bits = list(map(int, list('{0:0b}'.format(number))[::-1]))
    return bits


def convert_bits_array_to_num(bits: Iterable[Union[int, float]]):
    bits_raw = ''.join([str(int(bit)) for bit in bits[::-1]])
    return int(bits_raw, base=2)
