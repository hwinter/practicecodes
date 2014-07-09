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
#Name:dih_uberplotter
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
#


def dih_sun_plotter(dirname,savename):
    directory_lists = finder.dih_dir_finder(dirname)#gets fits files and ivo files
    fits_list = directory_lists[0]
    ivo_list = directory_lists[1]
    outerdatalist = []
    print fits_list
    for idx,dirpath in enumerate(fits_list):
    	print "processing "+str(idx)
    	innerdatalist = []
    	inlist = datum.dih_sunplot_data(dirpath)#gets data and metadata
    	if inlist == 11 or len(inlist[0]) < 50:#handling corrupt data cases
    		msg = ['none']
    		outerdatalist.append(msg)
    		continue
    	print len(inlist)
    	print type(inlist)
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
    	outerdatalist.append(innerdatalist)
    	#save each lightcurve's raw data into separate txt file
    	with open(savename+str(idx)+'.txt','wb') as fff:
    		pickle.dump(innerdatalist,fff)
    	#human readable save format
    	np.savetxt(fits_date+'_'+savename+'_col'+str(idx)+'.txt',np.column_stack((x,y)),header = 'x=time,y=flux data from '+fits_date+' for channel '+str(fits_channel)+' created on '+time.strftime("%c"),footer = str(ivo_list[idx]))
    	yspikeless = spike.dih_spike_picker(y)#removes ultra noisy peaks
    	yspikeless = spike.dih_dip_picker(yspikeless)#removes ultra noisy dips
    	#channel-selective smoothing
    	print "at smoothing "+str(idx)
    	if fits_channel == 131:
    		ysmooth = box.dih_boxavg_recurs(yspikeless,11,11)
    		window = 11
    	elif fits_channel == 171:
    		ysmooth = box.dih_boxavg_recurs(yspikeless,7,9)
    		window = 7
    	elif fits_channel == 211:
    		ysmooth = box.dih_boxavg_recurs(yspikeless,7,9)
    		window = 7
    	elif fits_channel == 193:
    		ysmooth = box.dih_boxavg_recurs(yspikeless,7,7)
    		window = 7
    	elif fits_channel == 304:
    		ysmooth = box.dih_boxavg_recurs(yspikeless,7,7)
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
    	for member in maxpeaklist:
    		plt.plot(x[member],ysmooth[member],'rD')
    		first_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
    		timediff = timedelta(seconds = x[member])
    		peaktime = first_time+timediff
    		maxpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
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
    	#pickling of metadata
    	with open(savename+'_meta'+str(idx)+'.txt','wb') as fff:
    		pickle.dump(metadatalist,fff)
    	with open(savename+'_chi'+str(idx)+'.txt','wb') as fff:
    		pickle.dump(chi,fff)
    	#Saving all relavant metadata/peakdata to human readable text file
    	file = open(savename+'_human_meta'+str(idx)+'.txt','wb')
    	simplejson.dump(metadatalist,file)
    	file.close()
    	#finish up plot characteristics
    	plt.plot(x,y,'b',linewidth = 1.0)
    	plt.plot(x,ysmooth,'r',linewidth = 1.5)
    	plt.title('Lightcurve at'+' '+fits_date+ ' '+ str(fits_channel)+'$\AA$',y=1.07)
    	plt.xlabel('Seconds Since'+' '+fits_date)
    	plt.ylabel('Arbitrary Flux Units')
    	plt.savefig(fits_date+'_'+savename+str(idx)+'.ps')#saves postscript file
    	continue
    
	return outerdatalist


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
#
def dih_sun_data_plot(savename,idx,newname):
	datalist = pickle.load(open(savename+str(idx)+'.txt','rb'))
	meta_datalist = pickle.load(open(savename+'_meta'+str(idx)+'.txt','rb'))
	fits_date = meta_datalist[0]#datetime for first fits file in dirpath
	fits_channel = meta_datalist[1]#channel for first fits
	print str(fits_channel)
	fits_center = meta_datalist[2]#center of first fits
	colors = iter(cm.rainbow(np.linspace(0,1,len(datalist[0])))) #creates color table
	x = datalist[0] #x coordinate data
	y = datalist[0] #y coordinate data
	yspikeless = spike.dih_spike_picker(y)#removes ultra noisy peaks
	yspikeless = spike.dih_dip_picker(yspikeless)#removes ultra noisy dips
	#channel-selective smoothing
	if fits_channel == 131:
		ysmooth = d.dih_boxcar_recurs(yspikeless,11,11)
		window = 11
	elif fits_channel == 171:
		ysmooth = d.dih_boxcar_recurs(yspikeless,7,9)
		window = 7
	elif fits_channel == 211:
		ysmooth = d.dih_boxcar_recurs(yspikeless,7,9)
		window = 7
	elif fits_channel == 193:
		ysmooth = d.dih_boxcar_recurs(yspikeless,7,9)
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
			plt.plot(x[member],ysmooth[member],'yD')
			#recreating peak times from time difference data
			first_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
			timediff = timedelta(seconds = x[member])
			peaktime = first_time+timediff
			relpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
			continue	
	maxpeaktimelist = []
	for member in maxpeaklist:
		plt.plot(x[member],ysmooth[member],'rD')
		first_time = datetime.strptime(fits_date,'%Y-%m-%dT%H:%M:%S.%f')
		timediff = timedelta(seconds = x[member])
		peaktime = first_time+timediff
		maxpeaktimelist.append(peaktime.strftime('%Y/%m/%d %H:%M:%S.%f'))
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
	metadatalist.append(ivolist[idx])
	#pickling of metadata
	with open(savename+'_'+newname_+'_meta'+str(idx)+'.txt','wb') as fff:
		pickle.dump(metadatalist,fff)
	with open(savename+'_'+newname+'_chi'+str(idx)+'.txt','wb') as fff:
		pickle.dump(chi,fff)
	#Saving all relavant metadata/peakdata to human readable text file
	file = open(savename+'_human_'+newname+'_meta'+str(idx)+'.txt','wb')
	simplejson.dump(metadatalist,file)
	file.close()
	#finish up plot characteristics
	plt.plot(x,y,'b',linewidth = 1.0)
	plt.plot(x,ysmooth,'r',linewidth = 1.5)
	plt.title('Lightcurve at'+' '+fits_date+ ' '+ str(fits_channel)+'$\AA$',y=1.07)
	plt.xlabel('Seconds Since'+' '+fits_date)
	plt.ylabel('Arbitrary Flux Units')
	plt.savefig(newname+fits_date+'_'+savename+str(idx)+'.ps')#saves postscript file
	return [x,ycopy]

