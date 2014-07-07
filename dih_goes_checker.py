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
#
#
#Name: dih_goes_checker
#
#Purpose: given dirname containing directories with fits files, filename used to save the data from the fits files and
#either max or rel keywords, this function will return GOES events within 3 minutes before and after either the absolute peak 
#of the AIA curve (max ==1) or the relative peaks of the AIA curve (rel == 1)
#
#
#Inputs: directory containing folders with fits files (dirname) in order to obtain length for for loop to run over, save name (filename) used to create raw data/metadata for the files in dirname
#
#
#Outputs: List of eventlists with idx matching idx of fitslist
#
#Examples: events = dih_goes_checker('/user/ivo/fits','sunnyplots')
#
#Written: 7/7/14 Dan Herman	daniel.herman@cfa.harvard.edu
#
#

def dih_goes_checker(dirname,filename,max,rel):
	fitslist = finder.dih_dir_finder(dirname)
	eventlist = []
	for idx,member in enumerate(fitslist):
		data = dih_filegrab(filename+'metacol'+str(idx)+'.txt')
		if max == 1 and rel == 0:
			peaklist = []
			for member in data[4]:
				timeval = datetime.strptime(member,'%Y/%m/%d %H:%M:%S.%f')
				peaklist.append(timeval)
		elif rel == 1 and max == 0:
			peaklist = []
			for member in data[3]:
				timeval = datetime.strptime(member,'%Y/%m/%d %H:%M:%S.%f')
				peaklit.append(timeval)
		else:
			print "bad keyword choice"
		for member in peaklist:
			time1 = member - timedelta(seconds = 180)
			time2 = member + timedelta(seconds = 180)
			subeventlist = dih_goes_getter(time1,time2)
			if len(subeventlist) > 0:
				print "Found Goes Event(s) near AIA Event"
			else:
				print "No Goes Event near AIA Event"
			eventlist.append(subeventlist)
	np.savetxt(filename+'GOESevents.txt',np.column_stack((eventlist)),header = 'Eventlist created on '+time.strftime("%c"))
	return eventlist