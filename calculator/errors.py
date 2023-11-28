class PolynomialException(Exception):
    pass


class UnknownIrreduciblePolynomialPower(PolynomialException):
    def __init__(self, power: int):
        super().__init__(f'Я не знаю неприводимого полинома степени {power=} над GF(2^power)')


class ParserError(Exception):
    pass


class PolynomialParseError(ParserError):
    def __init__(self, monomial_raw: str, polynomial_raw: str):
        super().__init__(f'Ошибка при парсинге одночлена: {monomial_raw} (полином: {polynomial_raw})')


class EllipticCurveError(Exception):
    pass


class CalculationError(EllipticCurveError):
    pass
