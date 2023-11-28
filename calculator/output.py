from abc import ABCMeta
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import get_args
from typing import Type
from typing import TypeVar

from calculator.elliptic import Point
from calculator.polynomial import Polynomial
from calculator.task import TaskConfig
from calculator.task import TaskResult
from calculator.task import TaskType


T = TypeVar('T')


def _get_generic_type(instance: Any):
    instance_cls = instance.__class__
    generic_type = get_args(instance_cls.__orig_bases__[0])[0]

    return generic_type


class Formatter(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def format(self, item: T) -> str:
        raise NotImplementedError


class FormattersRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, formatter: Formatter):
        generic_type = _get_generic_type(formatter)
        self._registry[generic_type] = formatter

    def get(self, type_: Type):
        try:
            return self._registry[type_]
        except KeyError:
            raise ValueError(f'Форматтер для данного типа {type_} не зарегистрирован')


class IntFormatter(Formatter[int]):
    def format(self, item: int) -> str:
        return str(item)


class PolynomialFormatter(Formatter[Polynomial]):
    def __init__(self, int_formatter: IntFormatter):
        self._int_formatter = int_formatter

    def format(self, item: Polynomial) -> str:
        return self._int_formatter.format(item.bits)


class PointFormatter(Formatter[Point]):
    def __init__(self, formatters_registry: FormattersRegistry):
        self._registry = formatters_registry

    def format(self, item: Point) -> str:
        if item.is_infinite():
            return 'O'

        formatter = self._registry.get(type(item.x))
        x_str = formatter.format(item.x)
        y_str = formatter.format(item.y)

        return f'({x_str}, {y_str})'


class TaskConfigFormatter(Formatter[TaskConfig]):
    def __init__(
        self,
        point_formatter: PointFormatter,
        int_formatter: IntFormatter,
    ):
        self._point_formatter = point_formatter
        self._int_formatter = int_formatter

    def format(self, item: TaskConfig) -> str:
        if item.task_type is TaskType.MUL:
            point = self._point_formatter.format(item.points[0])
            scalar = self._int_formatter.format(item.scalar)
            return f'{point} * {scalar}'

        if item.task_type is TaskType.ADD:
            points = [
                self._point_formatter.format(point,)
                for point in item.points
            ]
            return ' + '.join(points)

        raise ValueError(f'Операция {item.task_type} не распознана')


class TaskResultFormatter(Formatter[TaskResult]):
    def __init__(
        self,
        task_config_formatter: TaskConfigFormatter,
        point_formatter: PointFormatter,
    ):
        self._task_config_formatter = task_config_formatter
        self._point_formatter = point_formatter

    def format(self, item: TaskResult) -> str:
        task_config_str = self._task_config_formatter.format(item.task_config)
        result = self._point_formatter.format(item.result)

        return f'{task_config_str} = {result}'
