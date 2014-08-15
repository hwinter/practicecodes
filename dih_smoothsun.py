#Name: dih_smoothsun
#

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

## Key for sorting
def getKey(item):
	return item[0]
#see dih_smoothie for documentation for dih_smooth module
def dih_smooth(x,beta,num1):
    """ kaiser window smoothing """
    window_len=num1
    halflen=(window_len-1)/2
    # extending the data at beginning and at the end
    # to apply the window at the borders
    s = np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    w = np.kaiser(window_len,beta)#creates kaiser window
    y = np.convolve(w/w.sum(),s,mode='valid')#convolve normalized window with data
    return y[halflen:len(y)-halflen]
#
#
#Name:dih_smooth_recurs
#
#Purpose:complete a number of kaiser convolution by recursion 
def dih_kaiser_recurs(x,beta,num1,rounds):
	counter = rounds
	out = x
	while counter > 0:
		print 'smoothing on '+str(counter)
		out = dih_smooth(out,beta,num1)
		counter = counter-1
		continue
	return out
#
#Name:dih_uberplotter (old file ignore this)
#
#Purpose:smoothing/peak-finding/plotting program for AIA data
#
#Inputs: directory string, savename string, number of files to read from directory
#
#Keywords: kaiser = true -gives kaiser smoothing, boxcar = true -gives boxcar smoothing
#both = true -gives both kaiser then boxcar
#
#Outputs: plot of smoothed data from dirname, returns raw data
#
#Example: gah = dih_plotter2('../data','savename.ps',10)
#
#Written:6/23/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_uberplotter(dirname,savename):
    fitslist = finder.dih_dir_finder(dirname)
    print fitslist
    for idx,dirpath in enumerate(fitslist):
    	print "processing "+str(idx)
    	innerdatalist = []
    	inlist = datum.dih_sunplot_data(dirpath)
    	colors = iter(cm.rainbow(np.linspace(0,1,len(plotlist)))) #creates color table
    	x = inlist[0] #x coordinate data
    	innerdatalist.append(x)
    	y = inlist[1] #y coordinate data
    	innerdatalist.append(y)
    	#save each lightcurve's raw data into separate txt file
    	with open(savename+str(idx)+'.txt','wb') as fff:#pickle dump for data for easy recapture with python
    		pickle.dump(innerdatalist,fff)
    	#also save the data into human-readable format for use with other programming languages
    	np.savetxt(savename+'col.txt',np.column_stack((x,y)),header = 'x=time,y=flux data from '+date.dih_sunfirst(dirpath)+' for channel '+str(channel.dih_sunchannel(dirpath))+' created on '+time.strftime("%c"))
    	yspikeless = spike.dih_spike_picker(y)
    	yspikeless = spike.dih_dip_picker(yspikeless)
    	if channel.dih_sunchannel(dirpath) == 171:
    		ysmooth = dih_boxavg_recurs(yspikeless,7,9)#boxcar smoothing
    		window = 7
    	elif channel.dih_sunchannel(dirpath) == 211:
    		ysmooth	= dih_boxavg_recurs(yspikeless,7,9)
    		window = 23
    	else:
    		print 'Not a valid channel!'
    	diplist = argrelextrema(ysmooth[window:len(y)-window],np.less)
    	peaklist = argrelextrema(ysmooth[window:len(y)-window], np.greater)
    	x_short = x[window:len(y)-window]
    	y_short = y[window:len(y)-window]
    	sub_y_list = np.split(y_short,diplist[0])
    	sub_x_list = np.split(x_short,diplist[0])
    	plt.figure()
    	plt.plot(x,ysmooth,color = next(colors))
    	for idx,member in enumerate(sub_y_list):
    		member = spike.dih_spike_picker(member)
    		subpeak = max(member)
    		subpeaklist = [i for i, j in enumerate(member) if j== subpeak]
    		for num in subpeaklist:
    			plt.plot(sub_x_list[idx][num],member[num],'rD')
    	
    	#for num in peaklist[0]:
    		#plt.plot(x[num],ysmooth[num],'gD')#places markers on peaks
    	#peak = max(yspikeless)
    	#peaklist2 = [i for i, j in enumerate(yspikeless) if j == peak]#places markers on absolute peaks
    	#for num in peaklist2:
    		#plt.plot(x[num],ysmooth[num],'rD',linewidth =1.5)
    		
