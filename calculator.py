from argparse import ArgumentParser

from calculator.app import run_on_directory


def parse_args():
    arg_parse = ArgumentParser(description='Скрипт для сложения точек эллиптической кривой.')
    arg_parse.add_argument('-i', '--input', default='INPUT', help='Входная директория')
    arg_parse.add_argument('-o', '--output', default='OUTPUT', help='Выходная директория')
    return arg_parse.parse_args()


def main():
    options = parse_args()
    run_on_directory(input=options.input, output=options.output)


if __name__ == '__main__':
    main()
