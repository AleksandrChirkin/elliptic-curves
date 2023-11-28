from collections.abc import Iterable as IterableABC
from typing import Any
from typing import Iterable
from typing import Union

from calculator.utils import convert_bits_array_to_num
from calculator.utils import convert_num_to_bits_array


class Polynomial:
    def __init__(self, num_or_bits: Union[int, Iterable[Union[int, float]]]):
        if isinstance(num_or_bits, IterableABC):
            self._bits = convert_bits_array_to_num(num_or_bits)
        else:
            self._bits = num_or_bits

    @property
    def bits(self):
        return self._bits

    def __eq__(self, other: Any):
        if not isinstance(other, Polynomial):
            raise ValueError('Для сравнения нужны оба полинома')

        return self.bits == other.bits

    def __add__(self, other: 'Polynomial') -> 'Polynomial':
        return Polynomial(self.bits ^ other.bits)

    def __sub__(self, other: 'Polynomial') -> 'Polynomial':
        return self + other

    def __len__(self):
        return self.bits.bit_length()

    def __mul__(self, other: 'Polynomial') -> 'Polynomial':
        result, addend = Polynomial(0), Polynomial(self.bits)
        otherbits = other.bits

        while otherbits:
            shift = otherbits & 1

            if shift:
                result += addend

            addend <<= 1
            otherbits >>= 1

        return result

    def __mod__(self, other: 'Polynomial') -> 'Polynomial':
        self_polynomial = Polynomial(self.bits)

        while len(self_polynomial) >= len(other):
            len_dif = len(self_polynomial) - len(other)
            self_polynomial += Polynomial(other.bits << len_dif)

        return self_polynomial

    def __lshift__(self, other: int) -> 'Polynomial':
        return Polynomial(self.bits << other)

    def __rshift__(self, other: int) -> 'Polynomial':
        return Polynomial(self.bits >> other)

    def __floordiv__(self, divisor: 'Polynomial'):
        quotient = Polynomial(0)
        remainder = Polynomial(self.bits)

        while len(remainder) >= len(divisor):
            product = Polynomial(1 << (len(remainder) - len(divisor)))
            quotient += product
            remainder += product * divisor

        return quotient

    def __repr__(self):
        bits_array = convert_num_to_bits_array(self.bits)
        polynomial = []

        for index, value in enumerate(bits_array):
            if value == 1:
                polynomial.append(f'x^{index}')

        return ' + '.join(polynomial)