#finish up plot characteristics
    	plt.plot(x,y,'b',linewidth = 1.0)
    	plt.title('Lightcurve at'+' '+date.dih_sunfirst(dirpath)+ ' '+ str(channel.dih_sunchannel(dirpath))+'$\AA$',y=1.07)
    	plt.xlabel('Seconds Since'+' '+date.dih_sunfirst(dirpath))
    	plt.ylabel('Arbitrary Flux Units')
    	plt.savefig(savename+str(idx)+'.ps')#saves postscript file
	return outerdatalist

#
#
#
#
#
#
#Name: dih_sun_plotter
#
#Purpose: implements specialized smoothing for each AIA data channel
#
#Inputs: Directory containing directories with fits files, savename string to be used for saving plots,raw data, metadata
#
#Outputs: Plots lightcurves and saves them, creates txt file (both human and nonhuman readable) for raw data and metadata
#
#Example: foo = dih_sun_plotter('/users/fitsfiles','woohooplot')
#
#Written: 7/8/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#Note: Form of metadata -> [Event Starting Time, Event Channel, Event Center, Relative Peaks, Primary Peak, Source Ivo File, Flagged Peaks, Corrupt: 'flag' (y) or 'clear' (n), Contains Flagged Peaks: 'peakflag' (y) or 'no_peakflag' (n)]


