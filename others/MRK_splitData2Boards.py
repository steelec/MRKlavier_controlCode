#!/usr/bin/python
import argparse
import numpy as np
import sys
import os
#import glob
#from scipy.stats.mstats import zscore

#******************************************************
# Deal with command-line arguments
parser = argparse.ArgumentParser(description='Split single data file with MRKlavier key position data from a single block/npy file into one file per board. All boards output by default.')
parser.add_argument('filename', type=str, help='file with nx7 numpy array (.npy)')
parser.add_argument('-b','--board_number',help='create new file with data from only this board (default = all)',type=int,default=0)
#parser.add_argument('-g','--gaussian_filter_sigma',dest='sigma',help='filter data with gaussian of specified sigma (default = no filter)',type=int,default=0)
#parser.add_argument('-s','--subsample',dest='subsample',help='only plot 1 in subsample samples (default = 2)',type=int,default=2)

args=parser.parse_args()
adat=np.load(args.filename)
theBoard=args.board_number
#gauss_sigma=args.sigma
#subsamp=args.subsample

#if gauss_sigma==0:
#    GAUSS_FILTER_DATA=False
#else:
#    GAUSS_FILTER_DATA=True
  
# finish with command-line arguments
#******************************************************

clear_time_trigger=False	#True
clear_trial_trigger=False	#True
samp_offset=0 #number of samples to skip from the beginning of the file (likely corrupt)
#subsamp=2 #subsampling, in samples
SHOWPLOTTING=False #true shows the plot key by key, this slows it down
RELATIVE_TIME=False #XXX not implemented, could be used to set first sample to 0 (i.e., at samp_offset)
#GAUSS_FILTER_DATA=True #apply 1d gaussian filter to key signals


#remove 0s if they exist
if 0 in adat[:,0]:
    cleared=adat[adat[:,0]!=0,:]
    print("I cleaned data elements that had a boardID = 0 from the output.")
else:
    cleared=adat

#OR no data cleaning
#cleared=adat
    
#remove TIME_SYNC triggers if requested
if clear_time_trigger:
	for time_chan in range(129,129+7): #the timer reset codes are 128+boardID, there are 7 boards
		if time_chan in cleared[:,0]:
			#cleared= np.delete(cleared, np.where(np.in1d(cleared[:,0], time_chan)), 0)	#delete time stamps
			cleared=cleared[cleared[:,0]!=time_chan,:]

# ***************************************************
# create an array of the id=255 trial triggers 
# get idx, grab timestamp from the sample just before the trigger to use as a PROXY for the trigger time
# XXX Avrum does not reccomend this method - Roberta needs to check it against the log file (or you need to write a script to parse that too... :-/)

if clear_trial_trigger:
    #clear triggers from data
    cleared=cleared[cleared[:,0]!=255,:]

#xrange=np.arange(5,len(cleared)-100)
unique_IDs=np.unique(cleared[:,0])
unique_boards=unique_IDs[unique_IDs<8]
print "Identified boards with the following IDs:"
print(unique_boards)

def saveThisBoard(cleared,board):
    theBoardData=cleared[cleared[:,0]==board,:]
    dataFileName=os.path.abspath(args.filename)[:-4]+"_boardID_" + str(int(board)) + ".npy"
    print("You have chosen to grab the results for boardID: " + str(int(board)))
    print("Data stored in: " + dataFileName)
    try:
	theBoardData[0,0]
	outfile_h=open(dataFileName,'wb')
	np.save(outfile_h,theBoardData)
    except:
	print("#*****************************************************************************************#")
	print("Unfortunately you tried to save data from a board that does not have any data! Exiting now.")
	print("#*****************************************************************************************#")
	sys.exit()    

#if a single board was chosen tell us and output this one
if not(theBoard==0):
    saveThisBoard(cleared,theBoard)
else:
    for board in unique_boards:
	saveThisBoard(cleared,board)
