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
import dih_maxlistmaker as dmax
import dih_minlistmaker as dmin
from matplotlib.mlab import find


def dih_errmaker(dirname):
	indata = d.dih_tablereader(dirname)
	endlist =[]
	for member in indata:
		y = member[1]
		diff = abs(max(y)-min(y))
		if diff > .8:
			err = 6.3/7
		else:
			err = 6.3/3
	endlist.append(err)
	return endlist
		
		