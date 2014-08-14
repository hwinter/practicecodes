import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab
import glob
import matplotlib.cm as cm
from scipy import signal
from dih_tableread import dih_filegrab
from dih_tableread import dih_tablereader
import dih_boxcar as d
from dih_lightcurvedata import dih_lightcurvedata
import dih_sunplot as times
import dih_suncurve as values
import dih_sundate as date
import dih_sunchannel as channel
from scipy.signal import argrelextrema
import dih_dir_finder as finder
import pickle
import dih_spike_picker as spike
import dih_spike_picker2 as spike2
import time
import dih_goes_getter as goes
from datetime import datetime
from datetime import timedelta
import simplejson
import os.path
import itertools
import ast
import shutil
from dih_event_range import dih_event_range
from dih_ev_peak_compare import dih_ev_peak_compare
#
#
#
#Name: dih_event_goes_scratch_select
#
#Purpose:takes file containing pairs of metadata for goes/131 at the same time and picks out the primary 131 peak and the nearest x-ray peak. Will also plot goes and 131 at the same time for each event.
#
#Input: filename -> txt file created by dih_sun_recurs_goes_plot, savename -> string to put in savenames
#
#Output: text file containing metadata about shared 131/goes peaks (with new correlated peaks), ps files containing shared plots (outputs to scratch)
#
#Example: gah = dih_event_goes_select('/metadata/131_goes_info.txt','savesunstring')
#
#Written: 8/10/14 Dan Herman daniel.herman@cfa.harvard.edu
#
def dih_event_goes_scratch_select(filename,savename):
	savepathmeta = '/Volumes/Scratch/Users/dherman/sundata/metadata/'
	meta_file = open(filename,'r')
	meta_lines = meta_file.readlines()
	#get data for 131 and goes
	total_end_result = []
	for member in meta_lines:
		member = ast.literal_eval(member)
		metadata_131 = member[0]
		if metadata_131[-5] == 'flag':
			print 'flag spotted'
			continue
		metadata_goes = member[1]
		primary_peak = metadata_131[4]
		compare_peaks = metadata_goes[3]+metadata_goes[4]
		compare_131_peaks = metadata_131[3]+metadata_131[4]
		if len(primary_peak) > 0:
			primary_dt = datetime.strptime(primary_peak[0],'%Y/%m/%d %H:%M:%S.%f')
		else:
			print "no primary peak in 131"
			continue	
		diff_list = []
		abs_diff_list = []
		target_goes_peak = []
		for peak in compare_peaks:
			peak_dt = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			diff = peak_dt-primary_dt
			diff_num = diff.total_seconds()
			abs_diff_num = abs(diff_num)
			diff_list.append(diff_num)
			abs_diff_list.append(abs_diff_num)
		min_list = [i for i, j in enumerate(abs_diff_list) if j == min(abs_diff_list)]
		if len(min_list) > 0:
			goes_index = min_list[0]
		else:
			print "no min"
			continue
		target_goes_peak.append(compare_peaks[goes_index])
		diff_list_131 = []
		abs_diff_list_131 = []
		target_131_peak = []
		primary_goes_dt = datetime.strptime(target_goes_peak[0],'%Y/%m/%d %H:%M:%S.%f')
		for peak in compare_131_peaks:
			peak_dt = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			diff = peak_dt-primary_goes_dt
			diff_num = diff.total_seconds()
			abs_diff_num = abs(diff_num)
			diff_list_131.append((-1)*diff_num)
			abs_diff_list_131.append(abs_diff_num)
		min_list_131 = [i for i, j in enumerate(abs_diff_list_131) if j == min(abs_diff_list_131)]
		aia_index = min_list_131[0]
		target_131_peak.append(compare_131_peaks[aia_index])
		if compare_131_peaks[aia_index] == compare_peaks[goes_index]:
			end_result = [metadata_131[0:3]+metadata_131[4:],metadata_goes[0:3]+target_goes_peak+metadata_goes[5:],diff_list[goes_index]]
			key = 137
		else:
			end_result = [metadata_131[0:3]+ target_131_peak + metadata_131[5:],metadata_goes[0:3]+target_goes_peak+metadata_goes[5:],diff_list_131[aia_index]]
			key = 11		
		#shared plotting regime
		goes_x = list(member[2])
		goes_y = list(member[3])
		goes_copy_y = list(member[3])
		aia_x = metadata_131[-4]
		aia_y = metadata_131[-3]
		aia_copy_y = aia_y
		x_peaklist = argrelextrema(np.array(aia_x),np.greater)
		x_minlist = argrelextrema(np.array(aia_x),np.less)
		#removes lightcurves whose times are not monotonic
		if len(x_peaklist[0])>0 or len(x_minlist[0]) >0:
			print 'wacky times'
			continue
		maxa = max(aia_y)
		maxb = max(goes_y)
		aia_y = (np.array(aia_y)-min(aia_y))/max(np.array(aia_y)-min(aia_y))
		goes_y = (np.array(goes_y)-min(goes_y))/max(np.array(goes_y)-min(goes_y))
		goes_start_time = datetime.strptime(metadata_goes[0],'%Y-%m-%dT%H:%M:%S.%f')
		aia_start_time = datetime.strptime(metadata_131[0],'%Y-%m-%dT%H:%M:%S.%f')
		start_diff = goes_start_time - aia_start_time
		start_num = start_diff.total_seconds()
		goes_x_adj = list(np.array(goes_x) - start_num)
		fig = plt.figure()
		fig =fig.add_axes([0.1, 0.1, 0.6, 0.75])
		plt.plot(goes_x,goes_y,'g',linewidth = 1.2, label = 'GOES 1-8 $\AA$')
		plt.plot(aia_x,aia_y,'k',linewidth = 1.2, label = 'AIA 131 $\AA$')
		for peak in metadata_131[3]:
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-aia_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(aia_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(aia_x[x_range_list[0]],aia_y[x_range_list[0]],'yD', markersize = 9)
		for peak in metadata_131[4]:
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-aia_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(aia_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(aia_x[x_range_list[0]],aia_y[x_range_list[0]],'ro', markersize = 9)
		for peak in metadata_goes[3]:
			print metadata_goes[3]
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-goes_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'yD', markersize = 9)
		for peak in metadata_goes[4]:
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-goes_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'gD', markersize = 9)
		if key == 137:
			for peak in target_goes_peak:
				peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
				x_range = (peak_time-goes_start_time).total_seconds()
				x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
				if len(x_range_list) > 0:
					plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'ro', markersize = 9)
				end_result.append(goes_copy_y[x_range_list[0]])
		if key == 11:
			for peak in target_goes_peak:
				peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
				x_range = (peak_time-goes_start_time).total_seconds()
				x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
				if len(x_range_list) > 0:
					plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'ro', markersize = 9)
					end_result.append(goes_copy_y[x_range_list[0]])
				else:
					end_result.append('cannot find goes')	
			for peak in target_131_peak:
				peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
				x_range = (peak_time-aia_start_time).total_seconds()
				x_range_list = [i for i, j in enumerate(aia_x) if j == x_range]
				if len(x_range_list) > 0:
					plt.plot(aia_x[x_range_list[0]],aia_y[x_range_list[0]],'ro', markersize = 9)
		total_end_result.append(end_result)
		end_file = open(savepathmeta + savename + '_all_human_meta_goes131_compared.txt','a')
		simplejson.dump(end_result,end_file)
		end_file.close()
		plt.ylabel('Normalized Flux Units')
		plt.xlabel('Seconds since ' + metadata_131[0])
		plt.title('Lightcurve at ' + metadata_131[0], y = 1.07)
		plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
		plt.savefig('/Volumes/Scratch/Users/dherman/sundata/sun_plots/' + savename + '_' + metadata_131[0] + '_' + str(metadata_131[-3][-1]) + '_131_goes_shared_plot.ps')
	return total_end_result	