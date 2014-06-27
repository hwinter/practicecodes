import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import dih_sunplot as times
import dih_suncurve as values
import dih_sundate as date
import dih_sunchannel as channel
import dih_dir_finder as finder
#
#Name:dih_lightcurvedata
#
#Purpose:gets lightcurve data given AIA files in a directory
#
#Inputs:directory (dirname) with files, savename for plot
#
#Outputs:plot saved as savename
#
#Example: data = dih_lightcurvedata('../aiadata')
#
#Written:6/25/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_lightcurvedata(dirname):
	fitslist = finder.dih_dir_finder(dirname)
	lightcurvelist = []
	for dirpath in fitslist:
		x = times.dih_sunplot_times(dirpath)#retrieves times
		y = values.dih_suncurve(dirpath)#retrieves fluxes
		app = zip(x,y)
		lightcurvelist.append(app)
	return lightcurvelist