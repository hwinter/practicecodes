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
from dih_shared_plot import dih_shared_groups
from dih_event_range import dih_event_range
from dih_ev_peak_compare import dih_ev_peak_compare
#Name: dih_max_comparison
#
#Purpose: finds absolute peaks in different channels that correspond to each other temporally
#
#Inputs: Directory containing directory containing fits files to be analyzed (dirname) and
#name used to save data sets from given directory (filename)
#
#Outputs:returns list of lists where each sublist represents a group of temporally related events
#
#Example: peakgrouplist = dih_max_comparison('/ivo/fits','sunnyplot')
#
#Written: 7/8/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#


def dih_max_comparison(dirname,filename):
	fitslist = finder.dih_dir_finder(dirname)[0]#source ivo files to count over
	ivolist = finder.dih_dir_finder(dirname)[1]
	peaklist = []
	sharedlist = []
	for idx,member in enumerate(fitslist):
		if os.path.isfile(filename+'_human_meta'+str(idx)+'.txt') == False:
			continue
		else:
			data = simplejson.load(open(filename+'_human_meta'+str(idx)+'.txt','rb'))
			for member in data[4]:#create manageable peak data sets
				timeval = datetime.strptime(member,'%Y/%m/%d %H:%M:%S.%f')
				channel = data[1]
				values = [timeval,channel,ivolist[idx]]
				peaklist.append(values)
	cusp = timedelta(seconds = 180)#set temporal relatedness factor
	for idx,member in enumerate(peaklist):
		subsharedlist = []
		subsharedlist.append(member)
		separate_list = peaklist[0:idx] + peaklist[idx+1:len(peaklist)]
		for guy in separate_list:#populate subsharedlist with closely related peaks
			if guy[0]< member[0]+cusp and guy[0]>member[0]-cusp and guy[1] != member[1]:
				subsharedlist.append(guy)
				continue
			else:
				continue
		sharedlist.append(subsharedlist)
	for member in sharedlist:
		for item in member:
			item[0] = str(item[0])
	with open(filename+'_pickled_timerel_peaks.txt','wb') as fff:
		pickle.dump(sharedlist,fff)
	savefile = open(filename+'_timerel_peaks.txt','wb')
	simplejson.dump(sharedlist,savefile)
	savefile.close()
	return sharedlist
		
#
#
#Name: dih_171_comparison
#
#Purpose: sorts list of peaks into groups based upon temporal and spatial relatedness to 171 peaks
#
#inputs: Overall directory containing ivo files containing fits files to be analyzed (dirname)
#savename used when originally creating sunpy maps (filename1)
#savename used to create metadata tex files from Trae (filename2)
#
#Outputs: sharedlist containing lists of related peaks
#
#Example: list = dih_171_comparison('/Volumes/Scratch/Users/dherman/data_whoa','sunnywhoa','traetext.txt')
#
#Written: 7/10/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_171_comparison(dirname,filename1,filename2):
	fitslist = finder.dih_dir_finder(dirname)[0]
	all_peaks = []
	for idx,member in enumerate(fitslist):
		if os.path.isfile(filename1 + '_human_meta' + str(idx) + '.txt') == False:
			continue
		else:
			data = simplejson.load(open(filename + '_human_meta' + str(idx) + '.txt','rb'))
			if data[7] == 'flag':
				continue
			#code will need to be changed once true format of text file is known
			#file = open(filename2,'r')
			#lines = file.readlines()
			#center = lines[3]
			for guy in data[4]:
				timeval = datetime.strptime(guy,'%Y/%m/%d %H:%M:%S.%f')
				channel = data[1]
				all_peaks.append([timeval,channel])
	list171 = [j for j, j in enumerate(all_peaks) if j[1] == 171]
	other_list = [j for j, j in enumerate(all_peaks) if j[1] != 171]
	t_cusp = timedelta(seconds = 180)
	s_cusp = 3.0
	sharedlist = []
	for idx,peak in enumerate(list171):
		subsharedlist = [peak]
		for member in other_list:#if peak[0]<member[0]+t_cusp and peak[0]>member[0]-t_cusp and peak[2][0]<member[2][0]+s_cusp and peak[2][0]>member[2][0]-s_cusp and peak[1][0]<member[1][0]+s_cusp and peak[1][0]>member[1][0]-s_cusp:
			if peak[0]<member[0]+t_cusp and peak[0]>member[0]-t_cusp:
				subsharedlist.append(member)
				continue
			else:
				continue
		subsharedlist = list(set(subsharedlist))
		sharedlist.append(subsharedlist)
	for member in sharedlist:
		for item in member:
			item[0] = str(item[0])
	with open(filename1+'_pickled_related_peaks.txt','wb') as fff:
		pickle.dump(sharedlist,fff)
	savefile = open(filename1+'_related_peaks.txt','wb')
	simplejson.dump(sharedlist,savefile)
	savefile.close()
	return sharedlist
