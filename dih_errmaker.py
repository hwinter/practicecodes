#Name: dih_errmaker.py
#
#Purpose: makes rough estimate of error in peak time
#
#
import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab as P
import glob
import matplotlib.cm as cm
import dih_tableread as d



def dih_errmaker(dirname):
	indata = d.dih_tablereader(dirname)
	endlist =[]
	for member in indata:
		y = member[1]
		diff = abs(max(y)-min(y))
		if diff > 2.0:
			err = 6.3/11
		elif diff < 1.0:
			err = 6.3/5
		else:
			err = 6.3/9
		endlist.append(err)
	return endlist
		
		