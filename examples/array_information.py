#!/usr/bin/env python

Description = """
This python script will test:
    - Importing of the package.
    - Recovering information from the data files about the array.
"""


# import packages

import obspy
from circ_array.array_info import array

# read in data as an obspy stream

st = obspy.read('./data/19970525/*SAC')

a = array(st)

stations = a.stations()

geometry_degrees_absolute = a.geometry(return_center=False, distance='degrees', verbose='False', relative='False')
geometry_degrees_relative = a.geometry(return_center=False, distance='degrees', verbose='False', relative='True')

geometry_kilometres_absolute = a.geometry(return_center=False, distance='km', verbose='False', relative='False')
geometry_kilometres_relative = a.geometry(return_center=False, distance='km', verbose='False', relative='True')

# print(geometry_degrees_absolute)
# print(geometry_degrees_relative)
#
# print(geometry_kilometres_absolute)
# print(geometry_kilometres_relative)

centre_degrees = a.geometry(return_center=True, distance='degrees', verbose='False', relative='False')
centre_kilometres = a.geometry(return_center=True, distance='km', verbose='False', relative='False')

for i,tr in enumerate(st):
    print(tr.stats.station, tr.stats.sac.stlo, tr.stats.sac.stla)
    print(stations[i],geometry_degrees_absolute[i,0], geometry_degrees_absolute[i,1])
