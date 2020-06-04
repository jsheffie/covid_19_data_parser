#!/usr/bin/env python3

import os
import sys
from datetime import date, timedelta

# look for libraries that are configured by './build.sh'
cwd = os.getcwd()

# Add `/lib` to the path to pick up our pip installed 3rd party requirements
sys.path[0:0] = ["{}/lib".format(cwd)]


"""
==============
Load converter
==============

This example demonstrates passing a custom converter to `numpy.genfromtxt` to
extract dates from a CSV file.
"""

import dateutil.parser
from matplotlib import cbook, dates
import matplotlib.pyplot as plt
import numpy as np


datafile = cbook.get_sample_data('{}/data_output/US.csv'.format(cwd), asfileobj=False)
print('loading', datafile)

data = np.genfromtxt(
    datafile, delimiter=',', names=True,
    dtype=None, converters={0: dateutil.parser.parse})

fig, ax = plt.subplots()
ax.plot(data['date'], data['count'], '-')# data['new_cases'], data['multiplication_factor'])
fig.autofmt_xdate()
plt.show()
