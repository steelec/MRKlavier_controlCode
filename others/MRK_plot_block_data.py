#!/usr/bin/python
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import filters
from scipy.signal import cspline1d as cspline
from scipy.signal import resample
import sys
#import glob
#from scipy.stats.mstats import zscore

#******************************************************
# Deal with command-line arguments
parser = argparse.ArgumentParser(description='Plot MRKlavier key position data from a single block/npy file. Plot triggers with id=255 if present.')
parser.add_argument('filename', type=str, help='file with nx7 numpy array (.npy)')
parser.add_argument('-b','--board_number',help='board to display (default = all)',type=int,default=0)
parser.add_argument('-k','--key_number',help='key to display (default = all)',type=int,default=0)
parser.add_argument('-t','--triggers',dest='triggers',help='plot triggers with data',action='store_true',default=False)
parser.add_argument('-g','--gaussian_filter_sigma',dest='sigma',help='filter data with gaussian of specified sigma (default = no filter)',type=int,default=0)
parser.add_argument('-s','--subsample',dest='subsample',help='only plot 1 in subsample samples (default = 2)',type=int,default=2)
parser.add_argument('-v','--velocity',dest='velocity',help='plot velocities of key onsets as well',action='store_true',default=False)
parser.add_argument('-o','--keyOn',dest='keyOn',help='plot keyOn from MIDI on events',action='store_true',default=False)

args=parser.parse_args()
adat=np.load(args.filename)
theBoard=args.board_number
theKey=args.key_number
showTrigs=args.triggers
gauss_sigma=args.sigma
subsamp=args.subsample
SHOW_VEL=args.velocity
SHOW_KEYONS=args.keyOn

if gauss_sigma==0:
    GAUSS_FILTER_DATA=False
else:
    GAUSS_FILTER_DATA=True
    
#******************************************************
# define some functions
def scale(sig):
    theNoise=np.mean(sig[0:100])
    return (sig-theNoise)#/(np.max(sig)-np.min(sig))

def sig_spline(sig):
    SMOOTHING_COEF=10000
    pos_csp=cspline(sig,SMOOTHING_COEF)	#spline of position data    
    vel = cspline(np.diff(pos_csp,n=1),SMOOTHING_COEF) #derivative (velocity) of spline

    vel_csp=cspline(vel,SMOOTHING_COEF)
    return pos_csp, vel_csp
# finish function definitions
#******************************************************


clear_time_trigger=True#False	#True
clear_trial_trigger=True#False	#True
samp_offset=10 #number of samples to skip from the beginning of the file (likely corrupt)
#subsamp=2 #subsampling, in samples
SHOWPLOTTING=True #true shows the plot key by key, this slows it down
RELATIVE_TIME=False #XXX not implemented, could be used to set first sample to 0 (i.e., at samp_offset)
#GAUSS_FILTER_DATA=True #apply 1d gaussian filter to key signals


#cleared= np.delete(adat, np.where(np.in1d(adat[:,0], 0)), 0)	#delete zeros, because they are bad. (well, just empty data)
#remove 0s if they exist

if 0 in adat[:,0]:
    cleared=adat[adat[:,0]!=0,:]
else:
    cleared=adat


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
trigs_idx=(cleared[:,0]==255).astype(int)
trigs_idx_b4=np.append(np.diff(trigs_idx),0) #make the length the same as the original data, create as bool for indexing
trigs=cleared[trigs_idx_b4==1,:]
# ***************************************************


# ***************************************************
# get the MIDI onsets so that they can be plotted later
if SHOW_KEYONS:	
	def MIDIget(cleared):
		MIDI_ons=[0,0,0,0,0,0,0]
		for keyOn_chan in range(248,248+7): #MIDI onsets labeled as 255-boardID and has the keyID (- for keyOff) {ID,keyID{1..4,-1..4},raw signalvel(mm/s),<reserved>,tickTime,UTCtime}
			MIDI_ons=np.vstack([MIDI_ons,cleared[cleared[:,0]==keyOn_chan,:]])
		MIDI_ons[:,0]=abs(MIDI_ons[:,0]-255) #convert to boardIDs
		return(MIDI_ons[1:,:])
        MIDI_on=MIDIget(cleared)
# ***************************************************

#special case of trigger in first sample
if cleared[0,0]==255:
    trigs=np.vstack([cleared[1,:],trigs])

if clear_trial_trigger:
    #clear triggers from data
    cleared=cleared[cleared[:,0]!=255,:]
# finish creating list of triggers
# *************************************************** 

#xrange=np.arange(5,len(cleared)-100)
unique_IDs=np.unique(cleared[:,0])
unique_boards=unique_IDs[unique_IDs<8]
print "Identified boards with the following IDs:"
print(unique_boards)
print "Plotting all boards and keys with y-offset = boardID"
print "Data has been mean centred and then divided by the minimum signal value for display"
print "Close the plot to close the program"

#if a single board was chosen for plotting, plot it
if not(theBoard==0):
    cleared=cleared[cleared[:,0]==theBoard,:]
    print("You have chosen to plot the results for boardID: " + str(theBoard))
    unique_boards=[theBoard] #keep as an array so that we can loop across it below
    try:
	cleared[0,0]
    except:
	print("#*****************************************************************************************#")
	print("Unfortunately you tried to plot data from a board that does not have any data! Exiting now.")
	print("#*****************************************************************************************#")
	sys.exit()
    
plt.ion()
plt.figure()
plt.suptitle(args.filename)
print("----------------------------------PLOTTING----------------------------------")
for board in unique_boards:
    print("")
    print("Board " + str(board) + ":")
    b=cleared[cleared[:,0]==board,:]
    #clean spurious timestamps (likely corrupted data)
    #XXX implement a diff-based determination here or would that be too slow?
    UTCstart=b[samp_offset,-1]
    UTCstop=b[-samp_offset,-1]
