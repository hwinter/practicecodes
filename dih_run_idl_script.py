import pidly
from dih_tableread import dih_filegrab2
import ast
import subprocess
import os.path
#
#Name: dih_run_idl_goes_script
#
#Purpose: runs an idl program to extract goes data for a certain time range
#
#Inputs: start and end time strings in format 'day-month(abbreviation)-year hours:minutes:seconds.microseconds', save_name -> file name to be created by dih_get_goes.pro
#
#Outputs: columns of goes data in a list (2 columns in one list)
#
#Examples: columns = dih_run_idl_goes_script('01-May-2012 00:00:00.00','02-May-2012 00:00:00.00','goes_curve.txt')
#
#Written: 7/31/14 Dan Herman daniel.herman@cfa.harvard.edu
#
#

def dih_run_idl_goes_script(start_time,end_time,save_name):
	idl = pidly.IDL('/proj/DataCenter/ssw/gen/setup/ssw_idl')
	idl.pro('dih_get_goes',start_time,end_time,save_name)
	print 'here'
	#txt_file = open(save_name,'r')
	#txt_lines = txt_file.readlines()
	#txt_header = ast.literal_eval(txt_lines[0])
	if os.path.isfile(save_name) == True:
		columns = dih_filegrab2(save_name)
	else:
		return 11
	idl.close()
	subprocess.call(["killall", "idl"])
	return zip(*columns)