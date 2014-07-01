#Name: tableread2
#
#Purpose: read two columns of data and create postscripted version of the plotted data
#
#Inputs:filename 1/2/3 are ascii files with 2 columns, savename is the name for the postscript
#
#Outputs: totalplot is a list with the structure: [[[file 1 column 1],[file 1 column 2]],[[file 2 column 1] etc...]
#
#Example: tableread2('foo.txt','bar.txt','crum.txt', 'kitkat')
#
#Written:6/17/13 Daniel Herman, daniel.herman@cfa.harvard.edu
#
#import necessary packages and set matplotlib.use to postscript
import sys
import numpy as np
import matplotlib
matplotlib.use('ps')
import matplotlib.pyplot as plt 
import pylab

def tableread2(filename1,filename2,filename3,savename):
    #read in data from ascii files and split each data set into x and y vectors
    #line1 = x coordinates, line2 = y coordinates
    aline = np.genfromtxt(filename1, skip_header = 2, skip_footer = 1)
    aline1, aline2 = zip(*aline)
    bline = np.genfromtxt(filename2, skip_header = 2, skip_footer = 1)
    bline1, bline2 = zip(*bline)    
    cline = np.genfromtxt(filename3, skip_header = 2, skip_footer = 1)
    cline1, cline2 = zip(*cline)   
    #plot data using pyplot and save it
    plt.plot(aline1,aline2,'r',bline1,bline2,'g',cline1,cline2,'b') 
    plt.title('Super Awesome Graph!')
    plt.ylabel('Flux')
    plt.xlabel('Time')
    pylab.ylim([-1.5,4.5])
    pylab.xlim([0,6.3])
    plt.savefig(savename)
    #create return variable
    totalplot = [aline,bline,cline]
    return totalplot
    
    

if __name__ == "__main__": 

    if len(sys.argv) != 5:
        print("You suck!")
        sys.exit(1)
        
    tableread2(sys.argv[1], sys.argv[2],sys.argv[3],sys.argv[4])