def dih_sun_plotter(dirname,savename):
    directory_lists = finder.dih_dir_finder(dirname)#gets fits files and ivo files
    fits_list = directory_lists[0]
    ivo_list = directory_lists[1]
    ivos_file = open('/data/george/dherman/map_completed/all_completed_ivolist.txt','r')#gets already processed ivo files
    lines_ivo = ivos_file.readlines()
    #cue_file = open(cuepath,'r')
    #cue_lines = cue_file.readlines()
    for idx,dirpath in enumerate(fits_list):
    	print "processing "+str(idx)
    	if idx < 44:
    		continue
    	member_fits = glob.glob(dirpath + '/*.fits')
    	if len(member_fits) < 100:
    		continue
    	ivo_index = ivo_list[idx].find('ivo')#find relavant section of string
    	ivo_string = ivo_list[idx][ivo_index:]
    	completion = [s for s in lines_ivo if ivo_string in s]#tests to see if we have worked on this ivo file before
    	if len(completion) > 0:
    		print "ivo already processed"
    		continue
    	#cue = [s for s in cue_lines if ivo_string in s]
    	#if len(cue) == 0:
    		#print "ivo not on cue list"
    		#continue
    	innerdatalist = []
    	inlist = datum.dih_sunplot_data(dirpath)#gets data and metadata
    	if inlist == 11 or len(inlist[0]) < 50:#handling corrupt data cases
    		file_corr = open('/data/george/dherman/metadata/all_corrupted_ivolist.txt','a')
    		simplejson.dump(ivo_list[idx],file_corr)
    		file_corr.write('\n')
    		file_corr.close()
    		file_ivo = open('/data/george/dherman/map_completed/all_completed_ivolist.txt','a')
    		simplejson.dump(ivo_list[idx],file_ivo)
    		file_ivo.write('\n')
    		file_ivo.close()
    		continue
    	fits_date = inlist[2]#datetime for first fits file in dirpath
    	fits_channel = inlist[3]#channel for first fits
    	print str(fits_channel)
    	fits_center = inlist[4]#center of first fits
    	colors = iter(cm.rainbow(np.linspace(0,1,len(inlist[0])))) #creates color table
    	x = inlist[1] #x coordinate data
    	innerdatalist.append(x)
    	y = inlist[0] #y coordinate data
    	ycopy = y
    	innerdatalist.append(y)
    	#save each lightcurve's raw data into separate txt file
    	with open('/data/george/dherman/rawdata/'+savename+str(idx)+'.txt','wb') as fff:
    		pickle.dump(innerdatalist,fff)
    	#human readable save format
    	np.savetxt('/data/george/dherman/rawdata/' + fits_date + '_' + savename + '_col' + str(idx) + '.txt',np.column_stack((x,y)),header = 'x=time,y=flux data from ' + fits_date + ' for channel ' + str(fits_channel) + ' created on ' + time.strftime("%c"),footer = str(ivo_list[idx]))
    	yspikeless = spike.dih_spike_picker(y)#removes ultra noisy peaks
    	yspikeless = spike.dih_dip_picker(yspikeless)#removes ultra noisy dips
    	#channel-selective smoothing
    	print "at smoothing "+str(idx)
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
    	else:
    		print "Bad Channel!"
    		continue	
    	peaklist = argrelextrema(ysmooth,np.greater)#relative max
    	peak = max(ysmooth[(window-1)/2:len(ysmooth)-(window-1)/2])#absolute max ignoring the very ends of the data set
    	maxpeaklist = [i for i, j in enumerate(ysmooth) if j == peak]
    	plt.figure()
    	relpeaktimelist = []
    	for member in peaklist[0]:
    		if member < window or member > (len(ysmooth)-window):
    			continue
    		else:
    			plt.plot(x[member],ysmooth[member],'yD')
    			#recreating peak times from time difference data
    			first_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
    			timediff = timedelta(seconds = x[member])
    			peaktime = first_time+timediff
    			relpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
    			continue	
    	maxpeaktimelist = []
    	flagged_peaktimelist = []
    	for member in maxpeaklist:
    		first_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
    		timediff = timedelta(seconds = x[member])
    		peaktime = first_time+timediff
    		if x[member] > 200 and x[member] < x[-1]-200:
    			maxpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
    		else:
    			flagged_peaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
    	real_peaklist = [j for j, j in enumerate(maxpeaklist) if x[j] > 250 and x[j] < x[-1]-250]
    	flagged_peaklist = [j for j, j in enumerate(maxpeaklist) if x[j] < 250 or x[j] > x[-1]-250]
    	for member in real_peaklist:
    		plt.plot(x[member],ysmooth[member],'gD')
    	for member in flagged_peaklist:
    		plt.plot(x[member],ysmooth[member],'rD')
    	metadatalist = []
    	metadatalist.append(fits_date)
    	metadatalist.append(fits_channel)
    	metadatalist.append(fits_center)
    	metadatalist.append(relpeaktimelist)
    	metadatalist.append(maxpeaktimelist)
    	metadatalist.append(ivo_list[idx])
    	metadatalist.append(flagged_peaktimelist)
    	smooth_range = max(ysmooth)-min(ysmooth)
    	if smooth_range > max(ysmooth)* 1.0:
    		metadatalist.append('flag')
    		file_corr = open('/data/george/dherman/metadata/' + 'all_corrupted_ivolist.txt','a')
    		simplejson.dump(ivo_list[idx],file_corr)
    		file_corr.write('\n')
    		file_corr.close()
    	else:
    		metadatalist.append('clear')
    	if len(flagged_peaktimelist) > 0:
    		metadatalist.append('peakflag')
    		file_peakflag = open('/data/george/dherman/metadata/' + 'all_peakflag_meta.txt','a')
    		simplejson.dump(metadatalist,file_peakflag)
    		file_peakflag.write('\n')
    		file_peakflag.close()
    	else:
    		metadatalist.append('no_peakflag')
    	fits_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
    	fits_range = timedelta(seconds = x[-1])
    	fits_end = fits_time+fits_range
    	fits_end = datetime.strftime(fits_end,'%Y-%m-%dT%H:%M:%S.%f')
    	metadatalist.append(fits_end)
    	#pickling of metadata
    	with open('/data/george/dherman/metadata/' + savename + '_meta' + str(idx) + '.txt','wb') as fff:
    		pickle.dump(metadatalist,fff)
    
    	#Saving all relavant metadata/peakdata to human readable text file
    	file = open('/data/george/dherman/metadata/' + savename + '_all_human_meta.txt','a')
    	simplejson.dump(metadatalist,file)
    	file.write('\n')
    	file.close()
    	#finish up plot characteristics
    	plt.plot(x,y,'b',linewidth = 1.0)
    	plt.plot(x,ysmooth,'r',linewidth = 1.5)
    	plt.title('Lightcurve at' + ' ' + fits_date +  ' ' + str(fits_channel) + '$\AA$',y=1.07)
    	plt.xlabel('Seconds Since' + ' ' + fits_date)
    	plt.ylabel('Arbitrary Flux Units')
    	plt.savefig('/data/george/dherman/sun_plots/' + fits_date + '_' + savename + str(idx) + '.ps')#saves postscript file
    	file_ivo = open('/data/george/dherman/map_completed/all_completed_no_sav_ivolist.txt','a')
    	simplejson.dump(ivo_list[idx],file_ivo)
    	file_ivo.write('\n')
    	file_ivo.close()		
    return ivo_list


