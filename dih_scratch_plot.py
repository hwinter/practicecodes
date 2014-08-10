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
#
#
#
#
def getKey(item):
	return item[0]
#
#Name: dih_sun_scratch_plot
#
#Purpose: plot lightcurve for data that has already been run through sunpy map maker and moved to text files (sends files to scratch instead of george)
#
#Inputs:directory where ivo files were initially located, original savename for text files, number ivo file in dirname where desired text files came from, new savename (newname)
#
#Outputs: ps file for lightcurve plot, metadata about plot
#
#Example: gah = dih_sun_data_plot('/Volumes/Scratch/dherman/ivos','sunplots',18,'testplot')
#
#Written: 8/10/14 Dan Herman daniel.herman@cfa.harvard.edu
#
# 
def dih_sun_scratch_plot(dirname,savename,num,newname):
	directory_lists = finder.dih_dir_finder(dirname)#gets fits files and ivo files
	fits_list = directory_lists[0]
	ivo_list = directory_lists[1]
	datalist = pickle.load(open('/Volumes/Scratch/Users/dherman/sundata/rawdata' + savename + str(num) + '.txt','rb'))
	meta_datalist = pickle.load(open('/Volumes/Scratch/Users/dherman/sundata/metadata' + savename + '_meta' + str(num) + '.txt','rb'))
	fits_date = meta_datalist[0]#datetime for first fits file in dirpath
	fits_channel = meta_datalist[1]#channel for first fits
	fits_ev_peak = meta_datalist[10][0]
	fits_ev_peak = datetime.strptime(fits_ev_peak,'%Y-%m-%dT%H:%M:%S')
	print str(fits_channel)
	fits_center = meta_datalist[2]#center of first fits
	fits_box = meta_datalist[-4]
	colors = iter(cm.rainbow(np.linspace(0,1,len(datalist[0])))) #creates color table
	#x,y coordinate data sorting
	testsort = zip(*[datalist[0],datalist[1]])
	sorted_data = sorted(testsort, key=getKey)
	x = np.array(zip(*sorted_data)[0])
	y = np.array(zip(*sorted_data)[1])
	xcopy = x
	x = x - x[0]
	ycopy = y
	yspikeless = spike.dih_spike_picker(y)#removes ultra noisy peaks
	yspikeless = spike.dih_dip_picker(yspikeless)#removes ultra noisy dips
	#channel-selective smoothing
	if fits_channel == 131:
		ysmooth = box.dih_boxavg_recurs(yspikeless,11,2)
		window = 11
	elif fits_channel == 171:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)
		window = 7
	elif fits_channel == 211:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,3)
		window = 7
	elif fits_channel == 193:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)
		window = 7
	elif fits_channel == 304:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)	
		window = 7
	elif fits_channel == 335:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)
		window = 7
	elif fits_channel == 94:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)
		window = 7
	else:
		print "Bad Channel!"	
	fits_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
	fits_first = timedelta(seconds = xcopy[0])
	fits_last = timedelta(seconds = xcopy[-1])
	fits_begin = fits_time+fits_first
	fits_end = fits_time+fits_last
	fits_begin = datetime.strftime(fits_begin,'%Y-%m-%dT%H:%M:%S.%f')
	fits_end = datetime.strftime(fits_end,'%Y-%m-%dT%H:%M:%S.%f')
	peaklist = argrelextrema(ysmooth,np.greater)#relative max
	peak = max(ysmooth[(window-1)/2:len(ysmooth)-(window-1)/2])#absolute max ignoring the very ends of the data set
	maxpeaklist = [i for i, j in enumerate(ysmooth) if j == peak]
	plt.figure()
	relpeaktimelist = []
	for member in peaklist[0]:
		if member < window or member > (len(ysmooth)-window):
			continue
		else:
			plt.plot(x[member],ysmooth[member],'yD',markersize =8)
			#recreating peak times from time difference data
			first_time = datetime.strptime(fits_begin,'%Y-%m-%dT%H:%M:%S.%f')
			timediff = timedelta(seconds = x[member])
			peaktime = first_time+timediff
			relpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
			continue	
	maxpeaktimelist = []
	flagged_peaktimelist=[]
	for member in maxpeaklist:
		first_time = datetime.strptime(fits_begin,'%Y-%m-%dT%H:%M:%S.%f')
		timediff = timedelta(seconds = x[member])
		print 'timediff'
		print timediff
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
	metadatalist.append(fits_begin)
	metadatalist.append(fits_channel)
	metadatalist.append(fits_center)
	metadatalist.append(relpeaktimelist)
	if len(maxpeaktimelist) == 1:
		max_peak_dt = datetime.strptime(maxpeaktimelist[0],'%Y/%m/%d %H:%M:%S.%f')
		peakdiff = fits_ev_peak-max_peak_dt
		peakdiff = peakdiff.total_seconds()
		if abs(peakdiff) < 900:
			metadatalist.append(maxpeaktimelist)
		else:
			metadatalist.append([])
	else:
		metadatalist.append([])	
	metadatalist.append(ivo_list[num])
	metadatalist.append(flagged_peaktimelist)
	smooth_range = max(ysmooth)-min(ysmooth)
	#consider raising .75 to .9
	if smooth_range > max(ysmooth)*1.0:
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
	metadatalist.append(fits_box)
	metadatalist.append(list(x))
	metadatalist.append(list(ysmooth))
	metadatalist.append(fits_date)
	metadatalist.append(fits_end)	
	#pickling of metadata
	#with open(savename+'_'+newname+'_meta'+str(num)+'.txt','wb') as fff:
		#pickle.dump(metadatalist,fff)
	#shutil.move(savename+'_'+newname+'_meta'+str(num)+'.txt','/data/george/dherman/metadata')
	#with open(savename+'_'+newname+'_chi'+str(num)+'.txt','wb') as fff:
		#pickle.dump(chi,fff)
	#shutil.move(savename+'_'+newname+'_chi'+str(num)+'.txt','/data/george/dherman/metadata')
	#Saving all relavant metadata/peakdata to human readable text file
	#file = open(savename+'_human_'+newname+'_meta'+str(num)+'.txt','wb')
	#simplejson.dump(metadatalist,file)
	#file.close()
	#shutil.move(savename+'_human_'+newname+'_meta'+str(num)+'.txt','/data/george/dherman/metadata')
	#finish up plot characteristics
	plt.plot(x,y,'b',linewidth = 1.0)
	plt.plot(x,ysmooth,'r',linewidth = 1.5)
	plt.title('Lightcurve at'+' '+fits_begin+ ' '+ str(fits_channel)+'$\AA$',y=1.07)
	plt.xlabel('Seconds Since'+' '+fits_begin)
	plt.ylabel('Arbitrary Flux Units')
	plt.savefig('/Volumes/Scratch/Users/dherman/sundata/sun_plots/'+newname+'_'+fits_begin+'_'+savename+str(num)+'.ps')#saves postscript file
	return metadatalist








