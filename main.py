import sys
import os
import psutil
from os.path import isfile
from fm_index import FMIndex


def load_file(test_purposes=False):
    if test_purposes:
        return "ribaribigrizerepribaribigrizerepribaribigrizerep"

    if len(sys.argv) == 2:
        if not isfile(sys.argv[1]):
            print("Input file doesn't exist")
            os.abort()
        file_path = sys.argv[1]

    file = open(file_path, 'r')
    file.readline()
    data = file.read().replace('\n', '')
    file.close()
    print('File '+file_path+' has been loaded!')
    return data


def get_patterns():
    p1 = input("Insert first pattern: ")
    p2 = input("Insert second pattern: ")
    p3 = input("Insert third pattern: ")
    if not p1:
        p1 = 'ATGCATG'
    if not p2:
        p2 = 'TCTCTCTA'
    if not p3:
        p3 = 'TTCACTACTCTCA'

    return p1, p2, p3


def print_pattern_times(start_times, end_times, tally_step, sa_step, patterns):
    for i in range(len(start_times)):
        t = subtract_times(end_times[i], start_times[i])
        print("Pattern "+str(i+1)+": " + patterns[i] + " | FM search (tally_step=%s, sa_step=%s) execution took  %.3fms" % (tally_step, sa_step, t))


def subtract_times(t_end, t_start):
    return float((t_end - t_start)*1000)


def main():
    text = load_file()

    patterns = get_patterns()

    fm = FMIndex()

    pid = os.getpid()
    process = psutil.Process(pid)

    bw, sa = fm.encode(text)
    decoded = fm.decode(bw)

    tally_step, sa_step = fm.get_steps()
    pattern_start_times = []
    pattern_end_times = []

    for pattern in patterns:
        match, start_time, end_time = fm.search(pattern)
        for i, m in enumerate(match):
            print('{}"{}"{}'.format(decoded[0: m[0]], decoded[m[0]:m[1]], decoded[m[1]:]))

        pattern_start_times.append(start_time)
        pattern_end_times.append(end_time)

    print_pattern_times(pattern_start_times, pattern_end_times, tally_step, sa_step, patterns)
    print("\nMemory usage: {}MB".format(process.memory_info()[0] / 2. ** 20))


if __name__ == '__main__':
    main()
