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
def dih_lightcurvedata(name):
	x = times.dih_sunplot_times(name)#retrieves times
	y = values.dih_suncurve(name)#retrieves fluxes
	return zip(x,y)