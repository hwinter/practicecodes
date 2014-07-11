import sunpy
import sunpy.map
import glob
from sunpy.image.coalignment import mapcube_coalign_by_match_template
from datetime import datetime
import numpy as np
#
#Name:dih_sunplot_data
#
#Purpose:creates (time,flux) = (x,y) data, and also gives data,channel and center of first fits file in a given directory
#
#Inputs: directory with aia fits files (dirname)
#
#Outputs: list of:list of flux data points (curvelist), list of times since first AIA image in directory (diff list), time of first image, channel of first image 
#center of first image 
#
#Written: 7/8/14 Dan Herman	daniel.herman@cfa.harvard.edu
#
def dih_sunplot_data(dirname):
	filelist = glob.glob(dirname+"/*.fits")#get files
	maplist = []
	curvelist = []
	if len(filelist)>0:
		for idx,member in enumerate(filelist):#make list of sunpy maps
			print "mapping "+str(idx)
			my_map = sunpy.map.Map(member)
			maplist.append(my_map)
			sigma = np.sum(my_map)#creates lightcurve data
			curvelist.append(sigma)
		difflist = []
		for map in maplist:#populate difflist with time differences to first map
			string1 = maplist[0].date
			string2 = map.date
			d1 = datetime.strptime(string1, '%Y-%m-%dT%H:%M:%S.%f')
			d2 = datetime.strptime(string2, '%Y-%m-%dT%H:%M:%S.%f')
			deltatime = d2-d1
			diff = deltatime.total_seconds()
			difflist.append(diff)
		my_first_map = maplist[0]
		datalist = [curvelist,difflist,my_first_map.date,my_first_map.measurement,my_first_map.center,maplist]#data to be sent to larger plotting regime
		return datalist
	else:
		return 11
#
#
#Name:dih_sunmap_data
#
#Purpose:same job as dih_sunplot_data but with an already created maplist as input
#
#Inputs: list of sunpy maps
#
#Outputs:same as dih_sunplot_data minus the already stored maplist
#
#Written: 7/9/14 Dan Herman daniel.herman@cfa.harvard.edu

def dih_sunmap_data(inlist):
	maplist = inlist
	curvelist = []#flux list
	difflist = []#time difference list
	for map in maplist:#populate flux and time data
		sigma = np.sum(member)
		curvelist.append(sigma)
		string1 = maplist[0].date
		string2 = map.date
		d1 = datetime.strptime(string1, '%Y-%m-%dT%H:%M:%S.%f')
		d2 = datetime.strptime(string2, '%Y-%m-%dT%H:%M:%S.%f')
		deltatime = d2-d1
		diff = deltatime.total_seconds()
		difflist.append(diff)
	my_first_map = maplist[0]
	datalist = [curvelist,difflist,my_first_map.date,my_first_map.measurement,my_first_map.center]#data to be sent to larger plotting regime
	return datalist
