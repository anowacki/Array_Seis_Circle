#!/usr/bin/env python

Description = """
This python script will test:
    - Importing of the package.
    - Collect the predictions from headers in the SAC files.
    - Make predictions using the information in the SAC files.
"""

import obspy
import numpy as np
from circ_array.array_info import array

phase="SKS"
phases=["SKS","SKKS","SKKKS","ScS","Sdiff"]


st = obspy.read('./data/19990405/*SAC')
a = array(st)
stations = a.stations()

# Recover the predictions from the sac files in the Obspy stream.
Target_phase_times, time_header_times = a.get_predicted_times(phase=phase)

print(time_header_times[1][0])
print(st[0].stats.sac.t2, st[0].stats.sac.gcarc, st[0].stats.sac.kt2)

print(time_header_times[1][4])
print(st[4].stats.sac.t2, st[4].stats.sac.gcarc, st[4].stats.sac.kt2)

print(time_header_times[1][7])
print(st[7].stats.sac.t2, st[7].stats.sac.gcarc, st[7].stats.sac.kt2)

print("Mean %s time:" %phase, np.mean(Target_phase_times))
print("Max %s time:" %phase, np.amax(Target_phase_times))
print("Min %s time:" %phase, np.amin(Target_phase_times))


# Get the predictions for backazimuth and horizontal slowness
results = a.pred_baz_slow(phases=phases, one_eighty=True)
print(results)
