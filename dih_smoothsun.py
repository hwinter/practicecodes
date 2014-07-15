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
    ivos_file = open('/data/george/dherman/completed/all_completed_ivolist.txt','r')#gets already processed ivo files
    lines_ivo = ivos_file.readlines()
    for idx,dirpath in enumerate(fits_list):
    	print "processing "+str(idx)
    	ivo_index = ivo_list[idx].find('ivo')#find relavant section of string
    	ivo_string = ivo_list[idx][ivo_index:]
    	completion = [s for s in lines_ivo if ivo_string in s]#tests to see if we have worked on this ivo file before
    	if len(completion) > 0:
    		print "ivo already processed"
    		continue
    	innerdatalist = []
    	inlist = datum.dih_sunplot_data(dirpath)#gets data and metadata
    	if inlist == 11 or len(inlist[0]) < 50:#handling corrupt data cases
    		file_corr = open('all_corrupted_ivolist.txt','a')
    		simplejson.dump(ivo_list[idx],file_corr)
    		file_corr.write('\n')
    		file_corr.close()
    		file_ivo = open('all_completed_ivolist.txt','a')
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
    	with open(savename+str(idx)+'.txt','wb') as fff:
    		pickle.dump(innerdatalist,fff)
    	shutil.move(savename+str(idx)+'.txt','/data/george/dherman/rawdata')
    	#human readable save format
    	np.savetxt(fits_date+'_'+savename+'_col'+str(idx)+'.txt',np.column_stack((x,y)),header = 'x=time,y=flux data from '+fits_date+' for channel '+str(fits_channel)+' created on '+time.strftime("%c"),footer = str(ivo_list[idx]))
    	shutil.move(fits_date+'_'+savename+'_col'+str(idx)+'.txt','/data/george/dherman/rawdata')
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
    		ysmooth = box.dih_boxavg_recurs(yspikeless,7,2)
    		window = 7
    	elif fits_channel == 193:
    		ysmooth = box.dih_boxavg_recurs(yspikeless,7,1)
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
    		if x[member] > 250 and x[member] < x[-1]-250:
    			maxpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
    		else:
    			flagged_peaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
    	real_peaklist = [j for j, j in enumerate(maxpeaklist) if x[j] > 250 and x[j] < x[-1]-250]
    	flagged_peaklist = [j for j, j in enumerate(maxpeaklist) if x[j] < 250 or x[j] > x[-1]-250]
    	for member in real_peaklist:
    		plt.plot(x[member],ysmooth[member],'gD')
    	for member in flagged_peaklist:
    		plt.plot(x[member],ysmooth[member],'rD')
    	#creating chi-squared value
    	observed = np.array(ycopy)
    	expected = np.array(ysmooth)*np.sum(observed)
    	chi = chisquare(observed,expected)
    	metadatalist = []
    	metadatalist.append(fits_date)
    	metadatalist.append(fits_channel)
    	metadatalist.append(fits_center)
    	metadatalist.append(relpeaktimelist)
    	metadatalist.append(maxpeaktimelist)
    	metadatalist.append(ivo_list[idx])
    	metadatalist.append(flagged_peaktimelist)
    	smooth_range = max(ysmooth)-min(ysmooth)
    	if smooth_range > max(ysmooth)*.2:
    		metadatalist.append('flag')
    		file_corr = open('all_corrupted_ivolist.txt','a')
    		simplejson.dump(ivo_list[idx],file_corr)
    		file_corr.write('\n')
    		file_corr.close()
    	else:
    		metadatalist.append('clear')
    	if len(flagged_peaktimelist) > 0:
    		metadatalist.append('peakflag')
    		file_peakflag = open('all_peakflag_meta.txt','a')
    		simplejson.dump(metadatalist,file_peakflag)
    		file_peakflag.write('\n')
    		file_peakflag.close()
    	else:
    		metadatalist.append('no_peakflag')			
    	#pickling of metadata
    	#with open(savename+'_meta'+str(idx)+'.txt','wb') as fff:
    		#pickle.dump(metadatalist,fff)
    	#shutil.move(savename+'_meta'+str(idx)+'.txt','/data/george/dherman/metadata')
    	#with open(savename+'_chi'+str(idx)+'.txt','wb') as fff:
    		#pickle.dump(chi,fff)
    	#shutil.move(savename+'_chi'+str(idx)+'.txt','/data/george/dherman/metadata')
    	#Saving all relavant metadata/peakdata to human readable text file
    	file = open(savename+'_all_human_meta.txt','a')
    	simplejson.dump(metadatalist,file)
    	file.write('\n')
    	file.close()
    	#finish up plot characteristics
    	plt.plot(x,y,'b',linewidth = 1.0)
    	plt.plot(x,ysmooth,'r',linewidth = 1.5)
    	plt.title('Lightcurve at'+' '+fits_date+ ' '+ str(fits_channel)+'$\AA$',y=1.07)
    	plt.xlabel('Seconds Since'+' '+fits_date)
    	plt.ylabel('Arbitrary Flux Units')
    	plt.savefig(fits_date+'_'+savename+str(idx)+'.ps')#saves postscript file
    	shutil.move(fits_date+'_'+savename+str(idx)+'.ps','/data/george/dherman/sun_plots')
    	file_ivo = open('all_completed_ivolist.txt','a')
    	simplejson.dump(ivo_list[idx],file_ivo)
    	file_ivo.write('\n')
    	file_ivo.close()		
    if os.isfile('/home/dherman/Documents/togithub/'+savename+'_all_human_meta.txt'):
    	shutil.move(savename+'_all_human_meta.txt','/data/george/dherman/metadata')	
    if os.isfile('/home/dherman/Documents/togithub/'+'all_completed_ivolist.txt'):
    	shutil.move('all_completed_ivolist.txt','/data/george/dherman/completed')
    if os.isfile('/home/dherman/Documents/togithub/'+'all_corrupted_ivolist.txt'):
    	shutil.move('all_corrupted_ivolist.txt','/data/george/dherman/metadata')
    if os.isfile('/home/dherman/Documents/togithub/'+'all_peakflag_meta.txt'):
    	shutil.move('all_peakflag_meta.txt','/data/george/dherman/metadata')
    return ivo_list


