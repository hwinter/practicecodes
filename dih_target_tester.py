import pickle
import dih_boxcar as d
import dih_smoothsun as ddd
import dih_spike_picker as dd
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from scipy.signal import argrelextrema
from dih_boxavg import dih_boxavg_recurs
#
#
#Testing various signal processors on already created data

def dih_target_tester(filename,num1,num2):
	list = pickle.load(open(filename+'.txt','rb'))
	target = list[num1][1]
	domain = list[num1][0]
	target = dd.dih_spike_picker(target)
	target = dd.dih_dip_picker(target)
	window = 7
	endrange = dih_boxavg_recurs(target,window,9)
	targetlist = []
	targetlist.append(domain)
	targetlist.append(endrange)
	#peaklist =signal.find_peaks_cwt(endrange, np.arange(2,12))
	peaklist = argrelextrema(endrange,np.greater)
	print peaklist 
	plt.figure()
	plt.plot(domain,endrange)
	plt.plot(domain,list[num1][1])
	crestlist = []
	cresttimelist = []
	extrapeaks = []
	for member in peaklist[0]:
		if member < window or member > (len(endrange)-window):
			extrapeaks.append(member)
			
			continue
		else:
			crestlist.append(endrange[member])
			cresttimelist.append(domain[member])
			plt.plot(domain[member],endrange[member],'yD')
			continue	
	print crestlist
	crestlist = np.array(crestlist)
	uberlist = argrelextrema(crestlist, np.greater)
	plt.savefig('test'+str(num2)+'.ps')
	return targetlist