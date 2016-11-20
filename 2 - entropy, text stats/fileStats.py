#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
import codecs
import math
from time import gmtime, strftime


class Parser(argparse.ArgumentParser):
    def init_parameters(self):
        self.add_argument('filenames', nargs='+', help='filenames to check stats for')
        self.add_argument('--case', default=1, help='instruct to be case sensitive (0, default 1)',
                          choices=range(0, 2), type=int)
        self.add_argument('--whitespace', default=0, help='instruct to skip whitespaces (1, default 0)',
                          choices=range(0, 2), type=int)
        self.add_argument('--logbase', default=2, help='logarithm base for entropy algorithm',
                          type=int)
        self.add_argument('--precision', default=3, help='entropy algorithm precision',
                          type=int)
        self.add_argument('--skip', default='', help='skip certain sign in statistics')

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


class NGram:
    def __init__(self, n):
        self.n = n
        self.dictionary = {}
        self.letters_count = 0
        self.different_letters_count = 0
        self.entropy = 0

    def clear(self):
        self.n = 0
        self.dictionary = {}
        self.letters_count = 0
        self.different_letters_count = 0
        self.entropy = 0

class Entropy:
    def __init__(self, precision=3, logarithm_base=2, n_gram=0):
        self.precision = precision
        self.logarithm_base = logarithm_base
        self.n_grams = [NGram(1), NGram(2), NGram(3), NGram(n_gram)]

    def clear(self):
        for n_gram in self.n_grams:
          n_gram.clear()

    def inspect_message(self, message):
        for n_gram in self.n_grams:
            if n_gram.n == 0:
                continue

            for i in range(0, len(message) - n_gram.n + 1):
                n_gram.letters_count += 1
                l = message[i:i+n_gram.n]
                if l not in n_gram.dictionary:
                    n_gram.dictionary[l] = 1
                else:
                    n_gram.dictionary[l] += 1
            n_gram.different_letters_count = len(n_gram.dictionary)

    def get_dict_keyval(self, key, n_gram):
        bufkey = key
        if '\n' in key:
            bufkey = bufkey.replace('\n', '\\n')
        if '\t' in key:
            bufkey = bufkey.replace('\t', '\\t')
        if '\r' in key:
            bufkey = bufkey.replace('\r', '\\r')

        return "'" + bufkey + "'" + ": " + str(n_gram.dictionary[key]) + "(" \
               + str(round((n_gram.dictionary[key] / n_gram.letters_count) * 100, self.precision)) + "%)"

    def calc_entropy(self):
        for n_gram in self.n_grams:
            self.sum_entropy(n_gram)

    def sum_entropy(self, n_gram):
        if n_gram.n == 0:
            return
        for key in sorted(n_gram.dictionary):
            p = n_gram.dictionary[key] / n_gram.letters_count
            res = math.log(1/p ** p, self.logarithm_base)
            n_gram.entropy += res

    def return_statistics_as_string(self):
        statistics_string = ""
        for n_gram in self.n_grams:
            if n_gram.n == 0:
                continue
            statistics_string += "NGram n: " + str(n_gram.n) + "\n"
            statistics_string += "Letters count: " + str(n_gram.letters_count) + "\n"
            statistics_string += "Number of different chars: " + str(n_gram.different_letters_count) + "\n"
            statistics_string += "<-->\n"
            for l in sorted(n_gram.dictionary):
                statistics_string += self.get_dict_keyval(l, n_gram) + "\n"
            statistics_string += "<-->\n"
            statistics_string +="Entropy of the text: " + str(n_gram.entropy) + "\n"
            statistics_string +="Entropy normalized by length of the text: " + str(n_gram.entropy / n_gram.letters_count) + "\n"
            statistics_string +="Entropy in %: " + str((1 - n_gram.entropy / n_gram.letters_count) * 100) + "%" + "\n"
            statistics_string += "----------" + "\n"
        return statistics_string


    def skip_whitespaces(self, message):
        message = ''.join(message.split(' '))
        message = ''.join(message.split('\n'))
        message = ''.join(message.split('\r'))
        message = ''.join(message.split('\t'))
        return message

    def case_not_sensitive(self, message):
        return message.lower(),

    def skip_certain_chars(self, message, char):
        return ''.join(message.split(char))

parser = Parser()
parser.init_parameters()
args = parser.parse_args()

caseSensitive = args.case
skipWhitespace = args.whitespace
filenames = args.filenames
logbase = args.logbase
precision = args.precision
skip = args.skip

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
    if skip != '':
        message = entropyHelper.skip_certain_chars(message, skip)

    entropyHelper.inspect_message(message)
    entropyHelper.calc_entropy()
    file.write_line(entropyHelper.return_statistics_as_string())
    file.write_break_line()
    entropyHelper.clear()

file.close()
print("Statistics has been saved to file named " + file.filename)