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
from scipy.stats import skew
from scipy.stats import kurtosis
import simplejson
import dih_boxavg as box
import os.path
import os
import shutil
import ast
import math
from dih_event_goes_scratch_select import dih_event_goes_scratch_select
#
#Name: dih_hist_goes_131_scratch
#
#Purpose: takes data from dih_event_goes_select and plots a histogram of separations
#
#Inputs: same as dih_event_goes_select
#
#Outputs: end_hist_data_no_copy -> (131 peak, goes peak, separation), final -> (contents of bin, bins) (outputs directed to scratch)
#
#Example: gah = dih_hist_goes_131('/metadata/info.txt','supersaved')
#
#Written: 7/31/14 Dan Herman daniel.herman@cfa.harvard.edu
#
def dih_hist_goes_131_scratch(filelist,savename):
	savepathmeta = '/Volumes/Scratch/Users/dherman/sundata/metadata/'
	all_data = dih_event_goes_scratch_select(savepathmeta + filelist[0] + '_all_human_meta_131_goes.txt',savename)
	for idx,member in enumerate(filelist):
		if idx < 1:
			continue
		all_data = all_data + dih_event_goes_scratch_select(savepathmeta + member + '_all_human_meta_131_goes.txt',savename)
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
	f = P.figure()
	ax = f.add_subplot(111)
	maxhistprimary = math.ceil(max(hist_data_no_copy)/12)*12
	minhistprimary = math.floor(min(hist_data_no_copy)/12)*12
	n, bins, patches = P.hist(hist_data_no_copy,bins = np.arange(-600,601,12) ,histtype = 'stepfilled')
	sku = skew(hist_data_no_copy)
	kurt = kurtosis(hist_data_no_copy)
	standerr = np.std(hist_data_no_copy)
	avg = np.mean(hist_data_no_copy)
	final = []
	final.append('GOES and 131 Histogram data: n,bins,skew,kurtosis,standard deviation')
	final.append(tuple(n))
	final.append(tuple(bins))
	final.append(sku)
	final.append(kurt)
	final.append(standerr)
	final.append(avg)
	P.setp(patches, 'facecolor','b','alpha',0.75)
	P.xlabel('Time Difference between GOES and 131 peak in seconds')
	P.ylabel('Number of Peaks')
	P.title('Histogram of GOES 1-8 $\AA$ and AIA 131 $\AA$ Separations')
	P.text(.85,.9,'skew = ' + str(round(sku,3)),fontsize =12, ha='center',va='center',transform = ax.transAxes)
	P.text(.85,.8,'kurtosis = ' + str(round(kurt,3)),fontsize =12, ha='center',va='center',transform = ax.transAxes)
	P.text(.85,.7,'sigma = ' + str(round(standerr,3)),fontsize = 12, ha = 'center',va = 'center', transform = ax.transAxes)
	P.text(.85,.6,'mean = ' + str(round(avg,3)),fontsize = 12, ha = 'center', va = 'center', transform = ax.transAxes)
	P.savefig('/Volumes/Scratch/Users/dherman/sundata/sun_plots/' + savename + '_131_goes_hist.ps')
	hist_data_file1 = open(savepathmeta + savename + '_131_goes_hist_data.txt','w')
	hist_data_file2 = open(savepathmeta + savename + '_131_goes_hist_metadata.txt','w')
	hist_data_file1.write(str(end_hist_data_no_copy))
	hist_data_file2.write(str(final))
	hist_data_file1.close()
	hist_data_file2.close()
	goes_A = [j for j in goes_class_set if j[-1] < 10**(-7)]
	goes_B = [j for j in goes_class_set if j[-1] < 10**(-6) and j[-1] > 10**(-7)]
	goes_C = [j for j in goes_class_set if j[-1] < 10**(-5) and j[-1] > 10**(-6)]
	goes_M = [j for j in goes_class_set if j[-1] < 10**(-4) and j[-1] > 10**(-5)]
	goes_X = [j for j in goes_class_set if j[-1] < 10**(-3) and j[-1] > 10**(-4)]
	goes_C_low = [j for j in goes_class_set if j[-1] < 5*(10**(-6)) and j[-1] > 10**(-6)]
	goes_C_high = [j for j in goes_class_set if j[-1] < 10**(-5) and j[-1] > 5*(10**(-6))]
	goes_all = [goes_A,goes_B,goes_C,goes_M,goes_X,goes_C_low,goes_C_high]
	print len(goes_A)
	print len(goes_B)
	print len(goes_C)
	print len(goes_M)
	print len(goes_X)
	print 'lengths'
	xTickMarks = ['A','B','C','M','X','C 1.0-5.0','C 5.0-9.0']
	for idx,member in enumerate(goes_all):
		if len(member) > 0:
			goes_columns = zip(*member)
			f = P.figure()
			ax = f.add_subplot(111)
			maxhist = math.ceil(max(goes_columns[-2])/12)*12
			minhist = math.floor(min(goes_columns[-2])/12)*12
			n, bins, patches = P.hist(goes_columns[-2],bins = np.arange(-600,601,12) ,histtype = 'stepfilled')
			sku = skew(goes_columns[-2])
			kurt = kurtosis(goes_columns[-2])
			standerr = np.std(goes_columns[-2])
			avg = np.mean(goes_columns[-2])
			subfinal = []
			subfinal.append('GOES and 131 Histogram data: n,bins')
			subfinal.append(tuple(n))
			subfinal.append(tuple(bins))
			subfinal.append(sku)
			subfinal.append(kurt)
			subfinal.append(standerr)
			subfinal.append(avg)
			P.setp(patches, 'facecolor','b','alpha',0.75)
			P.xlabel('Time Difference between GOES and 131 peak in seconds')
			P.ylabel('Number of Peaks')
			ax.set_xlim(-600,600)
			ax.set_ylim(0,30)
			P.title('Histogram of class ' + xTickMarks[idx] + ' GOES 1-8 $\AA$ and AIA 131 $\AA$ Separations')
			P.text(.85,.9,'skew = ' + str(round(sku,3)),fontsize =12, ha='center',va='center',transform = ax.transAxes)
			P.text(.85,.8,'kurtosis = ' + str(round(kurt,3)),fontsize =12, ha='center',va='center',transform = ax.transAxes)
			P.text(.85,.7,'sigma = ' + str(round(standerr,3)),fontsize = 12, ha = 'center',va = 'center', transform = ax.transAxes)
			P.text(.85,.6,'mean = ' + str(round(avg,3)),fontsize = 12, ha = 'center', va = 'center', transform = ax.transAxes)
			P.savefig('/Volumes/Scratch/Users/dherman/sundata/sun_plots/' + savename + '_131_goes_' + xTickMarks[idx] + '_hist.ps')
			hist_data_file_a = open(savepathmeta + savename + '_131_goes_' + xTickMarks[idx] + '_hist_data.txt','w')
			hist_data_file_b = open(savepathmeta + savename + '_131_goes_' + xTickMarks[idx] + '_hist_metadata.txt','w')
			hist_data_file_a.write(str(goes_columns))
			hist_data_file_b.write(str(subfinal))
			hist_data_file_a.close()
			hist_data_file_b.close()
	goes_num = [len(goes_A),len(goes_B),len(goes_C),len(goes_M),len(goes_X)]
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ind = np.arange(len(goes_num))
	width = .7
	rects1 = ax.bar(ind, goes_num, width,color='black')
	ax.set_xlim(-width,len(ind)+width)
	ax.set_ylim(0,250)
	ax.set_ylabel('Number of Events')
	ax.set_title('Distribution of GOES Events by Class')
	ax.set_xticks(ind+width)
	xtickNames = ax.set_xticklabels(xTickMarks)
	plt.setp(xtickNames, rotation=45, fontsize=20)
	plt.savefig('/Volumes/Scratch/Users/dherman/sundata/sun_plots/' + savename + '_131_goes_class_hist.ps')
	hist_data_file3 = open(savepathmeta + savename + '_131_goes_class_hist_data.txt','w')
	final_two = [tuple(goes_num),tuple(xTickMarks)]
	hist_data_file3.write(str(final_two))
	return [end_hist_data_no_copy,final,final_two]							