#Name: dih_sun_mapper
#
#Purpose:create maps for fits files and extracts useful data
#
#
#
def dih_sun_mapper(dirname,savename):
    directory_lists = finder.dih_dir_finder(dirname)#gets fits files and ivo files
    fits_list = directory_lists[0]
    ivo_list = directory_lists[1]
    ivos_file = open('/data/george/dherman/map_completed/all_completed_ivolist.txt','r')#gets already processed ivo files
    lines_ivo = ivos_file.readlines()
    #cue_file = open(cuepath,'r')
    #cue_lines = cue_file.readlines()
    for idx,dirpath in enumerate(fits_list):
    	print "processing "+str(idx)
    	if idx < 44:
    		continue
    	member_fits = glob.glob(dirpath + '/*.fits')
    	if len(member_fits) < 100:
    		continue
    	ivo_index = ivo_list[idx].find('ivo')#find relavant section of string
    	ivo_string = ivo_list[idx][ivo_index:]
    	completion = [s for s in lines_ivo if ivo_string in s]#tests to see if we have worked on this ivo file before
    	if len(completion) > 0:
    		print "ivo already processed"
    		continue
    	#cue = [s for s in cue_lines if ivo_string in s]
    	#if len(cue) == 0:
    		#print "ivo not on cue list"
    		#continue
    	innerdatalist = []
    	inlist = datum.dih_sunplot_data(dirpath)#gets data and metadata
    	if inlist == 11 or len(inlist[0]) < 50:#handling corrupt data cases
    		file_corr = open('/data/george/dherman/metadata/all_corrupted_ivolist.txt','a')
    		simplejson.dump(ivo_list[idx],file_corr)
    		file_corr.write('\n')
    		file_corr.close()
    		file_ivo = open('/data/george/dherman/map_completed/all_completed_ivolist.txt','a')
    		simplejson.dump(ivo_list[idx],file_ivo)
    		file_ivo.write('\n')
    		file_ivo.close()
    		continue
    	fits_date = inlist[2]#datetime for first fits file in dirpath
    	fits_channel = inlist[3]#channel for first fits
    	print str(fits_channel)
    	fits_center = inlist[4]#center of first fits
    	metadatalist = []
    	metadatalist.append(fits_date)
    	metadatalist.append(fits_channel)
    	metadatalist.append(fits_center)
    	x = inlist[1] #x coordinate data
    	innerdatalist.append(x)
    	y = inlist[0] #y coordinate data
    	innerdatalist.append(y)
    	fits_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
    	fits_range = timedelta(seconds = x[-1])
    	fits_end = fits_time+fits_range
    	fits_end = datetime.strftime(fits_end,'%Y-%m-%dT%H:%M:%S.%f')
    	metadatalist.append(fits_end)
    	#pickling of metadata
    	with open('/data/george/dherman/metadata/' + savename + '_meta' + str(idx) + '.txt','wb') as fff:
    		pickle.dump(metadatalist,fff)
    
    	#Saving all relavant metadata/peakdata to human readable text file
    	file = open('/data/george/dherman/metadata/' + savename + '_all_human_meta.txt','a')
    	#save each lightcurve's raw data into separate txt file
    	with open('/data/george/dherman/rawdata/'+savename+str(idx)+'.txt','wb') as fff:
    		pickle.dump(innerdatalist,fff)
    	#human readable save format
    	np.savetxt('/data/george/dherman/rawdata/' + fits_date + '_' + savename + '_col' + str(idx) + '.txt',np.column_stack((x,y)),header = 'x=time,y=flux data from ' + fits_date + ' for channel ' + str(fits_channel) + ' created on ' + time.strftime("%c"),footer = str(ivo_list[idx]))
    	file_ivo = open('/data/george/dherman/map_completed/all_completed_no_sav_ivolist.txt','a')
    	simplejson.dump(ivo_list[idx],file_ivo)
    	file_ivo.write('\n')
    	file_ivo.close()
    return ivo_list	
