# Name: dih_tableread.py
#
#
#
#
#
#
#
#
#
import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab
import glob

#grabs columns of data from ascii files and returns x and y columns
def dih_filegrab(filename):
    cts = np.genfromtxt(filename, skip_header=2, skip_footer=1)
    return zip(*cts)

#removes files from directory and grabs columns of data
def dih_tablereader(dirname):
    filelist = glob.glob(dirname+"/*.data")
    openlist = []
    for filename in filelist:
        filecontent = dih_filegrab(filename)
        openlist.append(filecontent)
    print filelist
    return openlist
#Name:dih_plotter
#
#Purpose:plots the first number = (numplot) files in directory = (dirname) filled with ascii files and places marker on peak data point for each plot saves plot as savename
#
#Inputs:dirname-- directory name, savename-- plot file saved as postscript with this name, numplot-- number of files from directory to be plotted
def dih_plotter(dirname,savename,numplot):
    inlist = dih_tablereader(dirname,savename)
    plotlist = inlist[0:numplot]
    for memberlist in plotlist:
        x = memberlist[0] #x coordinate data
        y = memberlist[1] #y coordinate data
        peak = max(y)
        peaklist = [i for i, j in enumerate(y) if j==peak] #list of indices of peak points
        plt.plot(x,y,'b')
        for num in peaklist:
            plt.plot(x[num],y[num],'gD')#places markers on peaks
#finish up plot characteristics
    plt.title('Super Most Awesome Graph!')
    plt.ylabel('Flux')
    plt.xlabel('Time')       
    pylab.ylim([-1.5,4.5])
    pylab.xlim([0,6.3])
    plt.savefig(savename)
    return plotlist

    
    
        

















if __name__ == "__main__": 
    
    if len(sys.argv) != 4:
        print("You suck!")
        sys.exit(1)
    
    dih_plotter(sys.argv[1], sys.argv[2],sys.argv[3])