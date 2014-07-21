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
		primary_171 = [j for j, j in enumerate(primary_peaks) if j[1] = 171]
		primary_131 = [j for j, j in enumerate(primary_peaks) if j[1] = 131]
		primary_211 = [j for j, j in enumerate(primary_peaks) if j[1] = 211]
		primary_304 = [j for j, j in enumerate(primary_peaks) if j[1] = 304]
		primary_335 = [j for j, j in enumerate(primary_peaks) if j[1] = 335]
		primary_193 = [j for j, j in enumerate(primary_peaks) if j[1] = 193]
		primary_no_copy_peaks = []
		primary_no_copy_peaks.append(primary_171[0])
		primary_no_copy_peaks.append(primary_131[0])
		primary_no_copy_peaks.append(primary_211[0])
		primary_no_copy_peaks.append(primary_304[0])
		primary_no_copy_peaks.append(primary_335[0])
		primary_no_copy_peaks.append(primary_193[0])
		all_peaks = primary_no_copy_peaks + secondary_peaks
		#comparing primary peaks to all other peaks in other channels
		for peak in primary_no_copy_peaks:
			print peak	
			peak_time = datetime.strftime(peak[0],'%Y/%m/%d %H:%M:%S.%f')
			sub_peak_list = [(peak_time,peak[1],peak[2])]
			compare_peaks = [j for j, j in enumerate(all_peaks) if j[1] != peak[1]]
			compare_peaks_171 = list(set([j for j, j in enumerate(compare_peaks) if j[1] == 171]))
			compare_peaks_131 = list(set([j for j, j in enumerate(compare_peaks) if j[1] == 131]))
			compare_peaks_193 = list(set([j for j, j in enumerate(compare_peaks) if j[1] == 193]))
			compare_peaks_335 = list(set([j for j, j in enumerate(compare_peaks) if j[1] == 335]))
			compare_peaks_304 = list(set([j for j, j in enumerate(compare_peaks) if j[1] == 304]))
			compare_peaks_211 = list(set([j for j, j in enumerate(compare_peaks) if j[1] == 211]))
			compare_list = [compare_peaks_171,compare_peaks_131,compare_peaks_193,compare_peaks_335,compare_peaks_304,compare_peaks_211]
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
	
	
	
	
	
	
	
	
	
	
	
		
    		
    		

            
            
        
        
                    
