import sunpy
import sunpy.map
import glob
import numpy as np


def dih_suncurve(dirname):
	filelist = glob.glob(dirname+"/*.fits")
	curvelist = []
	for member in filelist:
		my_map = sunpy.map.Map(member)
		sigma = np.sum(my_map)
		curvelist.append(sigma)
	return curvelist
	