import numpy as np
import ast
import glob
import os.path
#
#
#
#
#
#Name: dih_get_outliers
#
#Purpose: finds outliers in hist data
def dih_get_outliers(filename):
	file = open(filename,'r')
	line = file.readlines()
	info = ast.literal_eval(line[0])
	outliers = [j for j in info if j[-2] > 100 or j[-2] < -100]
	return [outliers,info]
#
#
#
#
#Name: dih_find_event
#
#Must rewrite this!
def dih_find_event(timestring,filename):
	file = open(filename,'r')
	line = file.readlines()
	interest = line[0]
	firstnum = interest.find(timestring)
	print interest[int(firstnum),int(firstnum+400)]
	return interest[int(firstnum),int(firstnum+400)]
#
#
#
#
#Name: dih_track_george
#
#Purpose: finds ivo files in george with no sav file
def dih_track_george(num):
	if num < 1000:
		files = glob.glob('/data/george/hwinter/data/Flare_Detective_Data/Event_Stacks/Working/ivo*')
		nums = []
		for member in files:
			list1 = glob.glob(member+'/fits/*.fits')
			indexivo = member.find('ivo')
			ivostring = member[indexivo:]
			if os.path.isfile(member+'/'+ivostring + '.sav') == True:
				stringsav = 'yes there is a sav file'
			else:
				stringsav = 'no sav file'
			nums.append([member,len(list1),stringsav])
		return zip(*nums)
#
#
#
#Create line transfer function