#Name: dih_sun_mapper
#
#Purpose:create maps for fits files and extracts useful data
#
#
#
def dih_sun_mapper(dirname,savename):
	fitslist = finder.dih_dir_finder(dirname)
	totalrawdata = []
	for idx,dirpath in enumerate(fitslist):
		print "processing "+str(idx)
		inlist = zip(*dih_lightcurvedata(dirpath))
		plotlist = [list(row) for row in inlist]
		rawdata = plotlist
		np.savetxt(savename+'rawcol'+str(idx)+'.txt',np.column_stack((x,y)),header = 'x=time,y=flux data from '+date.dih_sunfirst(dirpath)+' for channel '+str(channel.dih_sunchannel(dirpath))+' created on '+time.strftime("%c"))
		totalrawdata.append(rawdata)
		np.savetxt(savename+'metacol'+str(idx)+'.txt',np.column_stack((date.dih_sunfirst(dirpath),channel.dih_sunchannel(dirpath),chi)),header = 'metadata for lightcurve generated on'+time.strftime("%c"))
	return totalrawdata
#
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
	datalist = pickle.load(open(savename+str(num)+'.txt','rb'))
	meta_datalist = pickle.load(open(savename+'_meta'+str(num)+'.txt','rb'))
	fits_date = meta_datalist[0]#datetime for first fits file in dirpath
	fits_channel = meta_datalist[1]#channel for first fits
	print str(fits_channel)
	fits_center = meta_datalist[2]#center of first fits
	colors = iter(cm.rainbow(np.linspace(0,1,len(datalist[0])))) #creates color table
	x = datalist[0] #x coordinate data
	y = datalist[1] #y coordinate data
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
	else:
		print "Bad Channel!"	
	peaklist = argrelextrema(ysmooth,np.greater)#relative max
	peak = max(ysmooth[(window-1)/2:len(ysmooth)-(window-1)/2])#absolute max ignoring the very ends of the data set
	maxpeaklist = [i for i, j in enumerate(ysmooth) if j == peak]
	plt.figure()
	relpeaktimelist = []
	for member in peaklist[0]:
		if member < window or member > (len(ysmooth)-window):
			continue
		else:
			plt.plot(x[member],ysmooth[member],'yD',markersize = 12)
			#recreating peak times from time difference data
			first_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
			timediff = timedelta(seconds = x[member])
			peaktime = first_time+timediff
			relpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
			continue	
	maxpeaktimelist = []
	flagged_peaktimelist=[]
	for member in maxpeaklist:
		first_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
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
		plt.plot(x[member],ysmooth[member],'gD',markersize = 12)
	for member in flagged_peaklist:
		plt.plot(x[member],ysmooth[member],'rD',markersize = 12)
	#creating chi-squared value
	observed = np.array(ycopy)
	expected = np.array(ysmooth)*np.sum(observed)
	chi = chisquare(observed,expected)
	metadatalist = []
	metadatalist.append(fits_date)
	metadatalist.append(fits_channel)
	metadatalist.append(fits_center)
	metadatalist.append(chi)
	metadatalist.append(relpeaktimelist)
	metadatalist.append(maxpeaktimelist)
	metadatalist.append(ivo_list[num])
	metadatalist.append(flagged_peaktimelist)
	smooth_range = max(ysmooth)-min(ysmooth)
	if smooth_range > max(ysmooth)*.2:
		metadatalist.append('flag')
	else:
		metadatalist.append('clear')
	#pickling of metadata
	#with open(savename+'_'+newname+'_meta'+str(num)+'.txt','wb') as fff:
		#pickle.dump(metadatalist,fff)
	#shutil.move(savename+'_'+newname+'_meta'+str(num)+'.txt','/data/george/dherman/metadata')
	#with open(savename+'_'+newname+'_chi'+str(num)+'.txt','wb') as fff:
		#pickle.dump(chi,fff)
	#shutil.move(savename+'_'+newname+'_chi'+str(num)+'.txt','/data/george/dherman/metadata')
	#Saving all relavant metadata/peakdata to human readable text file
	metadatalist.remove(chi)
	file = open(savename+'_human_'+newname+'_meta'+str(num)+'.txt','wb')
	simplejson.dump(metadatalist,file)
	file.close()
	shutil.move(savename+'_human_'+newname+'_meta'+str(num)+'.txt','/data/george/dherman/metadata')
	#finish up plot characteristics
	plt.plot(x,y,'b',linewidth = 1.0)
	plt.plot(x,ysmooth,'r',linewidth = 1.5)
	plt.title('Lightcurve at'+' '+fits_date+ ' '+ str(fits_channel)+'$\AA$',y=1.07)
	plt.xlabel('Seconds Since'+' '+fits_date)
	plt.ylabel('Arbitrary Flux Units')
	plt.savefig(newname+'_'+fits_date+'_'+savename+str(num)+'.ps')#saves postscript file
	shutil.move(newname+'_'+fits_date+'_'+savename+str(num)+'.ps','/data/george/dherman/sun_plots')
	return metadatalist
