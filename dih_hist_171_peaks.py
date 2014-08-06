import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab as P
import glob
import matplotlib.cm as cm
from scipy import signal
from dih_tableread import dih_filegrab
from dih_tableread import dih_tablereader
import dih_boxcar as d
from dih_lightcurvedata import dih_lightcurvedata
import dih_sunplot as datum
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
from scipy.stats import chisquare
import simplejson
import dih_boxavg as box
import os.path
import os
import shutil
import ast
from dih_max_comparison import dih_event_select
from dih_event_range import dih_event_range
from dih_max_comparison import dih_event_goes_select
import math
#
#
#
#Name: dih_hist_171_peaks
#
#Purpose: create time difference to channel peaks of choice and plot histogram of results
#
#Inputs: file containing information about shared peaks, savename for histogram, channel1 = channel to compare against, channel2 = channel to source other peaks from
#
#Outputs: histogram of time differences
#
#Example: gah = dih_hist_channel_peaks('shared_peaks.txt','hist.ps',193,171)
#
#Written: 7/17/14 Dan Herman daniel.herman@cfa.harvard.edu
#

def dih_hist_channel_peaks(infile,savename,channel1,channel2):
	peak_file = open(infile,'r')
	peak_list = peak_file.readlines()
	print peak_list
	peak_list = ast.literal_eval(peak_list[0])
	time_diff_channel = []
	for member in peak_list:
		time = datetime.strptime(member[0][0],'%Y-%m-%d %H:%M:%S.%f')
		others = member[1:len(member)]
		for guy in others:
			guy_time = datetime.strptime(guy[0],'%Y-%m-%d %H:%M:%S.%f')
			delt = time-guy_time
			time_diff_channel.append(-1*delt.total_seconds())
	P.figure()
	n, bins, patches = P.hist(time_diff_channel,10, histtype = 'stepfilled')
	P.setp(patches, 'facecolor','b','alpha',0.75)
	P.xlabel('Time Difference between '+str(channel1)+' and ' + str(channel2) + ' peak in seconds')
	P.ylabel('Number of Peaks')
	P.title('Histogram of ' + str(channel1) + ' & ' + str(channel2) + ' Separations')
	P.savefig(savename)
	return time_diff_channel
#
#Name: dih_hist_events
#
#Purpose: flexibly create histogram for two channels of choice displaying separation between peaks in those channels
#
#Inputs: filename1 -> metadata to analyze, savename -> save name for histogram, channel1 -> target channel, channel2 -> testing channel
#
#Outputs: histogram and final data [time differences,source ivo for channel1, source ivo for channel2]
#
#Example: gah = dih_hist_events('metadata.txt','hist.ps',193,131)
#
#Written: 7/18/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_hist_events(filename1,savename,channel1,channel2):
	#get event sets
	uber_list = dih_event_select(filename1)
	time_diff_channel = []
	target_ivo = []
	target_time_list = []
	other_time_list = []
	other_ivo = []
	outlier_list = []
	for member in uber_list:
		for guy in member:
			target = []
			other = []
			for dude in guy:
				dude = list(dude)
				if dude[1] == channel1:
					target.append(dude)
				if dude[1] == channel2:
					other.append(dude)
			#making sure lists are correct sizes
			if len(target) > 1:
				target = [target[0]]
			elif len(target) == 0:
				continue	
			if len(other) > 1:
				other = [other[0]]
			elif len(other) == 0:
				continue
			target_time = datetime.strptime(target[0][0],'%Y/%m/%d %H:%M:%S.%f')
			other_time = datetime.strptime(other[0][0],'%Y/%m/%d %H:%M:%S.%f')
			delt = other_time-target_time
			time_diff_channel.append(delt.total_seconds())
			target_ivo.append(target[0][2])
			other_ivo.append(other[0][2])
			target_time_list.append(target[0][0])
			other_time_list.append(other[0][0])
			if abs(delt.total_seconds()) > 500:
				outlier_data = (delt.total_seconds,target[0][2],other[0][2],target[0][0],other[0][2])
				outlier_list.append(outlier_data)
	final = [time_diff_channel,target_ivo,other_ivo,target_time_list,other_time_list]
	final = list(set(zip(*final)))
	final = zip(*final)
	if len(time_diff_channel) == 0:
		return [channel1,channel2,'no matches']
	final.append(channel1)
	final.append(channel2)
	final.append(outlier_list)
	P.figure()
	print final
	print 'here'
	n, bins, patches = P.hist(list(final[0]),10, histtype = 'stepfilled')
	final.append(tuple(n))
	final.append(tuple(bins))
	P.setp(patches, 'facecolor','b','alpha',0.75)
	P.xlabel('Time Difference between '+str(channel1)+' and ' + str(channel2) + ' peak in seconds')
	P.ylabel('Number of Peaks')
	P.title('Histogram of ' + str(channel1) + ' & ' + str(channel2) + ' Separations')
	P.savefig(savename)
		
	return final 		
			
