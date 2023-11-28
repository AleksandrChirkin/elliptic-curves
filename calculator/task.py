from dataclasses import dataclass
from enum import auto
from enum import Enum
from typing import Generic
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union

from calculator.elliptic import Curve
from calculator.elliptic import GF2NotSupersingularCurve
from calculator.elliptic import GF2SupersingularCurve
from calculator.elliptic import Point
from calculator.elliptic import ZpCurve
from calculator.irreducible import get_irreducible_polynomial
from calculator.polynomial import Polynomial


T = TypeVar('T')


class TaskType(Enum):
    ADD = auto()
    MUL = auto()


class FieldType(Enum):
    Z_p = auto()
    GF = auto()


@dataclass(unsafe_hash=True)
class TaskConfig(Generic[T]):
    task_type: TaskType
    points: Union[
        Tuple[Point[T], Point[T]],
        Tuple[Point[T]],
    ]
    scalar: Optional[int] = None


@dataclass(unsafe_hash=True)
class TaskResult(Generic[T]):
    task_config: TaskConfig[T]
    result: Point[T]


@dataclass(unsafe_hash=True)
class TaskRunnerConfig(Generic[T]):
    field_type: FieldType
    field_args: List[Union[int, Polynomial]]
    curve_args: List[Union[int, Polynomial]]
    task_configs: List[TaskConfig[T]]

    def build_runner(self):
        curve = None

        if self.field_type is FieldType.Z_p:
            curve = ZpCurve(*self.field_args, *self.curve_args)
        elif self.field_type is FieldType.GF:
            p: Union[int, Polynomial] = self.field_args[0]
            if isinstance(p, int):
                p = get_irreducible_polynomial(power=p)
            try:
                a1, a2, a3, a4, a5 = self.curve_args
            except ValueError:
                raise ValueError('Неверное число коэффициентов эллиптической кривой')

            bool_args = list(map(lambda poly: bool(poly.bits), self.curve_args))
            if bool_args == [True, False, True, False, True]:
                curve = GF2NotSupersingularCurve(p, a1, a3, a5)
            elif bool_args == [False, True, False, True, True]:
                curve = GF2SupersingularCurve(p, a2, a4, a5)
            else:
                raise ValueError('Неизвестная комбинация коэффициентов эллиптической кривой для конечного поля')

        return TaskRunner(curve=curve)


@dataclass
class TaskRunner:
    curve: Curve[T]

    def run(self, tasks: List[TaskConfig[T]]) -> Iterable[TaskResult[T]]:
        for task in tasks:
            yield self._run_task(task)

    def _run_task(self, task: TaskConfig) -> TaskResult[T]:
        if task.task_type is TaskType.ADD:
            result = self.curve.add(task.points[0], task.points[1])
        elif task.task_type is TaskType.MUL:
            result = self.curve.mul(task.points[0], task.scalar)
        else:
            raise ValueError(f'Операция {task.task_type} не распознана')
        return TaskResult(task, result)
