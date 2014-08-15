import numpy as np
import os
import dih_smoothsun
import simplejson
import pickle
from dih_smoothsun import dih_sun_plotter
from dih_smoothsun import dih_sun_recurs_shared_plot
from dih_smoothsun import dih_sun_recurs_data_plot
from dih_hist_171_peaks import dih_hist_events
from dih_hist_171_peaks import dih_hist_goes_131
from dih_hist_171_peaks import dih_hist_goes_131_scratch
from dih_sun_data_goes_plot import dih_sun_recurs_goes_plot
from dih_sun_data_goes_plot import dih_sun_recurs_goes_scratch_plot
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
#
#
#Name: dih_data_131_goes_routine
#
#Purpose: Runs all necessary data routines to make histograms/plots for all my AIA data (and add new data to data set)
#
#Inputs: directory where new files came from -> dirname, ubersavename for new files -> savename, new save string for new files -> newname, list of older file save strings -> savelist, name for new histograms ->histname
#
#Outputs: metadata,rawdata for new files, metadata about shared plots, shared plots, histogram and histogram data/metadata
#
#Example: final = dih_data_131_goes_routine('/data/george/hwinter/*/Working','aia_data_block','comtest1',['aia_data2_block_comtest4'],'newhist')
#
#Written: 8/1/14 Dan Herman daniel.herman@cfa.harvard.edu
#
def dih_data_131_goes_routine(dirname,savename,newname,savelist,histname):
	meta_path = '/data/george/dherman/metadata/'
	if type(savename) == str and type(newname) == str:
		save_path = savename + '_' + newname
		savelist.append(save_path)
		all_meta = dih_sun_recurs_data_plot(dirname,savename,newname,0)
	for member in savelist:
		split = member.split('_')
		save = split[0]+'_'+split[1]+'_'+split[2]
		new = split[3]
		#shared plots
		total_shared_meta = dih_sun_recurs_shared_plot(meta_path+ member + '_all_human_meta.txt',save,new,0)
		#get goes data
		uber_goes_metadatalist = dih_sun_recurs_goes_plot(meta_path + member + '_human_meta_131.txt',member)
	#make histogram
	hist_final = dih_hist_goes_131(savelist,histname)
	return hist_final
#
#
#
#
#
#
#Name: dih_data_131_goes_scratch_routine
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
def dih_data_131_goes_scratch_routine(dirname,savelist1,savelist2,histname):
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
		uber_goes_metadatalist = dih_sun_recurs_goes_scratch_plot(meta_path2 + member + '_human_meta_131.txt',member)
	for member in savelist2:
		split = member.split('_')
		save = split[0]+'_'+split[1]+'_'+split[2]
		new = split[3]
		#total_shared_meta = dih_sun_recurs_shared_plot(meta_path+ member + '_all_human_meta.txt',save,new,0)
		uber_goes_metadatalist = dih_sun_recurs_goes_scratch_plot(meta_path + member + '_human_meta_131.txt',member)
	savelist = savelist1 + savelist2
	hist_final = dih_hist_goes_131_scratch(savelist,histname)
	return hist_final
	