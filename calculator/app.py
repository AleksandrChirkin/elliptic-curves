import glob
import os.path
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor

from calculator.output import FormattersRegistry
from calculator.output import IntFormatter
from calculator.output import PointFormatter
from calculator.output import PolynomialFormatter
from calculator.output import TaskConfigFormatter
from calculator.output import TaskResultFormatter
from calculator.parser import Parser

parser = Parser()
registry = FormattersRegistry()
int_formatter = IntFormatter()
polynomial_formatter = PolynomialFormatter(int_formatter)
point_formatter = PointFormatter(registry)
task_config_formatter = TaskConfigFormatter(point_formatter, int_formatter)
task_result_config = TaskResultFormatter(task_config_formatter, point_formatter)

registry.register(int_formatter)
registry.register(polynomial_formatter)
registry.register(point_formatter)
registry.register(task_config_formatter)
registry.register(task_result_config)


def _check_error(future: Future):
    if future.exception() is not None:
        item = future.exception()
        raise RuntimeError(f'Ошибка: {item}')


def run(filename: str, output: str):
    input_f = open(filename, 'r')
    filename = os.path.basename(filename)

    config = parser.parse(input_lines=iter(input_f))
    task_runner = config.build_runner()

    with open(os.path.join(output, filename), 'w') as output_f:
        for task_result in task_runner.run(config.task_configs):
            task_result_str = task_result_config.format(task_result)
            output_f.write(task_result_str + os.linesep)


def run_on_directory(input: str, output: str):
    if not os.path.exists(output):
        try:
            os.mkdir(output)
        except FileNotFoundError:
            return
    with ThreadPoolExecutor() as executor:
        pattern = os.path.join(input, '*.txt')
        for filename in glob.iglob(pattern):
            future = executor.submit(run, filename, output)
            future.add_done_callback(_check_error)
