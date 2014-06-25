import sunpy
import sunpy.map
import glob
import numpy as np
#Name:dih_suncurve
#
#Purpose: creates list of total flux in a series of AIA fits files
#
#Inputs:directory containing fits files (dirname)
#
#Outputs: list of total fluxes (curvelist)
#
#Example: dih_suncurve("../thataiadata")
#
#Written: 6/25/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#
def dih_suncurve(dirname):
	filelist = glob.glob(dirname+"/*.fits")
	curvelist = []
	for member in filelist:
		my_map = sunpy.map.Map(member)
		sigma = np.sum(my_map)
		curvelist.append(sigma)
	return curvelist
	