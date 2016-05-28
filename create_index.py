#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
from os import listdir
from os.path import isfile, join
import json


class Lister:

    def __init__(self, path):
        self.path = path

    def list(self):
        self.files = [f for f in listdir(self.path)
                      if isfile(join(self.path, f))]

    def create_index(self):
        self.list()

        with open('index.json', 'w') as outfile:
            json.dump(
                self.files, outfile, sort_keys=True,
                indent=4, separators=(',', ': '))


def main(path):
    lister = Lister(path)
    lister.create_index()


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'p:', ['path=', 'params='])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-p', '--path'):
            main(arg)