#
#Name: dih_hist_crop_events
#
#Purpose: flexibly create histogram for two channels of choice displaying separation between peaks in those channels (for events processed with dih_sun_cropped_plotter)
#
#Inputs: filename1 -> metadata to analyze, savename -> save name for histogram, channel1 -> target channel, channel2 -> testing channel
#
#Outputs: histogram and final data [time differences,source ivo for channel1, source ivo for channel2]
#
#Example: gah = dih_hist_events('metadata.txt','hist.ps',193,131)
#
#Written: 7/29/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_hist_crop_events(filename1,savename,channel1,channel2):
	#get event sets
	uber_list = dih_event_crop_select(filename1)
	time_diff_channel = []
	target_ivo = []
	target_time_list = []
	other_time_list = []
	other_ivo = []
	outlier_list = []
	for member in uber_list:
		for guy in member:
			target = []
			other = []
			for dude in guy:
				dude = list(dude)
				if dude[1] == channel1:
					target.append(dude)
				if dude[1] == channel2:
					other.append(dude)
			#making sure lists are correct sizes
			if len(target) > 1:
				target = [target[0]]
			elif len(target) == 0:
				continue	
			if len(other) > 1:
				other = [other[0]]
			elif len(other) == 0:
				continue
			target_time = datetime.strptime(target[0][0],'%Y/%m/%d %H:%M:%S.%f')
			other_time = datetime.strptime(other[0][0],'%Y/%m/%d %H:%M:%S.%f')
			delt = other_time-target_time
			time_diff_channel.append(delt.total_seconds())
			target_ivo.append(target[0][2])
			other_ivo.append(other[0][2])
			target_time_list.append(target[0][0])
			other_time_list.append(other[0][0])
			if abs(delt.total_seconds()) > 500:
				outlier_data = (delt.total_seconds,target[0][2],other[0][2],target[0][0],other[0][2])
				outlier_list.append(outlier_data)
	final = [time_diff_channel,target_ivo,other_ivo,target_time_list,other_time_list]
	final = list(set(zip(*final)))
	final = zip(*final)
	if len(time_diff_channel) == 0:
		return [channel1,channel2,'no matches']
	final.append(channel1)
	final.append(channel2)
	final.append(outlier_list)
	P.figure()
	print final
	print 'here'
	n, bins, patches = P.hist(list(final[0]),10, histtype = 'stepfilled')
	final.append(tuple(n))
	final.append(tuple(bins))
	P.setp(patches, 'facecolor','b','alpha',0.75)
	P.xlabel('Time Difference between '+str(channel1)+' and ' + str(channel2) + ' peak in seconds')
	P.ylabel('Number of Peaks')
	P.title('Histogram of ' + str(channel1) + ' & ' + str(channel2) + ' Separations')
	P.savefig(savename)
		
	return final 		
