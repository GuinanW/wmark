#!/usr/bin/python
# -*- coding: utf8 -*-

from wmark.common import User, App, Job
import sys

if __name__ == '__main__':
    files = sys.argv[1:]
    if len(files) == 0:
        files = ['params.json', ]

    for f in files:
        app = App(f)
        app.run()
