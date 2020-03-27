#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

file = sys.argv[1]

cpu = CPU()

cpu.load(file)
cpu.run()
