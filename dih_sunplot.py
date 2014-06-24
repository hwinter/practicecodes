import sunpy
import sunpy.map
import glob
from sunpy.image.coalignment import mapcube_coalign_by_match_template

def dih_sunplot(dirname):
	filelist = glob.glob(dirname+"/*.fits")
	maplist = []
	for member in filelist:
		my_map = sunpy.map.Map(member)
		maplist.append(my_map)
	mapcube = sunpy.map.Map(maplist,cube = True)
	alignedcube = mapcube_coalign_by_match_template(mapcube)
    return alignedcube

	

