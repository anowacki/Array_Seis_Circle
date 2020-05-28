#!/usr/bin/env python

# code to test the manual pick time window function.

import obspy
import numpy as np
import time

from Circ_Array import Circ_Array
from Circ_Beam import BF_Spherical_XY, BF_Spherical_Pol
from Plotting import Plotting
c = Circ_Array()


st = obspy.read("./data/19990405/*SAC")
print(st[0].data)
phase = "SKKS"
event_time = c.get_eventtime(st)
window = c.pick_tw(stream=st, phase=phase)

print(window)

rel_window = c.pick_tw(stream=st, phase=phase, align=True)
print(rel_window)
