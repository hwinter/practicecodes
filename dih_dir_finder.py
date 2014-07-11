import os
import glob
#
#
#Name: dih_dir_finder
#
#Purpose: given a directory containing ivo files, extracts all directories containing fits files
#
#Inputs: directory with ivo files (dirpath)
#
#Outputs: list of directories containing fits files (fitslist)
#
#Written: 6/26/14	Dan Herman	daniel.herman@cfa.harvard.edu

def dih_dir_finder(dirpath):
    dirlist = [os.path.join(dirpath, f) for f in os.listdir(dirpath)]#open up first directory and list subdirectories/files
    ivolist = []#create list for ivo files
    for member in dirlist:#populate ivo list
    	if 'ivo' in member:
    		ivolist.append(member)
    gutslist = []#create list for guts of ivo files
    for member in ivolist:#populate the guts list
    	app = [os.path.join(member, f) for f in os.listdir(member)]
    	gutslist.append(app)
    fitslist = []#create list for fits files
    for list in gutslist:#populate fitslist with the appropriate files and remove ones we don't need
    	for member in list:
    		if 'DS_Store' in member:
    			continue
    		if '.sav' in member:
    			continue
    		if '.png' in member:
    			continue
    		if '.mp4' in member:
    			continue
    		if 'fits' in member:
    			fitslist.append(member)
    		if '.log' in member:
    			fitslist.remove(member)
    		if '.pro' in member:
    			fitslist.remove(member)
    		if '.txt' in member:
    			fitslist.remove(member)
    		if '.DS_Store' in member:
    			fitslist.remove(member)
    		if '.sav' in member:
    			fitslist.remove(member)
    		if '.png' in member:
    			fitslist.remove(member)
    		if '.mp4' in member:
    			fitslist.remove(member)
    return [fitslist,ivolist]