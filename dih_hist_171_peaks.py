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
#
#
#
#Name: dih_hist_171_peaks
#
#Purpose: create time difference to 171 peaks and plot histogram of results
#
#
#Notes: add titles and axis labels!

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
				
			