#
#
#Name:dih_channel_compare
#
#Purpose: same as dih_171_comparison but can compare any two channels to each other
#
#Inputs: filename1 is a txt file where line represents the metadata for a single ivo event file
#filename2 is a txt file containing spatial data about the ivo event,channel1 is the channel to be selected as the base of comparison, channel2 is the channel to compare against channel1
#
#Outputs: txt file containing a list where each sublist is a group of related peaks
#
#Example: list = dih_channel_compare('meta.txt','spatial.txt')
#
#Written: 7/11/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#


def dih_channel_compare(filename1,savename,channel1,channel2):
	meta_file = open(filename1,'r')
	meta_lines = meta_file.readlines()
	print len(meta_lines)
	#Codes to create list of centers
	#
	#
	#
	#centers = []
	all_peaks = []
	for idx,member in enumerate(meta_lines):
		member = ast.literal_eval(member)
		print member
		print idx
		if member[7] == 'flag':
			print 'flag'
			continue
		for guy in member[4]:
			timeval = datetime.strptime(guy,'%Y/%m/%d %H:%M:%S.%f')
			channel = member[1]
			ivo = member[5]
			all_peaks.append([timeval,channel,ivo])
	list_target = [j for j, j in enumerate(all_peaks) if j[1] == channel1]
	other_list = [j for j, j in enumerate(all_peaks) if j[1] == channel2]
	print len(list_target)
	print len(other_list)
	t_cusp = timedelta(seconds = 1000)
	sharedlist = []
	for idx,peak in enumerate(list_target):
		subsharedlist = [peak]
		for member in other_list:
			if peak[0]<member[0]+t_cusp and peak[0]>member[0]-t_cusp:	
				subsharedlist.append(member)
				continue
			else:
				continue
		sharedlist.append(subsharedlist)
	for member in sharedlist:
		for item in member:
			item[0] = str(item[0])
	with open(savename+'_pickled_related_peaks.txt','wb') as fff:
		pickle.dump(sharedlist,fff)
	savefile = open('/data/george/dherman/metadata/'+savename+'_related_peaks.txt','wb')
	simplejson.dump(sharedlist,savefile)
	savefile.close()
	return sharedlist
#
#Name: dih_event_select
#
#Purpose: selects primary peaks and the peaks in other channels that are closest to the primary peak
#
#Inputs: filename1 -> metadata
#
#Outputs: list of lists where each sublist contains lists of related peaks
#
#Example: uber_list = dih_event_select('meta.txt')
#
#Written:7/18/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#

def dih_event_select(filename1):
	#get list of related start times
	shared_times = dih_shared_groups(filename1)
	meta_file = open(filename1, 'r')
	meta_lines = meta_file.readlines()
	all_meta_datalist = []
	for member in meta_lines:
		member = ast.literal_eval(member)
		all_meta_datalist.append(member)
	event_list = []
	#getting full metadata for each event with time in shared_times
	for member in shared_times:
		event = []
		for guy in member:
			for part in all_meta_datalist:
				if part[0] == guy:
					event.append(part)
					break	
		event_list.append(event)
	uber_shared_list = []
	for idx,member in enumerate(event_list):
		print idx
		primary_peaks = []
		secondary_peaks = []
		#setting cut_off so program knows to ignore extra long data sets
		cut_off = timedelta(seconds = dih_event_range(member))
		print cut_off
		for guy in member:
			cut_off_time = datetime.strptime(guy[0],'%Y-%m-%dT%H:%M:%S.%f')+cut_off
			if guy [7] == 'flag':
				print 'flag'
				continue
			#getting relative peaks
			for tim in guy[3]:
				timeval = datetime.strptime(tim,'%Y/%m/%d %H:%M:%S.%f')
				channel = guy[1]
				ivo = guy[5]
				if timeval < cut_off_time:
					secondary_peaks.append((timeval,channel,ivo))
			#getting primary peaks
			for tim in guy[4]:
				timeval = datetime.strptime(tim,'%Y/%m/%d %H:%M:%S.%f')
				channel = guy[1]
				ivo = guy[5]
				if timeval < cut_off_time:
					primary_peaks.append((timeval,channel,ivo))
		shared_peak_list = []
		#Attempt at removing extra events in every channel (needs to be refined most likely)
		channel_list = [171,131,211,304,335,193]
		primary_no_copy_peaks = []
		for idx,channel in enumerate(channel_list):
			channel_group = [j for j, j in enumerate(primary_peaks) if j[1] == channel]
			if len(channel_group) > 0:
				primary_no_copy_peaks.append(channel_group[0])
			else:
				continue
		all_peaks = primary_no_copy_peaks + secondary_peaks
		#comparing primary peaks to all other peaks in other channels
		for peak in primary_no_copy_peaks:
			print peak	
			peak_time = datetime.strftime(peak[0],'%Y/%m/%d %H:%M:%S.%f')
			sub_peak_list = [(peak_time,peak[1],peak[2])]
			compare_peaks = [j for j, j in enumerate(all_peaks) if j[1] != peak[1]]
			compare_list = []
			for channel in channel_list:
				compare_peaks_by_channel = list(set([j for j, j in enumerate(compare_peaks) if j[1] == channel]))
				compare_list.append(compare_peaks_by_channel)
			for group in compare_list:
				compare_times = []
				for thing in group:
					time_diff = peak[0]-thing[0]
					num_diff = abs(time_diff.total_seconds())
					compare_times.append(num_diff)
				compare_min = [i for i, j in enumerate(compare_times) if j == min(compare_times)]
				if len(compare_min) == 1:
					interest = list(group[compare_min[0]])
					interest[0] = datetime.strftime(interest[0],'%Y/%m/%d %H:%M:%S.%f')
					print interest
					sub_peak_list.append(tuple(interest))		
			shared_peak_list.append(list(set(tuple(sub_peak_list))))
		uber_shared_list.append(shared_peak_list)			
	return uber_shared_list	