#
#Name: dih_sun_data_plot
#
#Purpose: plot lightcurve for data that has already been run through sunpy map maker and moved to text files
#
#Inputs:directory where ivo files were initially located, original savename for text files, number ivo file in dirname where desired text files came from, new savename (newname)
#
#Outputs: ps file for lightcurve plot, metadata about plot
#
#Example: gah = dih_sun_data_plot('/Volumes/Scratch/dherman/ivos','sunplots',18,'testplot')
#
#Written: 7/14/14 Dan Herman daniel.herman@cfa.harvard.edu
#
# 
def dih_sun_data_plot(dirname,savename,num,newname):
	directory_lists = finder.dih_dir_finder(dirname)#gets fits files and ivo files
	fits_list = directory_lists[0]
	ivo_list = directory_lists[1]
	datalist = pickle.load(open('/data/george/dherman/rawdata/' + savename + str(num) + '.txt','rb'))
	meta_datalist = pickle.load(open('/data/george/dherman/metadata/' + savename + '_meta' + str(num) + '.txt','rb'))
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
	metadatalist.append(meta_datalist[5])
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
	plt.savefig('/data/george/dherman/sun_plots/'+newname+'_'+fits_begin+'_'+savename+str(num)+'.ps')#saves postscript file
	return metadatalist
#
#
#
#Name: dih_sun_recurs_data_plot
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
def dih_sun_recurs_data_plot(dirname,savename,newname,test):
	directory_lists = finder.dih_dir_finder(dirname)#gets fits files and ivo files
	fits_list = directory_lists[0]
	ivo_list = directory_lists[1]
	savepathmeta = '/data/george/dherman/metadata/'
	savepathmeta_test = '/data/george/dherman/metadata_test/'
	savepathraw = '/data/george/dherman/rawdata/'
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
	list = range(0,5000)
	all_meta = []
	for num in list:
		if os.path.isfile('/data/george/dherman/rawdata/' + savename+str(num)+'.txt') == False or os.path.isfile('/data/george/dherman/metadata/' + savename+'_meta'+str(num)+'.txt') == False:
			continue
		else:
			metadatalist = dih_sun_data_plot(dirname,savename,num,newname)
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

#
#
#
#Name: dih_sun_shared_plot
#
#Purpose: overplot events that occur near each other in time
#
#Inputs: file_string is a time string for a time to plot nearby events for, savename is the overarching uber string from dih_sun_plotter, newname is the attached savestring that comes from later dih_sun_recurs_data_plot, if test = 1 files are directed to test folders in george
#
#Outputs: shared plot postscripts
#
#Ex: gah = dih_sun_shared_plot('2012/04/04T12:00:00.00','uber','test',1')
#
#Written: 7/10/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
 		
def dih_sun_shared_plot(file_string,savename,newname,first_time,test):
	raw_files = list(set(os.listdir('/data/george/dherman/rawdata')))
	my_file = []
	for file in raw_files:
		if file_string in file:
			my_file.append(file)
	print 'blah'
	print my_file
	print type(my_file)		
	datalist = zip(*dih_filegrab('/data/george/dherman/rawdata/' + my_file[0]))
	if test == 1:
		meta_datalist_file = open('/data/george/dherman/metadata_test/' + savename+'_'+ newname +'_all_human_meta.txt','r')
	elif test == 0:
		meta_datalist_file = open('/data/george/dherman/metadata/' + savename+'_'+ newname +'_all_human_meta.txt','r')	
	meta_datalist_lines = meta_datalist_file.readlines()
	all_meta_datalist = []
	for member in meta_datalist_lines:
		print member
		try:
			member = ast.literal_eval(member)
			all_meta_datalist.append(member)
		except ValueError:
			continue
	for part in all_meta_datalist:
		if part[-2] == file_string:
			meta_datalist = part
	print meta_datalist						
	if meta_datalist[7] == 'flag':
		return meta_datalist
	fits_date = meta_datalist[0]#datetime for first fits file in dirpath
	uber_time = datetime.strptime(first_time,'%Y-%m-%dT%H:%M:%S.%f')
	fits_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
	diff = uber_time-fits_time
	diff_num = diff.total_seconds()
	fits_channel = meta_datalist[1]#channel for first fits
	print str(fits_channel)
	fits_center = meta_datalist[2]#center of first fits
	x = datalist[0] #x coordinate data
	y = datalist[1] #y coordinate data
	testsort = zip(*[x,y])
	sorted_data = sorted(testsort, key=getKey)
	x = np.array(zip(*sorted_data)[0])
	y = np.array(zip(*sorted_data)[1])
	x = x - x[0]
	ycopy = y
	y = list(y)
	yspikeless = spike.dih_spike_picker(y)#removes ultra noisy peaks
	yspikeless = spike.dih_dip_picker(yspikeless)#removes ultra noisy dips
	if fits_channel == 131:
		ysmooth = box.dih_boxavg_recurs(yspikeless,11,2)
		window = 11
		color = 'b'
	elif fits_channel == 171:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)
		window = 7
		color = 'y'
	elif fits_channel == 211:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,3)
		window = 7
		color = 'g'
	elif fits_channel == 193:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)
		window = 7
		color = 'm'
	elif fits_channel == 304:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)	
		window = 7
		color = 'k'
	elif fits_channel == 335:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)
		window = 7
		color = 'r'
	elif fits_channel == 94:
		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)
		window = 7
		color = 'c'
	else:
		print "Bad Channel!"	
	peaklist = argrelextrema(ysmooth,np.greater)#relative max
	peak = max(ysmooth[(window-1)/2:len(ysmooth)-(window-1)/2])#absolute max ignoring the very ends of the data set
	maxpeaklist = [i for i, j in enumerate(ysmooth) if j == peak]
	relpeaktimelist = []
	x = np.array(x) - diff_num
	x_peaklist = argrelextrema(np.array(x),np.greater)
	x_minlist = argrelextrema(np.array(x),np.less)
	#removes lightcurves whose times are not monotonic
	if len(x_peaklist[0])>0 or len(x_minlist[0]) >0:
		return meta_datalist
	for member in peaklist[0]:
		if member < window or member > (len(ysmooth)-window):
			continue
		else:
			plt.plot(x[member],ysmooth[member]/max(ysmooth),'yD',markersize = 8)
			continue	
	real_peaklist = [j for j, j in enumerate(maxpeaklist) if x[j] > 250 and x[j] < x[-1]-250]
	print maxpeaklist
	print real_peaklist
	flagged_peaklist = [j for j, j in enumerate(maxpeaklist) if x[j] < 250 or x[j] > x[-1]-250]
	print flagged_peaklist
	for member in real_peaklist:
		plt.plot(x[member],ysmooth[member]/max(ysmooth),'gD',markersize = 8)
	for member in flagged_peaklist:
		plt.plot(x[member],ysmooth[member]/max(ysmooth),'rD',markersize = 8)
	#finish up plot characteristics
	plt.plot(x,ysmooth/max(ysmooth),color = color,linewidth = 1.5,label = str(meta_datalist[1]))
	return meta_datalist

