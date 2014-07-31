import numpy as np
import os
import dih_smoothsun
import simplejson
import pickle
from dih_smoothsun import dih_sun_plotter
from dih_smoothsun import dih_sun_recurs_shared_plot
from dih_smoothsun import dih_sun_recurs_data_plot
from dih_hist_171_peaks import dih_hist_events
#
#
#
#
#Name: dih_data_routine1()
#
#Purpose: Performs sunpy mapping, plotting of individual light curves, plotting of cotemporal (shared) light curves, creation of histograms depicting time separation of channels for the same event
#
#Inputs: directory containing ivo files (dirname), over-arching savename to tie all data/metadata together
#
#Outputs: txt files with rawdata,metadata for each lightcurve; plots of lightcurves (shared and individual); histograms of channel separation and histogram data txt files
#
#Example: gah = dih_data_routine1('/data/george/dherman/ivos','sun_block')
#
#Written: 7/24/14 Dan Herman daniel.herman@cfa.harvard.edu
#
# 

def dih_data_routine1(dirname,savename):
	#creates lightcurves, metadata, rawdata for ivo files
	ivo_list = dih_sun_plotter(dirname,savename)
	#creates shared_plots
	total_shared_meta = dih_sun_recurs_shared_plot('/data/george/dherman/metadata/'+ savename+'_all_human_meta.txt',savename,'shared_plot')
	channel_list = [131,171,211,304,335,193]
	all_hist_info = []
	#creates histograms for all channel combinations
	for channel in channel_list:
		other_channel_list = [j for j, j in enumerate(channel_list) if j != channel]
		for member in other_channel_list:
			hist_info = dih_hist_events('/data/george/dherman/metadata/'+ savename+'_all_human_meta.txt',str(channel)+'_'+str(member)+'_hist_'+savename,channel,member)
			hist_file = open('/data/george/dherman/metadata/'+savename+'all_peak_comparison_human_meta.txt','a')
			simplejson.dump(hist_info,hist_file)
			hist_file.close()
			all_hist_info.append(hist_info)
	return all_hist_info
#
#Name: dih_data_routine1_cropped
#
#
#
#
def dih_data_routine1_cropped(dirname,savename):
	#creates lightcurves, metadata, rawdata for ivo files
	ivo_list = dih_sun_cropped_plotter(dirname,savename)
	#creates shared_plots
	total_shared_meta = dih_sun_recurs_shared_plot('/data/george/dherman/metadata/'+ savename+'_all_human_meta.txt',savename,'shared_plot')
	channel_list = [131,171,211,304,335,193]
	all_hist_info = []
	#creates histograms for all channel combinations
	for channel in channel_list:
		other_channel_list = [j for j, j in enumerate(channel_list) if j != channel]
		for member in other_channel_list:
			hist_info = dih_hist_events('/data/george/dherman/metadata/'+ savename+'_all_human_meta.txt',str(channel)+'_'+str(member)+'_hist_'+savename,channel,member)
			hist_file = open('/data/george/dherman/metadata/'+savename+'all_peak_comparison_human_meta.txt','a')
			simplejson.dump(hist_info,hist_file)
			hist_file.close()
			all_hist_info.append(hist_info)
	return all_hist_info
#
#
#Name:dih_data_routine2()
#
#Purpose: Does same work as routine1 but with rawdata already created (no sunpy mapping necessary)
#
#Inputs: original directory containing ivos (dirname), original over-arching savename, additional savestring (newname), test == 1 sends data to test directories in george
#
#Outputs: txt files with rawdata,metadata; lightcurves, histograms (same as routine1)
#
#Example: gah = dih_data_routine2('/data/george/dherman/ivos','sun_block','test_six',1)
#
#Written 7/24/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#


def dih_data_routine2(dirname,savename,newname,test):
	#creates lightcurves,metadata from already created rawdata
	all_meta = dih_sun_recurs_data_plot(dirname,savename,newname,test)
	#directs shared_plot files to directories based on keyword value
	if test == 1:
		total_shared_meta = dih_sun_recurs_shared_plot('/data/george/dherman/metadata_test/'+ savename + '_' + newname + '_all_human_meta.txt',savename,newname,test)
	elif test == 0:
		total_shared_meta = dih_sun_recurs_shared_plot('/data/george/dherman/metadata/'+ savename + '_' + newname + '_all_human_meta.txt',savename,newname,test)
	else:
		print 'Bad Keyword!'
	channel_list = [131,171,211,304,335,193]
	all_hist_info = []
	#creates histograms for all channel combinations
	for channel in channel_list:
		other_channel_list = [j for j, j in enumerate(channel_list) if j != channel]
		for member in other_channel_list:
			if test == 1:
				hist_info = dih_hist_events('/data/george/dherman/metadata_test/'+ savename+ '_' + newname + '_all_human_meta.txt',str(channel)+'_'+str(member)+'_hist_'+savename + '_' + newname,channel,member)
				hist_file = open('/data/george/dherman/metadata_test/'+savename+ '_' + newname + 'all_peak_comparison_human_meta.txt','a')
			elif test == 0:
				hist_info = dih_hist_events('/data/george/dherman/metadata/'+ savename + '_' + newname + '_all_human_meta.txt',str(channel)+'_'+str(member)+'_hist_'+savename + '_' + newname,channel,member)
				hist_file = open('/data/george/dherman/metadata/'+savename+ '_' + newname + 'all_peak_comparison_human_meta.txt','a')
			simplejson.dump(hist_info,hist_file)
			hist_file.close()
			all_hist_info.append(hist_info)
	return all_hist_info