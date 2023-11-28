import re
from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Generic
from typing import Iterator
from typing import List
from typing import TypeVar
from typing import Union

from calculator.elliptic import Point
from calculator.common import parse_int
from calculator.errors import ParserError
from calculator.polynomial_parser import parse_polynomial
from calculator.polynomial import Polynomial
from calculator.task import FieldType
from calculator.task import TaskConfig
from calculator.task import TaskRunnerConfig
from calculator.task import TaskType


T = TypeVar('T')


class ArgsProvider(metaclass=ABCMeta):
    @abstractmethod
    def provide(self, input_lines: Iterator[str]) -> List[Any]:
        raise NotImplementedError


class ZpFieldArgsProvider(ArgsProvider):
    def provide(self, input_lines: Iterator[str]) -> List[Any]:
        return [parse_int(next(input_lines))]


class ZpCurveArgsProvider(ArgsProvider):
    def provide(self, input_lines: Iterator[str]) -> List[Any]:
        return [parse_int(next(input_lines)), parse_int(next(input_lines))]


class GF2FieldArgsProvider(ArgsProvider):
    def provide(self, input_lines: Iterator[str]) -> List[Any]:
        value = next(input_lines)
        if 'x' in value:
            return [parse_polynomial(value)]
        return [parse_int(value)]


class GF2CurveArgsProvider(ArgsProvider):
    def provide(self, input_lines: Iterator[str]) -> List[Any]:
        return [
            parse_int_polynomial(next(input_lines)),
            parse_int_polynomial(next(input_lines)),
            parse_int_polynomial(next(input_lines)),
            parse_int_polynomial(next(input_lines)),
            parse_int_polynomial(next(input_lines)),
        ]


def parse_int_polynomial(number_str: str) -> Polynomial:
    return Polynomial(parse_int(number_str))


@dataclass
class FieldConfigurator:
    field_type: FieldType
    field_args_provider: ArgsProvider
    curve_args_provider: ArgsProvider


FIELDS_CONFIGURATORS_MAP = {
    'Z_p': FieldConfigurator(
        field_type=FieldType.Z_p,
        field_args_provider=ZpFieldArgsProvider(),
        curve_args_provider=ZpCurveArgsProvider(),
    ),
    'GF(2^n)': FieldConfigurator(
        field_type=FieldType.GF,
        field_args_provider=GF2FieldArgsProvider(),
        curve_args_provider=GF2CurveArgsProvider(),
    ),
}


PARSE_POINT_OPERAND_FUNCTIONS_MAP = {
    FieldType.Z_p: parse_int,
    FieldType.GF: parse_int_polynomial,
}


TASKS_TYPES_MAP = {
    'a': TaskType.ADD,
    'm': TaskType.MUL,
}


class _ParserContext(Generic[T]):
    POINT_SANITIZER_PATTERN = re.compile(r'(?:(?<!\()\s+(?!\))|(?<=\()\s+|\s+(?=\)))')
    TOKENS_DELIMITER = re.compile(r'\s+')
    POINT_PATTERN = re.compile(r'\(\s*((?:0x|0o|0b)?[\dabcdef]+)\s*,\s*((?:0x|0o|0b)?[\dabcdef]+)\s*\)')

    def __init__(
        self,
        configurator: FieldConfigurator,
        parse_point_operand_function: Callable[[str], T],
    ):
        self._configurator = configurator
        self._parse_point_operand_function = parse_point_operand_function

    def do_parse(self, input_lines: Iterator[str]) -> TaskRunnerConfig[T]:
        field_args = self._configurator.field_args_provider.provide(input_lines)
        curve_args = self._configurator.curve_args_provider.provide(input_lines)
        task_configs = [self._parse_task(line) for line in input_lines]

        return TaskRunnerConfig(
            field_type=self._configurator.field_type,
            field_args=field_args,
            curve_args=curve_args,
            task_configs=task_configs,
        )

    def _parse_task(self, line: str) -> TaskConfig[T]:
        line = line.lower().strip()
        line = self.POINT_PATTERN.sub(r'(\1,\2)', line)

        try:
            task_type, operand_1, operand_2 = self.TOKENS_DELIMITER.split(line.lower())
        except ValueError:
            raise ParserError(f'Ошибка парсинга задачи: {line}')

        try:
            task_type = TASKS_TYPES_MAP[task_type]
        except KeyError:
            raise ParserError(f'Неизвестный тип операции: {line}')

        scalars = []
        points = []

        for operand in operand_1, operand_2:
            operand = self._parse_task_operand(operand)

            if isinstance(operand, int):
                scalars.append(operand)
            else:
                points.append(operand)

        if task_type is TaskType.ADD:
            if len(points) != 2:
                raise ValueError(f'Для операции сложения оба операнда должны быть точки: {line}')

            return TaskConfig(task_type, points=tuple(points))  # noqa

        if task_type is TaskType.MUL:
            if len(points) != 1 or len(scalars) != 1:
                raise ValueError(f'Для операции умножения один операнда - точка, второй - скаляр: {line}')

            return TaskConfig(task_type, points=tuple(points), scalar=scalars[0])  # noqa

    def _parse_task_operand(self, operand: str) -> Union[int, Point[T]]:
        if '(' not in operand:
            return parse_int(operand)

        match = self.POINT_PATTERN.match(operand)

        if match is None:
            raise ParserError(f'Неверный формат точки: {operand}')

        return Point(
            x=self._parse_point_operand_function(match.group(1)),
            y=self._parse_point_operand_function(match.group(2)),
        )


class Parser:
    @staticmethod
    def parse(input_lines: Iterator[str]) -> TaskRunnerConfig:
        field_type = next(input_lines).strip()

        if field_type not in FIELDS_CONFIGURATORS_MAP:
            raise ParserError(f'Неизвестный тип поля: {field_type}')

        configurator = FIELDS_CONFIGURATORS_MAP[field_type]
        parse_point_operand_function = (
            PARSE_POINT_OPERAND_FUNCTIONS_MAP[configurator.field_type]
        )

        parser_ctx = _ParserContext(configurator, parse_point_operand_function)

        try:
            return parser_ctx.do_parse(input_lines)
        except ParserError:
            raise
        except Exception as e:
            raise ParserError(e) from e