#
#
#Name: dih_sun_recurs_scratch_plot
#
#Purpose: Recurses over files in dirname and performs dih_sun_scratch_plot for each file
#
#Inputs: directory containing ivo files, original savename for files, new savename for files (newname), set test to be True to direct files to test directories
#
#Outputs: Postscript file for each ivo file, metadata about ps file
#
#Example: gah = dih_sun_recurs_data_plot('/Volumes/Scratch/Users/dherman/data','suncurves','test_for_smoothing')
#
#Written: 7/14/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_sun_recurs_scratch_plot(dirname,savename,newname,test):
	directory_lists = finder.dih_dir_finder(dirname)#gets fits files and ivo files
	fits_list = directory_lists[0]
	ivo_list = directory_lists[1]
	savepathmeta = '/Volumes/Scratch/Users/dherman/sundata/metadata/'
	savepathmeta_test = '/Volumes/Scratch/Users/dherman/sundata/metadata_test/'
	savepathraw = '/Volumes/Scratch/Users/dherman/sundata/rawdata/'
	#file_ivo = open('/data/george/dherman/completed/all_completed_ivolist.txt','a')
	print 'here'
	print ivo_list
	#for member in ivo_list:
		#file_ivo.write(member)
		#file_ivo.write('\n')
	#file_ivo.close()
	if test == 0:
		file2 = open(savepathmeta + savename + '_' + newname + '_human_meta_corrupted.txt','a')
		file3 = open(savepathmeta + savename + '_' + newname + '_all_human_meta.txt','a')
		file4 = open(savepathmeta + savename + '_' + newname + '_human_meta_131.txt','a')
		file5 = open(savepathmeta + savename + '_' + newname + '_human_meta_peakflag.txt','a')
	elif test == 1:
		file2 = open(savepathmeta_test + savename + '_' + newname + '_human_meta_corrupted.txt','a')
		file3 = open(savepathmeta_test + savename + '_' + newname + '_all_human_meta.txt','a')
		file4 = open(savepathmeta_test + savename + '_' + newname + '_human_meta_131.txt','a')
		file5 = open(savepathmeta_test + savename + '_' + newname + '_human_meta_peakflag.txt','a')
	else:
		print "Bad Test Keyword!" 
	list = range(len(ivo_list))
	all_meta = []
	for num in list:
		if os.path.isfile('/Volumes/Scratch/Users/dherman/sundata/rawdata' + savename+str(num)+'.txt') == False or os.path.isfile('/Volumes/Scratch/Users/dherman/sundata/metadata' + savename+'_meta'+str(num)+'.txt') == False:
			continue
		else:
			metadatalist = dih_sun_scratch_plot(dirname,savename,num,newname)
			all_meta.append(metadatalist)
			continue
	for member in all_meta:
		#simplejson.dump(member,file3)
		file3.write(str(member))
		file3.write('\n')
		if member[1] == 131:
			#simplejson.dump(member,file4)
			file4.write(str(member))
			file4.write('\n')
		if member[7] == 'flag':
			#simplejson.dump(member,file2)
			file2.write(str(member))
			file2.write('\n')
		if member[8] == 'peakflag':
			#simplejson.dump(member,file5)
			file5.write(str(member))
			file5.write('\n')	
	file2.close()
	file3.close()
	file4.close()
	file5.close()
	return all_meta