#
#
#Name: dih_sun_recurs_shared_plot
#
#
#Purpose: recurses over all the data in metadatafile and performs dih_sun_shared_plot
#
#Inputs: metadatafile created by dih_sun_recurs_data_plot, ubersavestring, newsavestring, test = 1 or 0
#
#Outputs: shared plots
#
#Example: gah = dih_sun_recurs_shared_plot('all_meta.txt','uber','test1',1)
#
#Written: 7/10/14 Dan Herman daniel.herman@cfa.harvard.edu
#
def dih_sun_recurs_shared_plot(metadatafile,savename,newname,test):
	shared_times = dih_shared_groups(metadatafile)
	print shared_times
	total_meta = []
	for idx,member in enumerate(shared_times):
		print "processing"+str(idx)
		fig = plt.figure()
		fig =fig.add_axes([0.1, 0.1, 0.6, 0.75])
		member_meta = []
		for guy in member:
			print 'first'
			print guy
			print 'here'
			guy_meta = dih_sun_shared_plot(guy,savename,newname,member[0],test)
			member_meta.append(guy_meta)
		plt.xlabel('Seconds Since'+' '+member[0])
		plt.ylabel('Normalized Flux Units')
		plt.title("Lightcurve at "+member[0]+" in all available channels",y=1.05)
		#plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=2, ncol= len(member), mode="expand", borderaxespad=0.)
		plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
		plt.savefig('/data/george/dherman/sun_plots/'+savename + '_' + newname+'_shared_plot_'+member[0]+'.ps')
		total_meta.append(member_meta)
	return total_meta
#
#
#Name: dih_sun_cropped_plotter
#
#Purpose: same as dih_sun_plotter but also focuses in on event bounding box portion of the sun and saves the bounding box information
#
#Inputs: dirname = directory containing ivo files, savename = uber string to tie all saved files together, cuelist = ivo files to run over or not run
#
#Outputs:rawdata,metadata on events
#
#Written: 8/1/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#

