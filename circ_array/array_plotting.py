
from circ_array import circ_array
c=circ_array()
import obspy
import matplotlib.pyplot as plt
import numpy as np
import scipy

plt.set_cmap('turbo')


class plotting:
    """
    This class holds functions for several plotting situations:

        - plot_record_section_SAC: plots record section of traces in an obspy stream object.

        - add_lines: add lines to $\theta-p$ plot.

        - add_circles: add circles to $\theta-p$ plot.

        - plot_TP_XY: plot theta-p plot in a cartesian coordinate system.

        - plot_TP_Pol: plot theta-p plot in polar corrdinate system.

        - plot_vespagram: plot vespagram of either backazimuth or slowness.
    """

    def __init__(self, ax):
        self.ax = ax
        pass


    def plot_record_section_SAC(self, st, phase, tmin=150, tmax=150, align=False):
        '''
        Plots a distance record section of all traces in the stream. The time window will
        be around the desired phase.

        Param: st (Obspy Stream Object)
        Description: Stream of SAC files with the time (tn) and labels (ktn) populated.

        Param: phase (string)
        Description: The phase you are interested in analysing (e.g. SKS). Travel time must
                     be stored in the SAC headers tn and phase name in tkn.

        Param: tmin (float)
        Description: Time before the minumum predicted time of the phase you are interested in.

        Param: tmax (float)
        Description: Time after the maximum predicted time of the phase you are interested in.

        Return:
            Plots record section, does not return anything.
        '''

        # get header with travel times for predicted phase
        Target_time_header = c.get_t_header_pred_time(stream=st, phase=phase)

        # get predicted travel times
        Target_phase_times, time_header_times = c.get_predicted_times(
            stream=st, phase=phase)

        # get min and max predicted times of pahse at the array
        avg_target_time = np.mean(Target_phase_times)
        min_target_time = np.amin(Target_phase_times)
        max_target_time = np.amax(Target_phase_times)

        # plot a record section and pick time window
        # Window for plotting record section
        win_st = float(min_target_time - tmin)
        win_end = float(max_target_time + tmax)

        event_time = c.get_eventtime(st)

        # copy stream and trim it around the time window
        stream_plot = st.copy
        stream_plot = st.trim(starttime=event_time + win_st,
                              endtime=event_time + win_end)
        stream_plot = stream_plot.normalize()

        # for each trace in the stream
        for i, tr in enumerate(stream_plot):

            # get distance of station from event location
            dist = tr.stats.sac.gcarc

            # if align, subtrace predcted times of the target from the other predicted times
            if align == True:
                tr_plot = tr.copy().trim(starttime=event_time + (getattr(tr.stats.sac, Target_time_header) - tmin),
                              endtime=event_time + (getattr(tr.stats.sac, Target_time_header) + tmax))
                time = np.linspace(-tmin, tmax, int((tmin + tmax) * tr.stats.sampling_rate))
            else:
                tr_plot = tr.copy()
                time = np.linspace(win_st, win_end, int((win_end - win_st) * tr.stats.sampling_rate))

            # reduce amplitude of traces and plot
            dat_plot = tr_plot.data *.5
            # dat_plot = np.pad(
            #     dat_plot, (int(start * (1 / tr.stats.sampling_rate))), mode='constant')
            dat_plot += dist

            # ensure time array is the same length as the data
            if time.shape[0] != dat_plot.shape[0]:
                points_diff = -(abs(time.shape[0] - dat_plot.shape[0]))
                if time.shape[0] > dat_plot.shape[0]:
                    time = np.array(time[:points_diff])
                if time.shape[0] < dat_plot.shape[0]:
                    dat_plot = np.array(dat_plot[:points_diff])

            # plot data
            self.ax.plot(time, dat_plot, color='black', linewidth=0.5)

        # set the x axis
        if align == True:
            self.ax.set_xlim(-tmin, tmax)

        else:
            self.ax.set_xlim(win_st, win_end)

        # plot predictions
        for i,time_header in enumerate(time_header_times):
            t = np.array(time_header)

            if align == True:
                try:
                    t[:,0] = np.subtract(t[:,0].astype(float), np.array(Target_phase_times))
                except:
                    pass
            else:
                pass

            try:
                # sort array on distance
                t = t[t[:,1].argsort()]
                self.ax.plot(t[:, 0].astype(float),
                    t[:, 1].astype(float), color='C'+str(i), label=t[0, 2])
            except:
                print("t%s: No arrival" %i)


        # plt.title('Record Section Picking Window | Depth: %s Mag: %s' %(stream[0].stats.sac.evdp, stream[0].stats.sac.mag))
        self.ax.set_ylabel('Epicentral Distance ($^\circ$)', fontsize=14)
        self.ax.set_xlabel('Time (s)', fontsize=14)
        plt.legend(loc='best')

        return

    def add_circles(self, radii, x, y, colour):
        """
        Adds circles of radius in the radii list with the centre at point xy with the defined colour
        to the axis the funtion is used in.

        Param: radii (array of floats)
        Description: array of circle radii.

        Param: x/y (float)
        Description: centre for circles.

        Param: colour (string)
        Description: colour of circles

        Return:
            Nothing.
        """

        for r in radii:
            circle = plt.Circle((x, y), r, color=colour, clip_on=True,
                        fill=False, linestyle='--')
            self.ax.add_artist(circle)

        for b in range(45, 315, 60):
            self.ax.text((r) * np.sin(np.radians(b)), (r) *
                    np.cos(np.radians(b)), str(r), clip_on=True, color=colour, fontsize=10)

        return


    def add_lines(self, radius, x, y, angles, colour):
        """
        Adds lines of length 'radius' from point xy with a variety of angles all
        with defined colour.

        Param: radius (float)
        Description: radius/length for lines.

        Param: x/y (float)
        Description: centre for lines.

        Param: angles (array floats)

        Param: colour (string)
        Description: colour of lines

        Returns nothing.
        """

        for a in angles:
            self.ax.plot([x, radius * np.cos(np.radians(a))],
                    [y, radius * np.sin(np.radians(a))], linestyle='--', color=colour, zorder=1)

        return



    def plot_TP_XY(self, tp, peaks, sxmin, sxmax, symin, symax, sstep, title, log = False, contour_levels=30, predictions=None):
        """
        Given a 2D array of power values for the $\theta-p$ analysis, it plots the
        values within the given slowness space with contours of power values.

        Param: tp (2D numpy array floats)
        Description: 2D array of power values of the theta-p plot.

        Param: peaks (1D numpy array floats)
        Description: x and y locations of the peak location.

        Param: s(x/y)min (float)
        Description: minimum x and y slowness value.

        Param: s(x/y)max (float)
        Description: maximum x and y slowness value.

        Param: sstep (float)
        Description: increment of steps in the slowness grid.

        Param: title (string)
        Description: title of the plot.

        Param: log (Bool)
        Description: True if you want the plot to be log scaled, False if linear scaling.

        Param: contour_levels (float)
        Description: number of contours.

        Param predictions (list of lists)
        Description: output of function 'pred_baz_slow' for the phases you
                     want to plot on the t-p plot.

        """

        # define space
        steps_x = int(np.round((sxmax - sxmin) / sstep, decimals=0)) + 1
        steps_y = int(np.round((symax - symin) / sstep, decimals=0)) + 1
        slow_x = np.linspace(sxmin, sxmax, steps_x, endpoint=True)
        slow_y = np.linspace(symin, symax, steps_y, endpoint=True)

        # if given predictions, plot them
        if predictions is not None:
            Phases_x=predictions[:,3].astype(float)
            Phases_y=predictions[:,4].astype(float)
            Phases=predictions[:,0]

            Phases_x = np.where((Phases_x > sxmin) & (Phases_x < sxmax), Phases_x,Phases_x)
            Phases_y = np.where((Phases_y > symin) & (Phases_y < symax), Phases_y,Phases_y)
        else:
            pass


        # define radii of circles and angles for lines
        radii = [2, 4, 6, 8, 10]
        angles = range(0, 360, 30)

        # if log, convert the values
        if log == True:
            p = self.ax.contourf(slow_x, slow_y, np.log(tp), contour_levels)
            cbar = plt.colorbar(p, label='Power', ticks = np.linspace(0,tp.max(),11), drawedges=True, ax=self.ax)

        elif log == False:
            p = self.ax.contourf(slow_x, slow_y, tp, contour_levels)
            cbar = plt.colorbar(p, label='Power', ticks = np.linspace(0,tp.max(),11), drawedges=True, ax=self.ax)

        else:
            pass

        # plot
        self.ax.set_xlabel("p$_{x}$ (s/$^{\circ}$)", fontsize=14)
        self.ax.set_ylabel("p$_{y}$ (s/$^{\circ}$)", fontsize=14)
        self.ax.set_title(title, fontsize=14)
        self.add_circles(radii=radii, x=0, y=0, colour='w')
        self.add_lines(radius=10, x=0, y=0, angles=angles, colour='w')

        if peaks is not None:
            x_peaks = list(peaks[:,0].astype(float))
            y_peaks = list(peaks[:,1].astype(float))
            self.ax.scatter(x_peaks, y_peaks, color='red', marker='x', zorder=2)

        else:
            pass
        if predictions is not None:
            self.ax.scatter(Phases_x,Phases_y,color='white',s=80, zorder=3, marker='x')
            for i,p in enumerate(Phases):
                self.ax.text(Phases_x[i],Phases_y[i]-0.2,p , color='white', fontsize=16,zorder=3)
        else:
            pass

        self.ax.set_xlim(sxmin,sxmax)
        self.ax.set_ylim(symin,symax)
        self.ax.set_aspect('equal', 'box')

        return



    def plot_TP_Pol(self, tp, peaks, smin, smax, bazmin, bazmax, sstep, bazstep, title, log = False, contour_levels=30, predictions=np.array([])):
        """
        Given a 2D array of power values for the theta-p analysis, it plots the
        values within the given slowness backazimuth space with contours of power values.

        Param: tp (2D numpy array floats)
        Description: 2D array of power values of the theta-p plot.

        Param: peaks (1D numpy array floats)
        Description: slowness and backazimuth locations of the peak location.

        Param: smin/smax (float)
        Description: minimum/maximum slowness value.

        Param: bazmin/bazmax (float)
        Description: Miniumum/maximum backazimuth values.

        Param: sstep (float)
        Description: increment of slowness steps.

        Param: sstep (float)
        Description: increment of backazimuth steps.

        Param: title (string)
        Description: title of the plot.

        Param: log (Bool)
        Description: True if you want the plot to be log scaled, False if linear scaling.

        Param: contour_levels (float)
        Description: number of contours.

        Param predictions (list of lists)
        Description: output of function 'pred_baz_slow' for the phases you
                     want to plot on the t-p plot.

        """


        # create space
        nslow = int(np.round(((smax - smin) / sstep) + 1))
        nbaz = int(np.round(((bazmax - bazmin) / bazstep) + 1))

        slows = np.linspace(smin, smax, nslow, endpoint=True)
        bazs = np.linspace(bazmin, bazmax, nbaz, endpoint=True)

        # if given predictions separate into x and y points
        if predictions.size !=0:
            Phases_b=predictions[:,2].astype(float)
            Phases_s=predictions[:,1].astype(float)
            Phases=predictions[:,0]

            Phases_b = np.where((Phases_b > bazmin) & (Phases_b < bazmax), Phases_b, Phases_b)
            Phases_s = np.where((Phases_s > smin) & (Phases_s < smax), Phases_s, Phases_s)
        else:
            pass

        # initialise figure
        # fig = plt.figure(figsize=(7,7))
        # ax = fig.add_subplot(111, polar=True)

        # if log, convert values
        if log == True:
            self.ax.contourf(np.radians(bazs), slows, np.log(tp), contour_levels)
        elif log == False:
            self.ax.contourf(np.radians(bazs), slows, tp, contour_levels)
        else:
            pass

        self.ax.set_title(title, fontsize=16)

        # if given peaks, plot them
        if peaks.size != 0:
            b_peaks = list(peaks[:,0].astype(float))
            s_peaks = list(peaks[:,1].astype(float))
            self.ax.scatter(np.radians(b_peaks), s_peaks, color='red', marker='x', zorder=2)

        else:
            pass

        # plot predictions if given
        if predictions.size != 0:
            self.ax.scatter(np.radians(Phases_b),Phases_s,color='white',s=20, zorder=3, marker='+')
            for i,p in enumerate(Phases):
                self.ax.text(np.radians(Phases_b[i]),Phases_s[i]+0.2, p, color='white', fontsize=10,zorder=3)

        else:
            pass


        # set orientation and dimensions of figure
        self.ax.set_thetalim(np.radians(bazmin),np.radians(bazmax))
        self.ax.set_rlim(smin,smax)
        self.ax.set_rorigin(0)
        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)

        # add axis labels
        self.ax.text(np.radians(bazmin - 7.5),(smin+smax)/2.,"$\it{p} \ (s/^{\circ})$", fontsize=14, rotation=90-bazmin, ha='center',va='center')
        self.ax.text(np.radians((bazmin+bazmax)/2),smin-0.25,"$\\theta \ (^{\circ})$", fontsize=14, rotation=180-((bazmax+bazmin)/2), ha='center',va='center')

        return


    def plot_vespagram(self, vespagram, ymin, ymax, y_space, tmin, tmax, sampling_rate, title, type, predictions=None, npeaks=5, log = False, contour_levels=30, envelope=True):
        """
        Given a 2D numpy array of values representing a vespagram, plot it with peaks and predictions.

        Param: vespagram (2D numpy array of floats)
        Description: amplitude values of a stack at each [slowness,time] point.

        Param: ymin/ymax (float)
        Description: min/max of y values (either backazimuth or slowness).

        Param: y_space (float)
        Description: y value increments (either backazimuth or slowness).

        Param: xmin/xmax (float)
        Description: min/max time values.

        Param: sampling_rate (float)
        Description: sampling rate of data in s^-1.

        Param: title (string)
        Description: title of the plot.

        Param: predictions (list of lists)
        Description: output of function 'pred_baz_slow' for the phases you
                     want to plot on the t-p plot.

        Param: npeaks (int)
        Description: the number of peaks to plot on the graph.

        Param: log (Bool)
        Description: True if you want the plot to be log scaled, False if linear scaling.

        Param: type (string)
        Description: is the y axis changing in backazimuth (baz) or slowness (slow).

        Param: contour_levels (float)
        Description: number of contours.

        Param: envelope (Bool)
        Description: do you want to plot the envelope of the amplitudes or not.

        Return:
            Nothing, but plots the vespagram.

        """

        # define space
        ny = int(np.round(((ymax - ymin) / y_space) + 1))
        ys = np.linspace(ymin, ymax, ny, endpoint=True)
        ntime = int(np.round(((tmax - tmin) * sampling_rate) + 1))
        times = np.linspace(tmin, tmax, ntime, endpoint=True)


        # if given the predictions separate into x and y points
        if predictions is not None:
            if type == 'slow':
                Phases_x=predictions[:,8].astype(float)
                Phases_y=predictions[:,1].astype(float)
                Phases=predictions[:,0]
            elif type == 'baz':
                Phases_x=predictions[:,8].astype(float)
                Phases_y=predictions[:,2].astype(float)
                Phases=predictions[:,0]
            else:
                print("type must be 'slow' or 'baz'")

            Phases_x = np.where((Phases_x > tmin) & (Phases_x < tmax), Phases_x,Phases_x)
            Phases_y = np.where((Phases_y > ymin) & (Phases_y < ymax), Phases_y,Phases_y)
        else:
            pass

        # if you want the envelope, convert the stacked traces
        if envelope == True:
            for i,stack in enumerate(vespagram):
                vespagram[i] = obspy.signal.filter.envelope(stack)
        else:
            pass

        # smooth the vespagram and find peaks
        smoothed_vesp = scipy.ndimage.filters.gaussian_filter(
        vespagram, 2, mode='constant')
        peaks = c.findpeaks_XY(smoothed_vesp, xmin=tmin, xmax=tmax, ymin=ymin, ymax=ymax, xstep=(1/sampling_rate), ystep=y_space, N=npeaks)


        # Plot vespagram
        # fig = plt.figure(figsize=(8,8))
        # ax = fig.add_subplot(111)

        # take log of values if requested
        if log == True:
            v = self.ax.contourf(times, ys, np.log(vespagram), contour_levels)
        elif log == False:
            v = self.ax.contourf(times, ys, vespagram, contour_levels)
        else:
            pass

        # plt.colorbar(v)

        # if wanted, plot predictions
        if predictions is not None:
            self.ax.scatter(Phases_x,Phases_y,color='white',s=20, zorder=3, marker='+')
            for i,p in enumerate(Phases):
                self.ax.text(Phases_x[i],Phases_y[i]-0.2,p , color='white', fontsize=10,zorder=3)
        else:
            pass

        # plot peaks
        self.ax.scatter(peaks[:,0],peaks[:,1],marker='x',color='red',label="peaks")

        self.ax.set_title(title)
        self.ax.set_xlim(tmin,tmax)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylim(ymin,ymax)
        if type=='slow':
            self.ax.set_ylabel("p ($s/^{\circ}$)")
        elif type=='baz':
            self.ax.set_ylabel("$\\theta (^{\circ})$")
        else:
            print("type needs to be 'baz' or 'slow'")

        return


    def plot_clusters_XY(self, labels, tp, peaks, sxmin, sxmax, symin, symax, sstep, title, log = False, contour_levels=30, predictions=None, ellipse=False, std_devs=[1,2,3]):
        """
        Given a 2D array of power values for the $\theta-p$ analysis, it plots the
        values within the given slowness space with contours of power values.

        Params: labels (1D numpy array of integers)
        Description: array of integers describing which cluster they belong to.
                     e.g. [-1 0 -1 0 0 -1]

        Param: tp (2D numpy array floats)
        Description: 2D array of power values of the theta-p plot.

        Param: peaks (2D numpy array floats)
        Description: x and y locations of the peaks. 0 axis should be same length as the labels.

        Param: s(x/y)min (float)
        Description: minimum x and y slowness value.

        Param: s(x/y)max (float)
        Description: maximum x and y slowness value.

        Param: sstep (float)
        Description: increment of steps in the slowness grid.

        Param: title (string)
        Description: title of the plot.

        Param: log (Bool)
        Description: True if you want the plot to be log scaled, False if linear scaling.

        Param: contour_levels (float)
        Description: number of contours.

        Param predictions (list of lists)
        Description: output of function 'pred_baz_slow' for the phases you
                     want to plot on the t-p plot.

        Param: ellipse (Bool)
        Description: Plot error ellipses (True) or not (False).

        Param: std_dev (list of integers)
        Description: std_dev of the error ellipse.

        Return:
            Nothing.

        """

        ## Plot the tp plot without the peaks

        self.plot_TP_XY(tp=tp, peaks=None, sxmin=sxmin, sxmax=sxmax, symin=symin,
                        symax=symax, sstep=sstep, title=title, log = log,
                        contour_levels=contour_levels, predictions=predictions)

        x_thresh = np.array(peaks)[:, 0].astype(float)
        y_thresh = np.array(peaks)[:, 1].astype(float)

        from cluster_utilities import cluster_utilities
        cu = cluster_utilities(labels = labels, points = peaks)

        means_xy, means_baz_slow = cu.cluster_means()
        covariance_matrices_clusters = cu.covariance_matrices()
        # create palette for the cluster points
        palette = np.array(['black', 'C0', 'C1', 'C2', 'C3', 'C4', 'C5'])
        palette_inv = np.array(['grey','green','purple','orange','red','blue'])

        # loop over the number of clusters

        for l in set(list(labels)):
            x_plot = x_thresh[np.where(labels == l)[0]]
            y_plot = y_thresh[np.where(labels == l)[0]]
            print(x_plot)
            print(y_plot)
            if l == -1:
                label = 'Noise'
            else:
                label = 'Cluster ' + str(l+1)

            self.ax.scatter(x_plot, y_plot,
               marker='o', s=30, linewidth=0.5, c=palette[l+1], edgecolors='black', zorder=2, label=label)



        for i, mean in enumerate(means_xy):

            if ellipse == True:
            # calculate ellipse using function
                for std_dev in std_devs:
                    ellipse_1 = plot_cov_ellipse(
                        cov=covariance_matrices_clusters[i], pos=mean, nstd=std_dev, linewidth=1.5)
                    self.ax.add_artist(ellipse_1)
            else:
                pass

            self.ax.scatter(mean[0], mean[1], marker="X", linewidth=0.5, edgecolors='black',
                       c=palette_inv[i], s=80, zorder=3, label='Mean Cluster ' + str(i+1))


        self.ax.legend(loc='best')

        return
