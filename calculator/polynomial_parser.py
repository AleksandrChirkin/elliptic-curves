import re

from calculator.common import parse_int
from calculator.errors import PolynomialParseError
from calculator.polynomial import Polynomial


class _GF2IrreduciblePolynomialParser:
    MONOMIAL_PATTERN = re.compile(r'^(?:((?:0x|0o|0b)?\d+)\*?)?x(?:\^((?:0x|0o|0b)?\d+))?$')

    @classmethod
    def parse(cls, polynomial_raw: str) -> Polynomial:
        polynomial_raw = (
            polynomial_raw
            .replace(' ', '')
            .replace('-', '+')
            .strip(' +')
        )

        polynomial_powers = []
        for monomial_raw in polynomial_raw.split('+'):
            monomial_raw = monomial_raw.strip()

            if monomial_raw.isnumeric():
                scalar = parse_int(monomial_raw) % 2

                if scalar != 0:
                    polynomial_powers.append(0)

                continue

            match = cls.MONOMIAL_PATTERN.match(monomial_raw)

            if match is None:
                raise PolynomialParseError(monomial_raw, polynomial_raw)

            scalar = 1
            if match.group(1) is not None:
                scalar = parse_int(match.group(1)) % 2

            power = parse_int(match.group(2) or '1')

            if scalar != 0:
                polynomial_powers.append(power)

        if len(polynomial_powers) != 0:
            polynomial_array = [0] * (max(polynomial_powers) + 1)

            for power in polynomial_powers:
                polynomial_array[power] = 1

            return Polynomial(polynomial_array)

        return Polynomial(0)


def parse_polynomial(polynomial: str) -> Polynomial:
    return _GF2IrreduciblePolynomialParser.parse(polynomial)
