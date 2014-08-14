import numpy as np
import os
import simplejson
import pickle
from dih_sun_data_goes_scratch_plot import dih_sun_recurs_goes_scratch_plot
from dih_hist_goes_131_scratch import dih_hist_goes_131_scratch
from dih_smoothsun import dih_sun_recurs_shared_plot

#
#
#
#Name: dih_scratch_routine
#
#Purpose: Runs all necessary data routines to make histograms/plots for all my AIA data (and add new data to data set)
#
#Inputs: directory where new files came from -> dirname, ubersavename for new files -> savename, new save string for new files -> newname, list of older file save strings in scratch -> savelist1, list of older file save strings in george -> savelist2, name for new histograms ->histname
#
#Outputs: metadata,rawdata for new files, metadata about shared plots, shared plots, histogram and histogram data/metadata
#
#Example: final = dih_data_131_goes_routine('/data/george/hwinter/*/Working','aia_data_block','comtest1',['aia_data2_block_comtest4'],'newhist')
#
#Written: 8/1/14 Dan Herman daniel.herman@cfa.harvard.edu
#
def dih_scratch_routine(dirname,savelist1,savelist2,histname):
	meta_path = '/data/george/dherman/metadata/'
	meta_path2 = '/Volumes/Scratch/Users/dherman/sundata/metadata/'
	#if type(savename) == str and type(newname) == str:
		#save_path = savename + '_' + newname
		#savelist.append(save_path)
		#all_meta = dih_sun_recurs_data_plot(dirname,savename,newname,0)
	for member in savelist1:
		split = member.split('_')
		save = split[0]+'_'+split[1]+'_'+split[2]
		new = split[3]
		#uber_goes_metadatalist = dih_sun_recurs_goes_scratch_plot(meta_path2 + member + '_human_meta_131.txt',member)
	for member in savelist2:
		split = member.split('_')
		save = split[0]+'_'+split[1]+'_'+split[2]
		new = split[3]
		total_shared_meta = dih_sun_recurs_shared_plot(meta_path+ member + '_all_human_meta.txt',save,new,0)
		#uber_goes_metadatalist = dih_sun_recurs_goes_scratch_plot(meta_path + member + '_human_meta_131.txt',member)
	savelist = savelist1 + savelist2
	hist_final = dih_hist_goes_131_scratch(savelist,histname)
	return hist_final