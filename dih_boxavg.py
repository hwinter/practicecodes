import numpy as np
#
#
#Name: dih_boxavg
#
#Purpose:performs running mean for prescribed width
#
#Inputs: Input 1d array, box width
#
#Outputs: smoothed array
#
#Example: smoothed_array = dih_boxavg(array,5)
#
#Written: 7/14/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#

def dih_boxavg(inarray,width):
	inarray = np.array(inarray)
	outarray = np.array(inarray)
	N = len(inarray)
	index1 = (width-1)/2
	index2 = (width+1)/2
	for idx,member in enumerate(inarray):
		if index1 <= idx and idx <= (N - index2):
			sumarray = inarray[idx-index1:idx+index2]
			outarray[idx] = np.sum(sumarray)/width
			continue
		else:
			outarray[idx] = inarray[idx]
			continue
	return outarray
		
#
#
#Name: dih_boxavg_recurs
#
#Purpose: recursive boxaveraging
#
#Inputs: inarray -> x, width -> num1, number of recursions -> rounds
#
#Outputs: output smooth array
#
#Example: smoothed = dih_boxavg_recurs(unsmoothed,7,2)
#
#Written: 7/14/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_boxavg_recurs(x,num1,rounds):
	counter = rounds
	out = x
	while counter > 0:
		print 'smoothing on '+str(counter)
		out = dih_boxavg(out,num1)
		counter = counter-1
		continue
	return out