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
	window = 5
	endrange = dih_boxavg_recurs(target,window,50)
	targetlist = []
	targetlist.append(domain)
	targetlist.append(endrange)
	diplist = argrelextrema(endrange[window:len(target)-window],np.less)
	print diplist
	peaklist = argrelextrema(endrange[window:len(target)-window], np.greater)
	x_short = domain[window:len(target)-window]
	y_short = target[window:len(target)-window]
	sub_y_list = np.split(y_short,diplist[0])
	sub_x_list = np.split(x_short,diplist[0])
	plt.figure()
	plt.plot(domain,target,color = 'b')
	plt.plot(domain,endrange,color = 'g')
	diff = max(target)-min(target)
	for idx,member in enumerate(sub_y_list):
		member = dd.dih_spike_picker3(member)
		subpeak = max(member)
		if (subpeak-min(target))>.1*diff:
			subpeaklist = [i for i, j in enumerate(member) if j== subpeak]
			for num in subpeaklist:
				plt.plot(sub_x_list[idx][num],member[num],'rD')
		else:
			print 'Bad Peak!'
	plt.xlabel('Seconds since first data point')
	plt.ylabel('Arbitrary Flux Units')
	plt.title('Lightcurve for '+filename+str(num1))
	plt.savefig('test'+str(num2)+'.ps')
	return targetlist