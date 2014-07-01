import pickle
import dih_boxcar as d
import dih_spike_picker2 as dd
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from scipy.signal import argrelextrema
#
#
#Testing various signal processors on already created data

def dih_target_tester(filename,num2):
	list = pickle.load(open(filename+'.txt','rb'))
	print list
	target = list[1]
	print target
	domain = list[0]
	target = d.dih_boxcar_recurs(target,23,4)
	targetlist = []
	endrange = dd.dih_spike_picker2(target)
	targetlist.append(domain)
	targetlist.append(endrange)
	#peaklist =signal.find_peaks_cwt(endrange, np.arange(2,12))
	peaklist = argrelextrema(endrange,np.greater)
	#sinklist = argrelextrema(endrange,np.less)
	print peaklist
	#print sinklist 
	plt.figure()
	plt.plot(domain,endrange)
	plt.plot(domain,list[1])
	crestlist = []
	cresttimelist = []
	#cavelist = []
	#cavetimelist = []
	for member in peaklist[0]:
		crestlist.append(endrange[member])
		cresttimelist.append(domain[member])
		plt.plot(domain[member],endrange[member],'yD')
	#for member in sinklist[0]:
		#cavelist.append(endrange[member])
		#cavetimelist.append(domain[member])
	print crestlist
	#print cavelist
	crestlist = np.array(crestlist)
	#cavelist = np.array(cavelist)
	uberlist = argrelextrema(crestlist, np.greater)
	#suberlist = argrelextrema(cavelist,np.less)
	print 'peaks'
	print uberlist
	#print 'sinks'
	#print suberlist
	#for member in uberlist[0]:
		#plt.plot(cresttimelist[member],crestlist[member],'gD')#places markers on peaks
	plt.savefig('test'+str(num2)+'.ps')
	return targetlist