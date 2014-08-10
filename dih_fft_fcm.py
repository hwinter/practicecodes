import os  
import glob 
import datetime
import time
import shutil
import sys
import re
import subprocess
import multiprocessing as mp
import scipy
from scipy.io.idl import readsav
import scipy.ndimage as image
import sunpy
import sunpy.map
import numpy as np
import pickle
import pyfits
###########################################################################
###########################################################################
def dih_get_event_peak_time(ev):
	"""
	extract the peak time from the event file
	
	Parameters:
	==========
	ev: event object
	
	Output:
	==========
	peak_time: event peak time (string format)
	"""
	peak_time = ev.event.EVENT_PEAKTIME[0]
	start_time = ev.event.EVENT_STARTTIME[0]
	end_time = ev.event.EVENT_ENDTIME[0]
	return [peak_time,start_time,end_time]
###########################################################################
###########################################################################
def dih_get_event_bounding_box(ev):
    """
    extract the coordinates, in arcseconds from the event file.
    
    Parameters:
    ==========
    ev: event object

    Output:
    ==========
    bbc: Bounding box coordinates [x1, y1, x2, y2]
    """
    bbc=[float(ev.event.BOUNDBOX_C1LL[0]),float(ev.event.BOUNDBOX_C2LL[0] ),
         float(ev.event.BOUNDBOX_C1UR[0]),float(ev.event.BOUNDBOX_C2UR[0] )]
         #print('bbc: ', bbc)
    return bbc
###########################################################################
###########################################################################
def dih_get_cropped_map(ev, file_list,savename):
    """
    
    
    Parameters:
    ==========
    ev: event object
    file_list: List of fits files to restore

    Output:
    ==========
    out_map_list: A list of map objects containing cropped images based of the
             event bounding box.
    """
  
    #Get the coordinates of the bounding box in arcsec
    bbc= dih_get_event_bounding_box(ev)
    out_map_list=[]
    for idx,file in enumerate(file_list):
    	print 'testing file ' + str(idx)
    	try:
    		file_open = pyfits.open(file)
    		file_data = file_open[0].data
    		print "Creating cropped map " + str(idx)
    		#Changed after Sunpy V0.5.0
    		#temp_map= sunpy.make_map(file)
    		temp_map=sunpy.map.Map(file)
    		temp_map=temp_map.submap([bbc[0], bbc[2]],[bbc[1], bbc[3]])
    		out_map_list.append(temp_map)
    		file_AIA_index = file.find('AIA')
    		file_AIA_string = file[file_AIA_index:-5]
            #if os.path.isfile('/data/george/dherman/sun_maps/'+ file_AIA_string + '_' + savename + '_' + str(idx) + '_cropped.fits') == False:
            #temp_map.save('/data/george/dherman/sun_maps/'+ file_AIA_string + '_' + savename + '_' + str(idx) + '_cropped.fits', filetype='fits')
    	except ValueError:
    		print 'Truncated fits file!'
    	except IOError:
			print 'Corrupt/Empty fits file!'
    print("out_map_list",len(out_map_list))
    return out_map_list
###########################################################################
