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
			for member in data[4]:
				timeval = datetime.strptime(member,'%Y/%m/%d %H:%M:%S.%f')
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
			if peak[0]<member[0]+t_cusp and peak[0]>member[0]-t_cusp
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
#Name:dih_171_compare
#
#Purpose: same as dih_171_comparison
#
#Inputs: filename1 is a txt file where line represents the metadata for a single ivo event file
#filename2 is a txt file containing spatial data about the ivo event
#
#Outputs: txt file containing a list where each sublist is a group of related peaks
#
#Example: list = dih_171_compare('meta.txt','spatial.txt')
#
#Written: 7/11/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#


def dih_171_compare(filename1,filename2):
	meta_file = open(filename1,'r')
	meta_lines = meta_file.readlines()
	#Codes to create list of centers
	#
	#
	#
	centers = []
	for member in meta_lines:
		member = ast.literal_eval(member)
		if member[7] == 'flag':
			continue
		
	
	
    		
    		

            
            
        
        
                    
