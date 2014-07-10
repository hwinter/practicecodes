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
	peaklist = []
	sharedlist = []
	for idx,member in enumerate(fitslist):
		data = simplejson.load(open(filename+'_human_meta'+str(idx)+'.txt','rb'))
		for member in data[4]:
			timeval = datetime.strptime(member,'%Y/%m/%d %H:%M:%S.%f')
			channel = data[1]
			peaklist.append([timeval,channel])
	cusp = datetime.timedelta(seconds = 180)
	for idx,member in enumerate(peaklist):
		poppedlist = list.pop([idx])
		subsharedlist = []
		subsharedlist.append(member)
		for guy in poppedlist:
			if guy[0]< member[0]+cusp and guy[0]>member[0]-cusp and guy[1] != member[1]:
				subsharedlist.append(guy)
				continue
			else:
				continue
		subsharedlist = list(set(subsharedlist))
		sharedlist.append(subsharedlist)
	np.savetxt(filename+'sharedpeaks.txt',np.column_stack((subsharedlist)),header = 'List of shared peaks created on '+time.strftime("%c"))
	return sharedlist
		
#
#
#Name: dih_171_comparison
#
def dih_171_comparison(dirname,filename1,filename2):
	fitslist = finder.dih_dir_finder(dirname)[0]
    all_peaks = []
    for idx,member in enumerate(fitslist):
        if os.path.is_file(filename1+_'human_meta'+str(idx)+'.txt') == False:
            continue
        else:
            data = simplejson.load(open(filename+'_human_meta'+str(idx)+'.txt','rb'))
            for member in data[4]:
                timeval = datetime.strptime(member,'%Y/%m/%d %H:%M:%S.%f')
                channel = data[1]
                all_peaks.append([timeval,channel])
    for peak in all_peaks:
        
        
				
		
	
	
