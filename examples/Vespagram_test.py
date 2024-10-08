#!/usr/bin/env python

# This is more of a work in progress, but this script will
# test the code for creating vespagrams with our curved wavefront correction.

import obspy
import numpy as np
import time
import matplotlib.pyplot as plt

from circ_array.array_info import array 
from circ_array.vespagram import Vespagram_Lin, Vespagram_PWS, Baz_vespagram_PWS, Baz_vespagram_Lin
from circ_array.array_plotting import plotting


# parameters
# phase of interest
phase = 'SKS'
phases = ['SKS','SKKS','ScS','Sdiff','sSKS','sSKKS','PS','SKKKS','pSKS']

# frequency band
fmin = 0.13
fmax = 0.26

st = obspy.read('./data/19970525/*SAC')
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
min_target = int(np.nanmin(Target_phase_times, axis=0))
max_target = int(np.nanmax(Target_phase_times, axis=0)) + 100

stime = event_time + min_target
etime = event_time + max_target

# trim the stream
# Normalise and cut seismogram around defined window
st = st.copy().trim(starttime=stime, endtime=etime)
st = st.normalize()

# get predicted slownesses and backazimuths
predictions = a.pred_baz_slow(phases=phases, one_eighty=True)

# find the line with the predictions for the phase of interest
row = np.where((predictions == phase))[0]
P, S, BAZ, PRED_BAZ_X, PRED_BAZ_Y, PRED_AZ_X, PRED_AZ_Y, DIST, TIME = predictions[row, :][0]


# make the box around the prediction to search over
smin=float(S)-2
smax=float(S)+6
s_step=0.1


# filter
st = st.filter('bandpass', freqmin=fmin, freqmax=fmax,
                  corners=4, zerophase=True)

a_processed = array(st)

# get the traces and phase traces
Traces = a_processed.traces()
Phase_traces = a_processed.phase_traces()

# get sampleing rate
sampling_rate=st[0].stats.sampling_rate

# slowness vespagrams
vesp_lin = Vespagram_Lin(traces=Traces, sampling_rate=sampling_rate, geometry=geometry,
                         distance=mean_dist, baz=float(BAZ), smin=smin, smax=smax, s_space=s_step)

fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(211)
p = plotting(ax = ax)

p.plot_vespagram(vespagram=vesp_lin, ymin=smin, ymax=smax, y_space=s_step, tmin=min_target, tmax=max_target,
                 sampling_rate=sampling_rate, title="Slow - Lin", predictions=predictions, type='slow',
                 envelope=True)

vesp_pws = Vespagram_PWS(traces=Traces, phase_traces=Phase_traces, sampling_rate=sampling_rate, geometry=geometry,
                         distance=mean_dist, baz=float(BAZ), smin=smin, smax=smax, s_space=s_step, degree=2)

ax = fig.add_subplot(212)
p = plotting(ax = ax)
p.plot_vespagram(vespagram=vesp_pws, ymin=smin, ymax=smax, y_space=s_step, tmin=min_target, tmax=max_target,
                 sampling_rate=sampling_rate, title="Slow - PWS", predictions=predictions, type='slow',
                 envelope=True)
plt.tight_layout()

plt.show()
# backazimuth vespagrams

bmin=float(BAZ)-30
bmax=float(BAZ)+30
b_step=0.05


vesp_lin = Baz_vespagram_Lin(traces=Traces, sampling_rate=sampling_rate, geometry=geometry,
                         distance=mean_dist, slow=float(S), bmin=bmin, bmax=bmax, b_space=b_step)

fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(211)
p = plotting(ax = ax)

p.plot_vespagram(vespagram=vesp_lin, ymin=bmin, ymax=bmax, y_space=b_step, tmin=min_target, tmax=max_target,
                 sampling_rate=sampling_rate, title="Baz - Lin", predictions=predictions, type='baz',
                 envelope=True)


vesp_pws = Baz_vespagram_PWS(traces=Traces, phase_traces=Phase_traces, sampling_rate=sampling_rate, geometry=geometry,
                         distance=mean_dist, slow=float(S), bmin=bmin, bmax=bmax, b_space=b_step, degree=2)


ax = fig.add_subplot(212)
p = plotting(ax = ax)
p.plot_vespagram(vespagram=vesp_pws, ymin=bmin, ymax=bmax, y_space=b_step, tmin=min_target, tmax=max_target,
                 sampling_rate=sampling_rate, title="Baz - PWS", predictions=predictions, npeaks=5, type='baz',
                 envelope=True)
plt.tight_layout()
plt.show()
