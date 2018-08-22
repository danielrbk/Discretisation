THREAD_COUNT = 4
EPSILON = 0.000000001
CLASS_SEPARATOR = -1
EXTREME_VAL = 10**8
DEBUG_MODE = False
HAPPY_LOG_PATH = r"D:\Rejabek\python_happy_log.txt"
SAD_LOG_PATH = r"D:\Rejabek\python_sad_log.txt"


class FileFormatNotCorrect(Exception):
    pass


def debug_print(string,args=""):
    if DEBUG_MODE:
        print(string,args)