#
#Name: dih_sun_recurs_data_plots
#
#Purpose: Recurses over files in dirname and performs dih_sun_data_plot for each file
#
#Inputs: directory containing ivo files, original savename for files, new savename for files (newname)
#
#Outputs: Postscript file for each ivo file, metadata about ps file
#
#Example: gah = dih_sun_recurs_data_plot('/Volumes/Scratch/Users/dherman/data','suncurves','test_for_smoothing')
#
#Written: 7/14/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_sun_recurs_data_plot(dirname,savename,newname):
	directory_lists = finder.dih_dir_finder(dirname)#gets fits files and ivo files
	fits_list = directory_lists[0]
	ivo_list = directory_lists[1]
	#file_ivo = open('/data/george/dherman/completed/all_completed_ivolist.txt','a')
	print 'here'
	print ivo_list
	#for member in ivo_list:
		#file_ivo.write(member)
		#file_ivo.write('\n')
	#file_ivo.close()
	file2 = open(savename+'_'+newname+'_human_meta_flagged.txt','wb')
	file3 = open(savename+'_'+newname+'_all_human_meta.txt','wb')
	file4 = open(savename+'_'+newname+'_human_meta_304.txt','wb')
	list = range(len(ivo_list))
	all_meta = []
	for num in list:
		if os.path.isfile(savename+str(num)+'.txt') == False or os.path.isfile(savename+'_meta'+str(num)+'.txt') == False:
			continue
		else:
			metadatalist = dih_sun_data_plot(dirname,savename,num,newname)
			all_meta.append(metadatalist)
			continue
	for member in all_meta:
		simplejson.dump(member,file3)
		file3.write('\n')
		if member[1] == 304:
			simplejson.dump(member,file4)
			file4.write('\n')
		if member[7] == 'flag':
			simplejson.dump(member,file2)
			file2.write('\n')
	file2.close()
	file3.close()
	file4.close()
	shutil.move(savename+'_'+newname+'_human_meta_flagged.txt','/data/george/dherman/metadata')
	shutil.move(savename+'_'+newname+'_all_human_meta.txt','/data/george/dherman/metadata')
	shutil.move(savename+'_'+newname+'_human_meta_304.txt','/data/george/dherman/metadata')
	return all_meta
		