def dih_sun_cropped_plotter(dirname,savename,cuelist):
    directory_lists = finder.dih_dir_finder(dirname)#gets fits files and ivo files
    fits_list = directory_lists[0]
    ivo_list = directory_lists[1]
    savepathmeta = '/Volumes/Scratch/Users/dherman/sundata/metadata'
    savepathraw = '/Volumes/Scratch/Users/dherman/sundata/rawdata'
    ivos_file = open('/data/george/dherman/map_completed/all_completed2_ivolist.txt','r')#gets already processed ivo files
    lines_ivo = ivos_file.readlines()
    #if type(cuename) == str:
    	#cue_file = open(cuename,'r')
    	#cue_lines = cue_file.readlines()
    for idx,dirpath in enumerate(fits_list):
    	#set indexing 
    	if idx < 776 or idx == 2539 or idx == 1521:
    		continue
    	member_fits = glob.glob(dirpath + '/*.fits')
    	if len(member_fits) < 100 or len(member_fits) > 600:
    		continue
    	print "processing ivo "+str(idx)
    	ivo_index = ivo_list[idx].find('ivo')#find relavant section of string
    	ivo_string = ivo_list[idx][ivo_index:]
    	completion = [s for s in lines_ivo if ivo_string in s]#tests to see if we have worked on this ivo file before
    	if len(completion) > 0:
    		print "ivo already processed"
    		continue
    	if type(cuelist) == list:
    		cue = [s for s in cuelist if ivo_string in s]
    		if len(cue) > 0:
    			print "ivo on cue list"
    			continue
    	innerdatalist = []
    	#checking for existence of sav file with metadata
    	if os.path.isfile(ivo_list[idx]+'/'+ivo_string+'.sav') == False:
    		print 'no sav file' + ivo_list[idx]
    		no_sav_file = open(savepathmeta + savename + '_no_sav_file_ivos.txt','a')
    		no_sav_file.write(ivo_list[idx])
    		no_sav_file.write('\n')
    		no_sav_file.close()
    		continue
    	#get event file
    	ev = readsav(ivo_list[idx]+'/'+ivo_string+'.sav')
    	bounding_box = fcm.dih_get_event_bounding_box(ev)
    	ev_peak_time = fcm.dih_get_event_peak_time(ev)
    	goes_events = dih_goes_csv_checker_event_files(ev,'/home/dherman/Documents/all_event_2.csv')
    	inlist = datum.dih_sunplot_cropped_data(ev,dirpath,savename)#gets data and metadata
    	if inlist == 11 or len(inlist[0]) < 50:#handling corrupt data cases
    		file_corr = open(savepathmeta+'all_corrupted_ivolist.txt','a')
    		simplejson.dump(ivo_list[idx],file_corr)
    		file_corr.write('\n')
    		file_corr.close()
    		file_ivo = open('/home/dherman/Documents/all_completed2_ivolist.txt','a')
    		simplejson.dump(ivo_list[idx],file_ivo)
    		file_ivo.write('\n')
    		file_ivo.close()
    		continue
    	fits_date = inlist[2]#datetime for first fits file in dirpath
    	fits_channel = inlist[3]#channel for first fits
    	print str(fits_channel)
    	fits_center = inlist[4]#center of first fits
    	colors = iter(cm.rainbow(np.linspace(0,1,len(inlist[0])))) #creates color table
    	x = inlist[1] #x coordinate data
    	innerdatalist.append(x)
    	y = inlist[0] #y coordinate data
    	ycopy = y
    	innerdatalist.append(y)
    	#save each lightcurve's raw data into separate txt file
    	with open(savepathraw+savename+str(idx)+'.txt','wb') as fff:
    		pickle.dump(innerdatalist,fff)
    	#human readable save format
    	np.savetxt(savepathraw + fits_date + '_' + savename + '_col' + str(idx) + '.txt',np.column_stack((x,y)),header = 'x=time,y=flux data from ' + fits_date + ' for channel ' + str(fits_channel) + ' created on ' + time.strftime("%c"),footer = str(ivo_list[idx]))
    	yspikeless = spike.dih_spike_picker(y)#removes ultra noisy peaks
    	yspikeless = spike.dih_dip_picker(yspikeless)#removes ultra noisy dips
    	#channel-selective smoothing
    	print "at smoothing "+str(idx)
    	print str(fits_channel)
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
    		continue	
    	peaklist = argrelextrema(ysmooth,np.greater)#relative max
    	peak = max(ysmooth[(window-1)/2:len(ysmooth)-(window-1)/2])#absolute max ignoring the very ends of the data set
    	maxpeaklist = [i for i, j in enumerate(ysmooth) if j == peak]
    	plt.figure()
    	relpeaktimelist = []
    	for member in peaklist[0]:
    		if member < window or member > (len(ysmooth)-window):
    			continue
    		else:
    			plt.plot(x[member],ysmooth[member],'yD')
    			#recreating peak times from time difference data
    			first_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
    			timediff = timedelta(seconds = x[member])
    			peaktime = first_time+timediff
    			relpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
    			continue	
    	maxpeaktimelist = []
    	flagged_peaktimelist = []
    	for member in maxpeaklist:
    		first_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
    		timediff = timedelta(seconds = x[member])
    		peaktime = first_time+timediff
    		if x[member] > 200 and x[member] < x[-1]-200:
    			maxpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
    		else:
    			flagged_peaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
    	real_peaklist = [j for j, j in enumerate(maxpeaklist) if x[j] > 250 and x[j] < x[-1]-250]
    	flagged_peaklist = [j for j, j in enumerate(maxpeaklist) if x[j] < 250 or x[j] > x[-1]-250]
    	for member in real_peaklist:
    		plt.plot(x[member],ysmooth[member],'gD')
    	for member in flagged_peaklist:
    		plt.plot(x[member],ysmooth[member],'rD')
    	metadatalist = []
    	metadatalist.append(fits_date)
    	metadatalist.append(fits_channel)
    	metadatalist.append(fits_center)
    	metadatalist.append(relpeaktimelist)
    	metadatalist.append(maxpeaktimelist)
    	metadatalist.append(ivo_list[idx])
    	metadatalist.append(flagged_peaktimelist)
    	smooth_range = max(ysmooth)-min(ysmooth)
    	if smooth_range > max(ysmooth)*1.0:
    		metadatalist.append('flag')
    		file_corr = open(savepathmeta + 'all_corrupted_ivolist.txt','a')
    		simplejson.dump(ivo_list[idx],file_corr)
    		file_corr.write('\n')
    		file_corr.close()
    	else:
    		metadatalist.append('clear')
    	if len(flagged_peaktimelist) > 0:
    		metadatalist.append('peakflag')
    		file_peakflag = open(savepathmeta + 'all_peakflag_meta.txt','a')
    		simplejson.dump(metadatalist,file_peakflag)
    		file_peakflag.write('\n')
    		file_peakflag.close()
    	else:
    		metadatalist.append('no_peakflag')
    	metadatalist.append(bounding_box)
    	metadatalist.append(ev_peak_time)
    	metadatalist.append(goes_events)
    	fits_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
    	fits_range = timedelta(seconds = x[-1])
    	fits_end = fits_time+fits_range
    	fits_end_time = datetime.strftime(fits_end,'%Y-%m-%dT%H:%M:%S.%f')
    	metadatalist.append(fits_end_time)
    	#pickling of metadata
    	with open(savepathmeta + savename + '_meta' + str(idx) + '.txt','wb') as fff:
    		pickle.dump(metadatalist,fff)
    
    	#Saving all relavant metadata/peakdata to human readable text file
    	file = open(savepathmeta + savename + '_all_human_meta.txt','a')
    	simplejson.dump(metadatalist,file)
    	file.write('\n')
    	file.close()
    	#finish up plot characteristics
    	plt.plot(x,y,'b',linewidth = 1.0)
    	plt.plot(x,ysmooth,'r',linewidth = 1.5)
    	plt.title('Lightcurve at' + ' ' + fits_date +  ' ' + str(fits_channel) + '$\AA$',y=1.07)
    	plt.xlabel('Seconds Since' + ' ' + fits_date)
    	plt.ylabel('Arbitrary Flux Units')
    	plt.savefig('/Volumes/Scratch/Users/dherman/sundata/sun_plots/' + fits_date + '_' + savename + str(idx) + '.ps')#saves postscript file
    	file_ivo = open('/home/dherman/Documents/all_completed2_ivolist.txt','a')
    	simplejson.dump(ivo_list[idx],file_ivo)
    	file_ivo.write('\n')
    	file_ivo.close()		
    return ivo_list
#
#
#
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
	datalist = pickle.load(open('/data/george/dherman/rawdata/' + savename + str(num) + '.txt','rb'))
	meta_datalist = pickle.load(open('/data/george/dherman/metadata/' + savename + '_meta' + str(num) + '.txt','rb'))
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
		if os.path.isfile('/data/george/dherman/rawdata/' + savename+str(num)+'.txt') == False or os.path.isfile('/data/george/dherman/metadata/' + savename+'_meta'+str(num)+'.txt') == False:
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

		
		
		