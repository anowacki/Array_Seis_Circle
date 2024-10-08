#!/usr/bin/env python

# file to test out the theta - p codes and plotting!

# imports
import obspy
import numpy as np
import time
import matplotlib.pyplot as plt

from circ_array.array_info import array 
from circ_array.beamforming_polar import BF_Pol_all, BF_Pol_Lin, BF_Pol_PWS
from circ_array.array_plotting import plotting

# parameters
# phase of interest
phase = 'SKS'
phases = ['SKS','SKKS','ScS','Sdiff','sSKS','sSKKS','PS']

# frequency band
fmin = 0.13
fmax = 0.52

st = obspy.read('./data/19990405/*SAC')
a = array(st)

# get array metadata
event_time = a.eventtime()
geometry = a.geometry()
distances = a.distances(type='deg')
mean_dist = np.mean(distances)
stations = a.stations()


# get travel time information and define a window
Target_phase_times, time_header_times = a.get_predicted_times(phase)

avg_target_time = np.mean(Target_phase_times)
min_target_time = int(np.nanmin(Target_phase_times, axis=0)) 
max_target_time = int(np.nanmax(Target_phase_times, axis=0)) + 10

stime = event_time + min_target_time
etime = event_time + max_target_time

# trim the stream
# Normalise and cut seismogram around defined window
st = st.copy().trim(starttime=stime, endtime=etime)
st = st.normalize()

# get predicted slownesses and backazimuths
predictions = a.pred_baz_slow(phases=phases, one_eighty=True)

# find the line with the predictions for the phase of interest
row = np.where((predictions == phase))[0]
P, S, BAZ, a._X, a._Y, PRED_AZ_X, PRED_AZ_Y, DIST, TIME = predictions[row, :][0]

slow_min = float(S) - 1.5
slow_max = float(S) + 4
baz_min = float(BAZ) - 30
baz_max = float(BAZ) + 30
b_space = 1
s_space = 0.1

# filter
st = st.filter('bandpass', freqmin=fmin, freqmax=fmax,
                  corners=4, zerophase=True)

# get the traces and phase traces
Traces = a.traces()
Phase_traces = a.phase_traces()

# get sampleing rate
sampling_rate=st[0].stats.sampling_rate


start = time.time()
Lin_arr, PWS_arr, F_arr, Results_arr, peaks = BF_Pol_all(traces=Traces, phase_traces=Phase_traces, sampling_rate=np.float64(
                                                        sampling_rate), geometry=geometry, distance=mean_dist, smin=slow_min,
                                                        smax=slow_max, bazmin=baz_min, bazmax=baz_max, s_space=0.1, baz_space=b_space, degree=2)
end = time.time()

print("time", end-start)
peaks = np.c_[peaks, np.array(["PWS", "LIN", "F"])]

peaks = peaks[np.where(peaks == "PWS")[0]]


fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='polar')
p = plotting(ax = ax)

p.plot_TP_Pol(tp=PWS_arr, peaks=peaks, smin=slow_min, smax=slow_max, bazmin=baz_min, bazmax=baz_max,
              sstep=s_space, bazstep=b_space, contour_levels=50, title="PWS Plot", predictions=predictions, log=False)

plt.show()






start = time.time()
Lin_arr, Results_arr, peaks = BF_Pol_Lin(traces=Traces, sampling_rate=np.float64(
                                                        sampling_rate), geometry=geometry, distance=mean_dist, smin=slow_min,
                                                        smax=slow_max, bazmin=baz_min, bazmax=baz_max, s_space=s_space, baz_space=b_space)
end = time.time()

print("time", end-start)

fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='polar')
p = plotting(ax = ax)

p.plot_TP_Pol(tp=Lin_arr, peaks=peaks, smin=slow_min, smax=slow_max, bazmin=baz_min, bazmax=baz_max,
              sstep=s_space, bazstep=b_space, contour_levels=50, title="Lin Plot", predictions=predictions, log=False)

plt.show()




start = time.time()
PWS_arr, Results_arr, peaks = BF_Pol_PWS(traces=Traces, phase_traces=Phase_traces, sampling_rate=np.float64(
                                                        sampling_rate), geometry=geometry, distance=mean_dist, smin=slow_min,
                                                        smax=slow_max, bazmin=baz_min, bazmax=baz_max, s_space=s_space, baz_space=b_space, degree=2)
end = time.time()

print("time", end-start)


fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='polar')
p = plotting(ax = ax)

p.plot_TP_Pol(tp=PWS_arr, peaks=peaks, smin=slow_min, smax=slow_max, bazmin=baz_min, bazmax=baz_max,
              sstep=s_space, bazstep=b_space, contour_levels=50, title="PWS Plot", predictions=predictions, log=False)
plt.show()
