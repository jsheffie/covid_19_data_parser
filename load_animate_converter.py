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
import matplotlib.animation as animation
import time
# filename="US.csv"
filename="New_York_City_New_York_US.csv"

datafile = cbook.get_sample_data('{}/data_output/{}'.format(cwd, filename), asfileobj=False)
print('loading', datafile)

data = np.genfromtxt(
    datafile, delimiter=',', names=True,
    dtype=None, converters={0: dateutil.parser.parse})

# fig, ax = plt.subplots()
# ax.plot(data['date'], data['count'], '-')# data['new_cases'], data['multiplication_factor'])
# fig.autofmt_xdate()
# plt.show()

def data_gen():
    for data_line in data:
        yield data_line[0], data_line[1]

def init():
	pass

fig, ax = plt.subplots()
# line, = ax.plot([], [], lw=2)
# line, = ax.plot(data['date'], data['count'], '-')# data['new_cases'], data['multiplication_factor'])
line, = ax.plot(data['Date'], data['Confirmed'], '-')
ax.grid()
xdata, ydata = [], []

def run(data):
    # update the data
    t, y = data
    xdata.append(t)
    ydata.append(y)
    # time.sleep(0.3)
    # xmin, xmax = ax.get_xlim()

    # if t >= xmax:
    #     ax.set_xlim(xmin, 2*xmax)
    #     ax.figure.canvas.draw()
    line.set_data(xdata, ydata)

    return line,

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=600,
                              repeat=False, init_func=init)
plt.show()
