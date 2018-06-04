THREAD_COUNT = 8
EPSILON = 0.000000001
CLASS_SEPARATOR = -1
EXTREME_VAL = 10**8
DEBUG_MODE = False
HAPPY_LOG_PATH = r"C:\Users\Daniel\PycharmProjects\Discretisation\datasets\happylog.txt"
SAD_LOG_PATH = r"C:\Users\Daniel\PycharmProjects\Discretisation\datasets\sadlog.txt"


class FileFormatNotCorrect(Exception):
    pass


def debug_print(string):
    if DEBUG_MODE:
        print(string)