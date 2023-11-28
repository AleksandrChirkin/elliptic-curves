from calculator.polynomial_parser import parse_polynomial
from calculator.errors import UnknownIrreduciblePolynomialPower
from calculator.polynomial import Polynomial

GF2_IRREDUCIBLE_POLYNOMIALS_DIRECTORY = {
    2: 'x^2+x+1',
    3: 'x^3+x+1',
    4: 'x^4+x+1',
    5: 'x^5+x^2+1',
    6: 'x^6+x+1',
    7: 'x^7+x^3+1',
    8: 'x^8+x^4+x^3+x^2+1',
    9: 'x^9+x^4+1',
    10: 'x^10+x^3+1',
    11: 'x^11+x^2+1',
    12: 'x^12+x^6+x^4+x+1',
    13: 'x^13+x^4+x^3+x+1',
    14: 'x^14+x^10+x^6+x+1',
    15: 'x^15+x+1',
    16: 'x^16+x^12+x^3+x+1',
    17: 'x^17+x^3+1',
    18: 'x^18+x^7+1',
    19: 'x^19+x^5+x^2+x+1',
    20: 'x^20+x^3+1',
    21: 'x^21+x^2+1',
    22: 'x^22+x+1',
    23: 'x^23+x^5+1',
    24: 'x^24+x^7+x^2+x+1',
    25: 'x^25+x^3+1',
    26: 'x^26+x^6+x^2+x+1',
    27: 'x^27+x^5+x^2+x+1',
    28: 'x^28+x^3+1',
    29: 'x^29+x^2+1',
    30: 'x^30+x^23+x^2+x+1',
    31: 'x^31+x^3+1',
    32: 'x^32+x^22+x^2+x+1',
    36: 'x^36+x^11+1',
    40: 'x^40+x^9+x^3+x+1',
    48: 'x^48+x^28+x^3+x+1',
    56: 'x^56+x^42+x^2+x+1',
    64: 'x^64+x^46+x^4+x+1',
    72: 'x^72+x^62+x^3+x^2+1',
    80: 'x^80+x^54+x^2+x+1',
    96: 'x^96+x^31+x^4+x+1',
    128: 'x^128+x^7+x^2+x+1',
    160: 'x^160+x^19+x^4+x+1',
    163: 'x^163+x^7+x^6+x^3+1',  # NIST
    192: 'x^192+x^107+x^4+x+1',
    233: 'x^233+x^74+1',  # NIST
    256: 'x^256+x^16+x^3+x+1',
    283: 'x^283+x^12+x^7+x^5+1',  # NIST
    409: 'x^409+x^87+1',  # NIST
    571: 'x^571+x^10+x^5+x^2+1',  # NIST
}


def get_irreducible_polynomial(power: int) -> Polynomial:
    if power not in GF2_IRREDUCIBLE_POLYNOMIALS_DIRECTORY:
        raise UnknownIrreduciblePolynomialPower(power)

    polynomial = GF2_IRREDUCIBLE_POLYNOMIALS_DIRECTORY[power]

    return parse_polynomial(polynomial)