#    BAD_UTC=np.diff(b[:,-1])>1 #where diff is greater than 1s
    UTCmax=7*2*60+UTCstart #arbitrary based on current experiment (YES, it is a quick hack)
    b=b[b[:,-1]<UTCmax,:]

    if GAUSS_FILTER_DATA:
        b[samp_offset:,1:5]=filters.gaussian_filter1d(b[samp_offset:,1:5],gauss_sigma,0)
    if subsamp!=1:
        b=b[np.arange(0,np.shape(b)[0],subsamp),:] #just look at a subset of the data, nothing fancy... only reporting the subsample-ith element

    if SHOW_KEYONS:
        b_ons=MIDI_on[MIDI_on[:,0]==board,:] 
        b_ons=b_ons[b_ons[:,-1]<UTCstop,:]
        b_ons[:,-1]=b_ons[:,-1]-b[samp_offset,-1] #zero the time
        

    
    #zero the UTC time to the beginning of the offset (NOT THE BEGINNING OF THE EXPERIMENT!!! XXX)
    #this is only for display purposes, do not interpret absolute times (because 0 is arbitrary)
    b[:,-1]=b[:,-1]-b[samp_offset,-1]
    
    for key in range(1,5):
        if key==1:
            lspec='r.:'
        if key==2:
            lspec='b.:'
        if key==3:
            lspec='g.:'
        if key==4:
            lspec='k.:'
            print("")
        sig=(b[samp_offset:,key]-np.mean(b[samp_offset:,key]))/abs(np.min(b[samp_offset:,key]))+board #remove mean, scale to MIN value (max depression), add offset, all board now at y=boardID
        sig_t=b[samp_offset:,-1]

        if SHOW_KEYONS:
            keyOns=b_ons[b_ons[:,1]==key,:]
            keyOffs=b_ons[b_ons[:,1]==key*-1,:]

	#sig = scale(b[samp_offset:,key]-np.mean(b[samp_offset:,key]))+board
        sig,vel = sig_spline(sig)

#	if subsamp!=1:
#		sig, sig_t = resample(sig, t=sig_t, num=np.shape(sig)[0]/subsamp)

        if (board==7.) and (key==4):
            pass
            print("Data for board 7, key 4 was not plotted")
        else:
            if theKey==0: #plot all keys
                #plt.plot(sig)
                plt.plot(sig_t,sig,lspec)
                if SHOW_KEYONS and np.shape(unique_boards)[0]==1: #only do this when plotting a single board, too messy otherwise
                    lspec=lspec[:-2]+'+--' #make it a line
                    if np.shape(keyOns)[0]==1:
                        keyOns=[keyOns] #make it iterable if there is only one element
                    for keyOn in keyOns:
                        plt.plot([keyOn[-1],keyOn[-1]],[board-.5,board+.5],lspec)
                if SHOW_KEYONS and np.shape(unique_boards)[0]==1:
                    lspec=lspec[:-3]+'*--' #make it a line
                    if np.shape(keyOffs)[0]==1:
                        keyOffs=[keyOffs] #make it iterable if there is only one element
                    for keyOff in keyOffs:
                        plt.plot([keyOff[-1],keyOff[-1]],[board-.5,board+.5],lspec)
                if SHOW_VEL and np.shape(unique_boards)[0]==1:
                    lspec=lspec[0]+":"
                    plt.plot(sig_t[1:],vel+board,lspec)
                print("key " + str(key)),
            elif key==theKey:
		plt.subplot(2,1,1)
                plt.plot(sig_t,sig,lspec)
                if SHOW_KEYONS:
                    lspec=lspec[:-2]+'+--' #make it a line
                    if np.shape(keyOns)[0]==1:
                        keyOns=[keyOns] #make it iterable if there is only one element
                    for keyOn in keyOns:
                        plt.plot([keyOn[-1],keyOn[-1]],[board-.5,board+.5],lspec)
                if SHOW_KEYONS:
                    lspec=lspec[:-3]+'*--' #make it a line
                    if np.shape(keyOffs)[0]==1:
                        keyOffs=[keyOffs] #make it iterable if there is only one element
                    for keyOff in keyOffs:
                        plt.plot([keyOff[-1],keyOff[-1]],[board-.5,board+.5],lspec)
                if SHOW_VEL and np.shape(unique_boards)[0]==1:
		    plt.subplot(2,1,2)
                    lspec=lspec[0]
                    plt.plot(sig_t[:-1],vel+board,lspec)
                print("key " + str(key)),
        if SHOWPLOTTING:
            plt.draw()

if showTrigs: 
    # plot triggers, no intelligence on the y-range here
    if np.shape(trigs)[0]==1:
		trigs=[trigs] #make it iterable if there is only one element
    for trig in trigs:
        plt.plot([trig[-1],trig[-1]],[0,8],'k-.')
#	plt.text(trig[-1],8.1,str(trig[-1]))
    if theKey==0:
        plt.legend(['k1','k2','k3','k4','trig'])
else:
    plt.grid()
    if theKey==0: #only plot the legend if we have more than one key
		plt.legend(['k1','k2','k3','k4'])


#rescale the plot if we are only looking at data from a single board
#if theBoard!=0:
#    plt.ylim([ theBoard-1, theBoard+1]);

plt.ylabel('Board Number')
plt.xlabel('Time (s) (UTC)')
plt.show(block=True) #block=True keeps plot after program exits
#keys_filt=filters.gaussian_filter1d(keys[10:,:],4,0)