#
#Name: dih_event_crop_select
#
#Purpose: selects primary peaks and the peaks in other channels that are closest to the primary peak from original event file
#
#Inputs: filename1 -> file containing metadata created by dih_sun_cropped_plotter (or equivalent program)
#
#Outputs: list of lists where each sublist contains lists of related peaks
#
#Example: uber_list = dih_event_select('meta.txt')
#
#Written:7/29/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#

def dih_event_crop_select(filename1):
	#get list of related start times
	shared_times = dih_shared_groups(filename1)
	meta_file = open(filename1, 'r')
	meta_lines = meta_file.readlines()
	all_meta_datalist = []
	for member in meta_lines:
		member = ast.literal_eval(member)
		all_meta_datalist.append(member)
	event_list = []
	#getting full metadata for each event with time in shared_times
	for member in shared_times:
		event = []
		for guy in member:
			for part in all_meta_datalist:
				if part[0] == guy:
					event.append(part)
					break	
		event_list.append(event)
	uber_shared_list = []
	for idx,member in enumerate(event_list):
		print idx
		#setting cut_off so program knows to ignore extra long data sets
		cut_off = timedelta(seconds = dih_event_range(member))
		print cut_off
		shared_list = []
		for guy in member:
			cut_off_time = datetime.strptime(guy[0],'%Y-%m-%dT%H:%M:%S.%f')+cut_off
			#find peak that corresponds to peak from original event file
			peak_target = dih_ev_peak_compare(guy[3]+guy[4],guy[10][0])
			channel = guy[1]
			ivo = guy[5]
			if peak_target < cut_off_time:
				shared_list.append((datetime.strftime(peak_target,'%Y/%m/%d %H:%M:%S.%f'),channel,ivo))
		channel_list = [131,171,211,304,335,193]
		shared_no_copy_list = []
		for idx,channel in enumerate(channel_list):
			channel_group = [j for j, j in enumerate(shared_list) if j[1] == channel]
			if len(channel_group)>0:
				shared_no_copy_list.append(channel_group[0])
			else:
				continue
		uber_shared_list.append(shared_no_copy_list)
	return uber_shared_list
