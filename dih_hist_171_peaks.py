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
							
				
			