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
from dih_shared_plot import dih_shared_groups
import ast
from scipy.io.idl import readsav
import dih_fft_fcm as fcm
from dih_goes_csv_reader import dih_goes_csv_checker_event_files
from dih_create_goes_times import dih_create_goes_times
from dih_run_idl_script import dih_run_idl_goes_script
#
#Name: dih_sun_data_goes_plot
#
#Purpose: plot lightcurve and find peaks for GOES lightcurve data
#
# 
def dih_sun_data_goes_plot(datalist,start_time):
	colors = iter(cm.rainbow(np.linspace(0,1,len(datalist[0])))) #creates color table
	x = datalist[0] #x coordinate data
	y = datalist[1] #y coordinate data
	#time difference data
	x = time_info_list[1]
	ycopy = y
	ysmooth = box.dih_boxavg_recurs(y,3,1)
	window = 3	
	peaklist = argrelextrema(ysmooth,np.greater)#relative max
	peak = max(ysmooth[(window-1)/2:len(ysmooth)-(window-1)/2])#absolute max ignoring the very ends of the data set
	maxpeaklist = [i for i, j in enumerate(ysmooth) if j == peak]
	plt.figure()
	relpeaktimelist = []
	for member in peaklist[0]:
		if member < window or member > (len(ysmooth)-window):
			continue
		else:
			plt.plot(x[member],ysmooth[member],'yD',markersize = 8)
			#recreating peak times from time difference data
			first_time = datetime.strptime(start_time,'%d-%m-%Y %H:%M:%S.%f)
			timediff = timedelta(seconds = x[member])
			peaktime = first_time+timediff
			relpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
			continue	
	maxpeaktimelist = []
	flagged_peaktimelist=[]
	for member in maxpeaklist:
		first_time = datetime.strptime(start_time, '%d-%m-%Y %H:%M:%S.%f)
		timediff = timedelta(seconds = x[member])
		peaktime = first_time+timediff
		if x[member] > 250 and x[member] < x[-1]-250:
			maxpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
		else:
			flagged_peaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
	real_peaklist = [j for j, j in enumerate(maxpeaklist) if x[j] > 250 and x[j] < x[-1]-250]
	print maxpeaklist
	print real_peaklist
	flagged_peaklist = [j for j, j in enumerate(maxpeaklist) if x[j] < 250 or x[j] > x[-1]-250]
	print flagged_peaklist
	for member in real_peaklist:
		plt.plot(x[member],ysmooth[member],'gD',markersize = 8)
	for member in flagged_peaklist:
		plt.plot(x[member],ysmooth[member],'rD',markersize = 8)
	#creating chi-squared value
	observed = np.array(ycopy)
	expected = np.array(ysmooth)*np.sum(observed)
	chi = chisquare(observed,expected)
	metadatalist = []
	metadatalist.append(start_time)
	metadatalist.append('GOES 1-8 Angstroms')
	metadatalist.append('Full sun Goes image')
	metadatalist.append(relpeaktimelist)
	metadatalist.append(maxpeaktimelist)
	metadatalist.append(ivo_list[num])
	metadatalist.append(flagged_peaktimelist)
	smooth_range = max(ysmooth)-min(ysmooth)
	if smooth_range > max(ysmooth)*.2:
		metadatalist.append('flag')
	else:
		metadatalist.append('clear')
	if len(flagged_peaktimelist) > 0:
		metadatalist.append('peakflag')
		#file_peakflag = open('/data/george/dherman/metadata/' + 'all_peakflag_meta.txt','a')
		#simplejson.dump(metadatalist,file_peakflag)
		#file_peakflag.write('\n')
		#file_peakflag.close()
	else:
		metadatalist.append('no_peakflag')
	fits_time = datetime.strptime(start_time,'%d-%m-%Y %H:%M:%S.%f)
	fits_range = timedelta(seconds = x[-1])
	fits_end = fits_time+fits_range
	fits_end = datetime.strftime(fits_end,'%Y-%m-%dT%H:%M:%S.%f')
	metadatalist.append(fits_end)	
	plt.plot(x,y,'b',linewidth = 1.0)
	plt.plot(x,ysmooth,'r',linewidth = 1.5)
	plt.title('Lightcurve at' + ' ' + start_time + ' GOES 1-8 $\AA$',y=1.07)
	plt.xlabel('Seconds Since' + ' ' + fits_date)
	plt.ylabel('Arbitrary Flux Units')
	plt.savefig('/data/george/dherman/sun_plots/' + newname + '_' + start_time + '_' + savename + str(num) + '.ps')#saves postscript file
	return metadatalist
#
#
#
#
#
#
#
#
def dih_sun_recurs_goes_plot(131_file,savename):
	data_file = open(131_file,'r')
	meta_lines = data_files.readlines()
	uber_goes_metadatalist = []
	for member in meta_lines:
		member = ast.literal_eval(member)
		start_time = datetime.strptime(member[0],'%Y-%m-%dT%H:%M:%S.%f')
		end_time = datetime.strptime(member[-1],'%Y-%m-%dT%H:%M:%S.%f')
		month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
		start_month = month_list[start_time.month - 1]
		end_month = month_list[end_time.month - 1]
		start_string = datetime.strftime(start_time,'%d-'+start_month+'-%Y %H:%M:%S.%f')
		end_string = datetime.strftime(end_time,'%d-'+end_month+'-%Y %H:%M:%S.%f')
		columns = dih_run_idl_goes_script(start_string,end_string,savename + '_goes_curve_' + start_string + '.txt')
		with open(savename + '_goes_curve_' + start_string + '.txt','r') as f:
			first_line = [f.readline()]
			real_first_time = dih_create_goes_times(first_line)[0]
		metadatalist = dih_sun_data_goes_plot(columns,real_first_time)
		meta_file = open('/data/george/dherman/metadata/' + savename + '_all_human_meta_131_goes.txt','a')
		simplejson.dump([member,metadatalist],meta_file)
		meta_file.write('\n')
		meta_file.close()
		uber_goes_metadatalist.append(metadatalist)
	return uber_goes_metadatalist
		
		
		
		
		