#
#Name: dih_event_goes_select
#
#Purpose:takes file containing pairs of metadata for goes/131 at the same time and picks out the primary 131 peak and the nearest x-ray peak. Will also plot goes and 131 at the same time for each event.
#
#Input: filename -> txt file created by dih_sun_recurs_goes_plot, savename -> string to put in savenames
#
#Output: text file containing metadata about shared 131/goes peaks (with new correlated peaks), ps files containing shared plots
#
#Example: gah = dih_event_goes_select('/metadata/131_goes_info.txt','savesunstring')
#
#Written: 7/31/14 Dan Herman daniel.herman@cfa.harvard.edu
#
def dih_event_goes_select(filename,savename):
	meta_file = open(filename,'r')
	meta_lines = meta_file.readlines()
	#get data for 131 and goes
	total_end_result = []
	for member in meta_lines:
		member = ast.literal_eval(member)
		metadata_131 = member[0]
		#get rid of flags
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
		#compare the peaks by time difference
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
		plt.plot(goes_x,goes_y,'b',linewidth = 1.0, label = 'GOES 1-8 $\AA$')
		plt.plot(aia_x,aia_y,'r',linewidth = 1.0, label = 'AIA 131 $\AA$')
		#plot peaks
		for peak in metadata_131[3]:
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-aia_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(aia_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(aia_x[x_range_list[0]],aia_y[x_range_list[0]],'yD', markersize = 8)
		for peak in metadata_131[4]:
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-aia_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(aia_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(aia_x[x_range_list[0]],aia_y[x_range_list[0]],'ro', markersize = 8)
		for peak in metadata_goes[3]:
			print metadata_goes[3]
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-goes_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'yD', markersize = 8)
		for peak in metadata_goes[4]:
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-goes_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'gD', markersize = 8)
		if key == 137:
			for peak in target_goes_peak:
				peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
				x_range = (peak_time-goes_start_time).total_seconds()
				x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
				if len(x_range_list) > 0:
					plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'ro', markersize = 8)
				end_result.append(goes_copy_y[x_range_list[0]])
		if key == 11:
			for peak in target_goes_peak:
				peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
				x_range = (peak_time-goes_start_time).total_seconds()
				x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
				if len(x_range_list) > 0:
					plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'ro', markersize = 8)
					end_result.append(goes_copy_y[x_range_list[0]])
				else:
					end_result.append('cannot find goes')	
			for peak in target_131_peak:
				peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
				x_range = (peak_time-aia_start_time).total_seconds()
				x_range_list = [i for i, j in enumerate(aia_x) if j == x_range]
				if len(x_range_list) > 0:
					plt.plot(aia_x[x_range_list[0]],aia_y[x_range_list[0]],'ro', markersize = 8)
		total_end_result.append(end_result)
		end_file = open('/data/george/dherman/metadata/' + savename + '_all_human_meta_goes131_compared.txt','a')
		simplejson.dump(end_result,end_file)
		end_file.close()
		plt.ylabel('Normalized Flux Units')
		plt.xlabel('Seconds since ' + metadata_131[0])
		plt.title('Lightcurve at ' + metadata_131[0], y = 1.07)
		plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
		plt.savefig('/data/george/dherman/sun_plots/' + savename + '_' + metadata_131[0] + '_' + str(metadata_131[-3][-1]) + '_131_goes_shared_plot.ps')
	return total_end_result
#
#
#
#
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
		plt.plot(goes_x,goes_y,'b',linewidth = 1.0, label = 'GOES 1-8 $\AA$')
		plt.plot(aia_x,aia_y,'r',linewidth = 1.0, label = 'AIA 131 $\AA$')
		for peak in metadata_131[3]:
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-aia_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(aia_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(aia_x[x_range_list[0]],aia_y[x_range_list[0]],'yD', markersize = 8)
		for peak in metadata_131[4]:
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-aia_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(aia_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(aia_x[x_range_list[0]],aia_y[x_range_list[0]],'ro', markersize = 8)
		for peak in metadata_goes[3]:
			print metadata_goes[3]
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-goes_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'yD', markersize = 8)
		for peak in metadata_goes[4]:
			peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
			x_range = (peak_time-goes_start_time).total_seconds()
			x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
			if len(x_range_list) > 0:
				plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'gD', markersize = 8)
		if key == 137:
			for peak in target_goes_peak:
				peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
				x_range = (peak_time-goes_start_time).total_seconds()
				x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
				if len(x_range_list) > 0:
					plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'ro', markersize = 8)
				end_result.append(goes_copy_y[x_range_list[0]])
		if key == 11:
			for peak in target_goes_peak:
				peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
				x_range = (peak_time-goes_start_time).total_seconds()
				x_range_list = [i for i, j in enumerate(goes_x) if j == x_range]
				if len(x_range_list) > 0:
					plt.plot(goes_x_adj[x_range_list[0]],goes_y[x_range_list[0]],'ro', markersize = 8)
					end_result.append(goes_copy_y[x_range_list[0]])
				else:
					end_result.append('cannot find goes')	
			for peak in target_131_peak:
				peak_time = datetime.strptime(peak,'%Y/%m/%d %H:%M:%S.%f')
				x_range = (peak_time-aia_start_time).total_seconds()
				x_range_list = [i for i, j in enumerate(aia_x) if j == x_range]
				if len(x_range_list) > 0:
					plt.plot(aia_x[x_range_list[0]],aia_y[x_range_list[0]],'ro', markersize = 8)
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
			
			
			
		
		
		
	
	
	
	
	
	
	
	
	
		
    	
            
            
        
        
                    