#
#
#
#
#Name: dih_hist_goes_131
#
#Purpose: takes data from dih_event_goes_select and plots a histogram of separations
#
#Inputs: same as dih_event_goes_select
#
#Outputs: end_hist_data_no_copy -> (131 peak, goes peak, separation), final -> (contents of bin, bins)
#
#Example: gah = dih_hist_goes_131('/metadata/info.txt','supersaved')
#
#Written: 7/31/14 Dan Herman daniel.herman@cfa.harvard.edu
#
def dih_hist_goes_131(filelist,savename):
	all_data = dih_event_goes_select('/data/george/dherman/metadata/' + filelist[0] + '_all_human_meta_131_goes.txt',savename)
	for idx,member in enumerate(filelist):
		if idx < 1:
			continue
		all_data = all_data + dih_event_goes_select('/data/george/dherman/metadata/' + filelist[idx] + '_all_human_meta_131_goes.txt',savename)
	hist_data = []
	end_hist_data = []
	for member in all_data:
		hist_data.append(member[2])
		end_hist_data.append((member[0][3],member[1][3],member[2],member[3]))
	end_columns = zip(*end_hist_data)
	goes_time_set = list(set(end_columns[1]))
	goes_class_set = []
	end_hist_data_no_copy = []
	hist_data_no_copy = []
	for member in goes_time_set:
		test_list = []
		test_list2 =[]
		for idx,pair in enumerate(end_hist_data):
			if pair[1] == member:
				test_list.append(pair)
				test_list2.append(hist_data[idx])
			else:
				continue
		end_hist_data_no_copy.append(test_list[0])
		hist_data_no_copy.append(test_list2[0])
		goes_class_set.append(test_list[0])
	P.figure()
	maxhistprimary = math.ceil(max(hist_data_no_copy)/25)*25
	minhistprimary = math.floor(min(hist_data_no_copy)/25)*25
	n, bins, patches = P.hist(hist_data_no_copy,bins = np.arange(int(minhistprimary),int(maxhistprimary + 1),25) ,histtype = 'stepfilled')
	final = []
	final.append('GOES and 131 Histogram data: n,bins')
	final.append(tuple(n))
	final.append(tuple(bins))
	P.setp(patches, 'facecolor','b','alpha',0.75)
	P.xlabel('Time Difference between GOES and 131 peak in seconds')
	P.ylabel('Number of Peaks')
	P.title('Histogram of GOES 1-8 $\AA$ and AIA 131 $\AA$ Separations')
	P.savefig('/home/dherman/Documents/sun_plots/' + savename + '_131_goes_hist.ps')
	hist_data_file1 = open('/data/george/dherman/metadata/' + savename + '_131_goes_hist_data.txt','w')
	hist_data_file2 = open('/data/george/dherman/metadata/' + savename + '_131_goes_hist_metadata.txt','w')
	hist_data_file1.write(str(end_hist_data_no_copy))
	hist_data_file2.write(str(final))
	hist_data_file1.close()
	hist_data_file2.close()
	print goes_class_set
	goes_A = [j for j in goes_class_set if j[-1] < 10**(-7)]
	goes_B = [j for j in goes_class_set if j[-1] < 10**(-6) and j[-1] > 10**(-7)]
	goes_C = [j for j in goes_class_set if j[-1] < 10**(-5) and j[-1] > 10**(-6)]
	goes_M = [j for j in goes_class_set if j[-1] < 10**(-4) and j[-1] > 10**(-5)]
	goes_X = [j for j in goes_class_set if j[-1] < 10**(-3) and j[-1] > 10**(-4)]
	goes_all = [goes_A,goes_B,goes_C,goes_M,goes_X]
	print goes_all
	xTickMarks = ['A','B','C','M','X']
	for idx,member in enumerate(goes_all):
		if len(member) > 0:
			goes_columns = zip(*member)
			P.figure()
			maxhist = math.ceil(max(goes_columns[-2])/25)*25
			print 'hists'
			print str(maxhist)
			minhist = math.floor(min(goes_columns[-2])/25)*25
			print str(minhist)
			n, bins, patches = P.hist(goes_columns[-2],bins = np.arange(int(minhist),int(maxhist+1),25) ,histtype = 'stepfilled')
			final = []
			final.append('GOES and 131 Histogram data: n,bins')
			final.append(tuple(n))
			final.append(tuple(bins))
			P.setp(patches, 'facecolor','b','alpha',0.75)
			P.xlabel('Time Difference between GOES and 131 peak in seconds')
			P.ylabel('Number of Peaks')
			P.title('Histogram of class ' + xTickMarks[idx] + ' GOES 1-8 $\AA$ and AIA 131 $\AA$ Separations')
			P.savefig('/home/dherman/Documents/sun_plots/' + savename + '_131_goes_' + xTickMarks[idx] + '_hist.ps')
			hist_data_file_a = open('/data/george/dherman/metadata/' + savename + '_131_goes_' + xTickMarks[idx] + '_hist_data.txt','w')
			hist_data_file_b = open('/data/george/dherman/metadata/' + savename + '_131_goes_' + xTickMarks[idx] + '_hist_metadata.txt','w')
			hist_data_file_a.write(str(goes_columns))
			hist_data_file_b.write(str(final))
			hist_data_file_a.close()
			hist_data_file_b.close()
	goes_num = [len(goes_A),len(goes_B),len(goes_C),len(goes_M),len(goes_X)]
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ind = np.arange(len(goes_num))
	width = .7
	rects1 = ax.bar(ind, goes_num, width,color='black')
	ax.set_xlim(-width,len(ind)+width)
	ax.set_ylim(0,45)
	ax.set_ylabel('Number of Events')
	ax.set_title('Distribution of GOES Events by Class')
	ax.set_xticks(ind+width)
	xtickNames = ax.set_xticklabels(xTickMarks)
	plt.setp(xtickNames, rotation=45, fontsize=20)
	plt.savefig('/home/dherman/Documents/sun_plots/' + savename + '_131_goes_class_hist.ps')
	hist_data_file3 = open('/data/george/dherman/metadata/' + savename + '_131_goes_class_hist_data.txt','w')
	final_two = [tuple(goes_num),tuple(xTickMarks)]
	hist_data_file3.write(str(final_two))
	return [end_hist_data_no_copy,final,final_two]							
				
			