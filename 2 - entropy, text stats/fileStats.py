#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
import codecs
import math
from time import gmtime, strftime


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


class FileStats:
    def __init__(self, filenames, case_sensitive, skip_whitespace, logbase, precision):
        date_and_time_filename = str(strftime("%Y-%m-%d_%H-%M-%S", gmtime()))
        date_and_time = str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        self.filename = "STATS_" + date_and_time_filename
        self.file = codecs.open(self.filename, 'w', 'utf-8')
        self.write_line("Analysis date and time: " + date_and_time)
        self.write_line("Filenames analyzed: ")
        for filename in filenames:
            self.write_line("\t" + filename)
        self.write_line("Analysis options:")
        self.write_line("\tCase sensitive:" + str(case_sensitive))
        self.write_line("\tWhitespace skipped:" + str(skip_whitespace))
        self.write_line("\tLogarithm base: " + str(logbase))
        self.write_line("\tCalculations precision: " + str(precision))
        self.write_break_line()

    def write_line(self, line):
        self.file.write(line+"\n")

    def write_break_line(self):
        self.write_line("--------------------------------------------------------")

    def close(self):
        self.file.close()


class Entropy:
    def __init__(self, precision=3, logarithm_base=2):
        self.precision = precision
        self.logarithm_base = logarithm_base
        self.letters_dict = {}
        self.letters_count = 0
        self.different_letters_count = 0

    def clear(self):
        self.letters_count = 0
        self.letters_dict = {}
        self.different_letters_count = 0

    def inspect_message(self, message):
        self.letters_count = 0
        self.different_letters_count = 0
        for l in message:
            self.letters_count += 1
            if l not in self.letters_dict:
                self.letters_dict[l] = 1
            else:
                self.letters_dict[l] += 1
        self.different_letters_count = len(self.letters_dict)

    def get_dict_keyval(self, key):
        bufkey = ""
        if key == '\n':
            bufkey = "\\n"
        elif key == '\t':
            bufkey = '\\t'
        elif key == '\r':
            bufkey = '\\r'
        else:
            bufkey = key
        return "'" + bufkey + "'" + ": " + str(self.letters_dict[key]) + "(" \
               + str(round((self.letters_dict[key]/self.letters_count) * 100, self.precision)) + "%)"

    def sum_entropy(self, key):
        p = self.letters_dict[key]/self.letters_count
        return math.log(1/p ** p, self.logarithm_base)

    def skip_whitespaces(self, message):
        message = ''.join(message.split(' '))
        message = ''.join(message.split('\n'))
        message = ''.join(message.split('\r'))
        message = ''.join(message.split('\t'))
        return message

    def case_not_sensitive(self, message):
        return message.lower()

parser = Parser()
parser.add_argument('filename', nargs='+', help='filename to check stats for')
parser.add_argument('--case', default=1, help='instruct to be case sensitive (0, default 1)',
                    choices=range(0, 2), type=int)
parser.add_argument('--whitespace', default=0, help='instruct to skip whitespaces (1, default 0)',
                    choices=range(0, 2), type=int)
parser.add_argument('--logbase', default=2, help='logarithm base for entropy algorithm',
                    type=int)
parser.add_argument('--precision', default=3, help='entropy algorithm precision',
                    type=int)
args = parser.parse_args()

caseSensitive = args.case
skipWhitespace = args.whitespace
filenames = args.filename
logbase = args.logbase
precision = args.precision

message = ""
entropyHelper = Entropy(precision, logbase)
file = FileStats(filenames, caseSensitive, skipWhitespace, logbase, precision)

for filename in filenames:
    with codecs.open(filename, 'r', 'utf-8') as f:
        message = f.read()

    file.write_line("Name of the file: " + filename)
    if not caseSensitive:
        message = entropyHelper.case_not_sensitive(message)
    if skipWhitespace:
        message = entropyHelper.skip_whitespaces(message)

    entropyHelper.inspect_message(message)
    file.write_line("Letters count: " + str(entropyHelper.letters_count))
    file.write_line("Number of different chars: " + str(entropyHelper.different_letters_count))

    entropy = 0
    for l in sorted(entropyHelper.letters_dict):
        file.write_line(entropyHelper.get_dict_keyval(l))
        entropy += entropyHelper.sum_entropy(l)

    file.write_line("Entropy of the text: " + str(entropy))
    file.write_line("Entropy normalized by length of the text: " + str(entropy / entropyHelper.letters_count))
    file.write_line("Entropy in %: " + str((1 - entropy / entropyHelper.letters_count) * 100) + "%")
    file.write_break_line()
    entropyHelper.clear()

file.close()
print("Statistics has been saved to file named " + file.filename)