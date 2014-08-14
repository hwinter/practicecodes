import pickle
import dih_boxcar as d
import dih_spike_picker as dd
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
from scipy.signal import argrelextrema
from dih_boxavg import dih_boxavg_recurs
from scipy.stats import chisquare
#
#
#Testing various signal processors on already created data

def dih_target_tester(filename,num1,num2):
	list = pickle.load(open(filename+'.txt','rb'))
	target = list[num1][1]
	domain = list[num1][0]
	target = dd.dih_spike_picker(target)
	target = dd.dih_dip_picker(target)
	window = 11
	recursions = 11
	endrange = dih_boxavg_recurs(target,window,recursions)
	targetlist = []
	targetlist.append(domain)
	targetlist.append(endrange)
	peak = max(endrange[(window-1)/2:len(target)-(window-1)/2])
	subpeaklist = [i for i, j in enumerate(endrange) if j== peak]
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
	for member in subpeaklist:
		plt.plot(domain[member],endrange[member],'rD')
	print crestlist
	observed = np.array(list[num1][1])
	expected = np.array(endrange)*np.sum(observed)
	chi = chisquare(observed,expected)
	plt.xlabel('Seconds since first data point')
	plt.ylabel('Arbitrary Flux Units')
	plt.title('Lightcurve for '+filename+str(num1)+' '+'chi = '+str(chi[0])+'\n r='+str(recursions)+' w='+str(window) ,y = 1.03)
	plt.savefig('test'+str(num2)+'.ps')
	return targetlist