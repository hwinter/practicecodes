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
    	inlist = zip(*dih_lightcurvedata(dirpath))
    	plotlist = [list(row) for row in inlist]
    	colors = iter(cm.rainbow(np.linspace(0,1,len(plotlist)))) #creates color table
    	x = plotlist[0] #x coordinate data
    	innerdatalist.append(x)
    	y = plotlist[1] #y coordinate data
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
    		window = 7
    	elif channel.dih_sunchannel(dirpath) == 131:
    		ysmooth = dih_boxavg_recurs(yspikeless,23,3)
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



def dih_plotter4(dirname,savename,kaiser,boxcar,both):
    fitslist = finder.dih_dir_finder(dirname)
    print fitslist
    outerdatalist = []
    for idx,dirpath in enumerate(fitslist):
    	print "processing "+str(idx)
    	innerdatalist = []
    	inlist = zip(*dih_lightcurvedata(dirpath))
    	plotlist = [list(row) for row in inlist]
    	colors = iter(cm.rainbow(np.linspace(0,1,len(plotlist)))) #creates color table
    	x = plotlist[0] #x coordinate data
    	innerdatalist.append(x)
    	y = plotlist[1] #y coordinate data
    	innerdatalist.append(y)
    	#save each lightcurve's raw data into separate txt file
    	with open(savename+str(idx)+'.txt','wb') as fff:
    		pickle.dump(innerdatalist,fff)
    	print innerdatalist
    	outerdatalist.append(innerdatalist)#rough data to be sent to pickle dump
    	if kaiser == 1:
    		ysmooth = dih_smooth(y,14,7)#kaiser smoothing
    	if boxcar == 1:
    		ysmooth = d.dih_boxcar_recurs(y,21)#boxcar smoothing
    	if both == 1:
    		ysmooth = dih_boxcar(dih_smooth(y,14),21)
    	ycopy = ysmooth
    	yspikeless = spike2.dih_spike_picker2(ysmooth)
    	peaklist =signal.find_peaks_cwt(yspikeless, np.arange(2,14))
    	print peaklist
    	crestlist = []
    	cresttimelist = []
    	for member in peaklist:
    		crestlist.append(yspikeless[member])
    		cresttimelist.append(x[member])
    	crestlist = np.array(crestlist)
    	uberlist = argrelextrema(crestlist, np.greater)
    	plt.figure()
    	plt.plot(x,ysmooth,color = next(colors))
    	for member in uberlist[0]:
    		plt.plot(cresttimelist[member],crestlist[member],'gD')#places markers on peaks
    	peak = max(yspikeless)
    	peaklist2 = [i for i, j in enumerate(yspikeless) if j == peak]#places markers on absolute peaks
    	for num in peaklist2:
    		plt.plot(x[num],yspikeless[num],'rD',linewidth =1.5)
    		
#finish up plot characteristics
    	plt.plot(x,y,'b',linewidth = 1.0)
    	plt.title('Lightcurve at'+' '+date.dih_sunfirst(dirpath)+ ' '+ str(channel.dih_sunchannel(dirpath))+'$\AA$',y=1.07)
    	plt.xlabel('Seconds Since'+' '+date.dih_sunfirst(dirpath))
    	plt.ylabel('Arbitrary Flux Units')
    	plt.savefig(savename+str(idx)+'.ps')#saves postscript file
    with open(savename+'.txt','wb') as ff:
    	pickle.dump(outerdatalist,ff)
    
	return outerdatalist
