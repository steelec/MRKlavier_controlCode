#python tcp stream test script

import socket
import numpy as np
#import matplotlib.pyplot   as  plt
#from bitstring import *
from struct import *
import sys
import os
import time
from time import ctime
import ntplib
import serial
import logging
import glob
import subprocess
#import cPickle
import json
import mido
import atexit
#ntpServerIP="192.168.1.1"
from scipy.signal import cspline1d as cspline
from scipy.stats.mstats import zscore
import matplotlib.pyplot as plt


serial_timeout=0.01
global adat
ntpServerIP_default='192.168.1.10'
    

def scale_vel_to_midi(vel):
    #velocities tend to go from appx 100 to appx 2000?
    #max key velocity close to 1.5m/s (paper reference) 
    mapping="Power" # "Natural_Log" "Quadratic" "Square_Root" "Sigmoid", "Linear", "DEFAULT"
    MAX_VAL=127
    
    if mapping=="Power":
        POWER=.5
        CONST=0 #default=0
        MIN_VEL=50
        MAX_VEL=4000
        norm_vel=abs((vel-MIN_VEL)/(MAX_VEL-MIN_VEL))**POWER
        mvel=norm_vel*MAX_VAL+CONST
    elif mapping=="Sigmoid":
        #need to scale betwen -1 and 1 for sigmoid function
        MIN_VEL=100
        MAX_VEL=2000
        K=-5                    #describes the steepness of the sigmoid
        SKEW=-.4                #0 is symmetrical sigmoid, negative values push the curve to the left, positive to the right (+/-.5 seem reasonable)
        norm_vel=2*(vel-MIN_VEL)/(MAX_VEL-MIN_VEL)-1 #scale between -1 and 1 (y = 2*(x - min(x))/(max(x) - min(x)) - 1)
        mvel=1/(1+np.exp(K*(norm_vel-SKEW)))*MAX_VAL
        #norm_vel=2*(np.log(vel)-np.log(MIN_VEL))/(np.log(MAX_VEL)-np.log(MIN_VEL))-1 #scale between -1 and 1 (y = 2*(x - min(x))/(max(x) - min(x)) - 1)
        #mvel=1/(1+np.exp(K*(norm_vel-SKEW)))*MAX_VAL
    elif mapping=="Cubic":
        #also scale between -1 and 1
        MIN_VEL=100
        MAX_VEL=2000
        norm_vel=2*(vel-MIN_VEL)/(MAX_VEL-MIN_VEL)-1 #scale between -1 and 1 (y = 2*(x - min(x))/(max(x) - min(x)) - 1)
        mvel=abs((norm_vel**3+1)/2)*MAX_VAL 
    elif mapping=="Natural_Log":
        VEL_SCALAR=20
        lscaler=.3
        mvel=np.log(lscaler*vel)*VEL_SCALAR     #np.log is natural log, use np.log10 for base 10
    elif mapping=="Linear":
        MIN_VEL=100
        MAX_VEL=2000
        norm_vel=(vel-MIN_VEL)/(MAX_VEL-MIN_VEL)
        mvel=norm_vel*MAX_VAL
    elif mapping=="DEFAULT":
        mvel=MAX_VAL/2
    
    if mvel>MAX_VAL:
        mvel=MAX_VAL
    if mvel<0:
        mvel=0
    return int(mvel)

def List2Array(alist):
    yy=[]
    for aline in alist:
        if type(aline[0]) is list:
            for bline in aline:
                yy.append(bline)
        else:
            yy.append(aline)
    return np.array(yy)


def getLocalMachineIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); 
    s.connect(('192.168.1.1', 80)); 
    print("Local Machine IP is: " + s.getsockname()[0]); 
    IPstr=s.getsockname()[0]
    s.close()
    return IPstr
try:
    ntpServerIP=getLocalMachineIP()
except:
    print("Can't automatically find local machine trying default IP")
    ntpServerIP=ntpServerIP_default

def Closing(myBoards):
    for devName in myBoards:
        try:
            myBoards[devName].close_stream()
        except:
            print "No stream to close"
        try:
            myBoards[devName].close_serial_port()
        except:
            print "No serial port to close"

        try:
            print myBoards[devName].Blogger.handlers
            for hand in list(myBoards[devName].Blogger.handlers):   #important casting/copying list as we're deleting elements from it!
                myBoards[devName].Blogger.warn("Removing handler for logger: " + str(hand))
                myBoards[devName].Blogger.removeHandler(hand)
            print myBoards[devName].Blogger.handlers
        except:
            print "Board logger had trouble closing"
            #raise
    print "Closed! Now to exit!"
    #sys.exit()


class MyBoard:
    def serRead(self):
            linelist=[]
            
            while (self.serPort.inWaiting()):
                newline=self.serPort.readlines(1)
                linelist.append(newline)
                
                if (newline[0] =="\r\n") or (newline[0]=="ARM$ \n") or (newline[0]=="ARM$ "):   
                    continue #don't log blank lines, continue while loop from start
                
                try:    #just in case logger isn't yet active, don't throw an exception
                    self.Blogger.info(newline[0])
                except:
                    pass
            return linelist

    def C3toNTP(self,C3val):

        return (float(C3val)-float(self.counter3_lastSync))/100000.0+self.ntp_sec_float_lastSync

    def NTPtoUTC(self,NTPval):
        return float(NTPval)-float(2208988800)

    def AddSyncOffset(self,fseconds):
        return float(fseconds)+float(self.lastSyncOffset)


    

    def parseTime(self,serDat):
        for sline in serDat:
            if "clock offset" in sline[0]:
                
                oline=sline[0].split("clock offset (seconds): ")
                oline=oline[1].split("\t and us: ")
                offset_seconds=float(oline[0])
                oline=oline[1].split("\r\n")
                self.offset_seconds=offset_seconds+float(oline[0])/1000.0/1000.0
                self.Blogger.info("Offset is (seconds): "+ str(self.offset_seconds))

            elif "Received NTP time is secs,fracs:" in sline[0]:
                uline=sline[0].split("Received NTP time is secs,fracs: ")
                uline=uline[1].split(",")
                self.ntp_sec_int_recv=int(uline[0])
                
                self.ntp_frac_int_recv=int(uline[1])
                self.Blogger.info("Received NTP time seconds (int): " + str(self.ntp_sec_int_recv) + ", and fractional (int): " + str(self.ntp_frac_int_recv))
                
                self.ntp_sec_float_recv=float(uline[0])+float(float(uline[1])/float(0xFFFFFFFF))
                self.Blogger.info("Received NTP time seconds (float): " + "{:.9f}".format(self.ntp_sec_float_recv))
                self.counter3_recv=int(uline[2].split("recv counter is: ")[1])
                self.Blogger.info("Counter3 value at received NTP time : " + str(self.counter3_recv))

            elif "Last NTP update" in sline[0]:
                uline=sline[0].split("Last NTP update secs,fracs: ")
                uline=uline[1].split(",")
                self.ntp_sec_int_lastSync=int(uline[0])
                
                self.ntp_frac_int_lastSync=int(uline[1])
                self.Blogger.info("Last NTP sync time seconds (int): " + str(self.ntp_sec_int_lastSync) + ", and fractional (int): " + str(self.ntp_frac_int_lastSync))
                
                self.ntp_sec_float_lastSync=float(uline[0])+float(float(uline[1])/float(0xFFFFFFFF))
                self.Blogger.info("Last NTP sync time seconds (float): " + "{:.9f}".format(self.ntp_sec_float_lastSync))
                self.counter3_lastSync=int(uline[2].split("Counter3 last update count: ")[1])
                self.Blogger.info("Last NTP sync time, counter3 value: " + str(self.counter3_lastSync))

            elif "Send time" in sline[0]:

                uline=sline[0].split("seconds ")
                
                self.ntp_sent_time_sec_int=int(uline[1].split(" ")[0])
                uline=uline[2].split(",")
                self.ntp_sent_time_microsec_int=int(uline[0])
                uline=uline[1].split(" ")

                self.counter3_sent_time=int(uline[2])

                self.ntp_sent_time_fsec=float(self.ntp_sent_time_sec_int)+float(self.ntp_sent_time_microsec_int)/1000.0/1000.0

                self.Blogger.info("Board NTP originate time seconds (float): " + "{:.9f}".format(self.ntp_sent_time_fsec))
                self.Blogger.info("Board counter3 at originate: " + str(self.counter3_sent_time))

        #self.Blogger.info("Board NTP Originate time: " + "{:.9f}".format(self.ntp_sent_time_fsec))
        #self.Blogger.info("Board NTP from Counter3 originate count: "+ "{:.9f}".format(self.C3toNTP(self.counter3_sent_time)))
        self.Blogger.info("Received NTP time seconds (float): " + "{:.9f}".format(self.ntp_sec_float_recv))
        self.Blogger.info("Board NTP from Counter3 receive count: "+ "{:.9f}".format(self.C3toNTP(self.counter3_recv)))
        
        self.hostNTP=self.NTPresponse.tx_timestamp+self.NTPresponse.offset
        print "{:.9f}".format(self.hostNTP)
        self.Blogger.info("Host UTC time (includes offset) from NTP at <?t> was: " + "{:.9f}".format(self.NTPtoUTC(self.hostNTP)))
        self.NTPresponse=ntpc.request(ntpServerIP)
        
        self.Blogger.info("Current UTC time from NTP is (includes offset): " + "{:.9f}".format(self.NTPtoUTC(self.NTPresponse.tx_timestamp+self.NTPresponse.offset)))

        

            #***OVERFLOW NOT YET IMPLEMENTED***#


    def getNTPtime(self,updateOffset_flag):
        self.Blogger.info("Getting time update.")
        
        self.serPort.writelines("?t\r\n")
        self.NTPresponse=ntpc.request(ntpServerIP)
        time.sleep(.1)  #wait for NTP server to respond
        serial_data_read=self.serRead()
        self.parseTime(serial_data_read)
        if updateOffset_flag==True:
            self.lastSyncOffset=self.offset_seconds
        recv_ntp_from_counter3=float(self.counter3_recv-self.counter3_lastSync)/100000.0+self.ntp_sec_float_lastSync#+self.lastSyncOffset
        print str(float(self.counter3_recv-self.counter3_lastSync))
        self.Blogger.info("Received time from counter 3: " + "{:.9f}".format(recv_ntp_from_counter3))
        recv_board_ntp=self.ntp_sec_float_recv#+self.lastSyncOffset
        self.Blogger.info("Received time from board NTP: " + "{:.9f}".format(recv_board_ntp))


        #[t_offset, counter_base, ntp_base]
    def __init__(self, SerPortNum,mainLogger):
        self.flip_thresh=True       #this is True for key-on low-to-high transitions (i.e., in Peanut the First)


        def parse_channel_name(serDat,chan):
            for serLine in serDat:
                if "Channel" in serLine[0]:
                    chanName=serLine[0].split("name ")[1]
                    self.Blogger.info("Board " + str(self.boardID) + ", Channel " + str(chan) + " has name " + chanName)
                    return chanName
                
        def parse_channel_thresholds(serDat):
            
            for serLine in serDat:
                if "thresholds" in serLine[0]:  #check to make sure it's a (high/low) thres, and not a min/max
                    lineSplit=serLine[0].split(" ")
                    chanNum=int(lineSplit[1])
                    
                    self.ch_thresh_off[chanNum]=int(lineSplit[7])
                    self.ch_thresh_on[chanNum]=int(lineSplit[4])
                    self.ch_state[chanNum]=False^self.flip_thresh
                    
                    

                elif "max" in serLine[0]:
                    lineSplit=serLine[0].split(" ")
                    chanNum=int(lineSplit[1])
                    self.ch_min_val[chanNum]=int(lineSplit[4])
                    self.ch_max_val[chanNum]=int(lineSplit[7])
            try:
                self.Blogger.info("Channel " +str(chanNum)+ " off threshold: " + str(self.ch_thresh_off))
                self.Blogger.info("Channel " +str(chanNum)+ " on threshold: " + str(self.ch_thresh_on))
                self.Blogger.info("Channel " +str(chanNum)+ " min value: " + str(self.ch_min_val))
                self.Blogger.info("Channel " +str(chanNum)+ " max value: " + str(self.ch_max_val))
                self.chMin=np.array(self.ch_min_val.values())
                self.chMax=np.array(self.ch_max_val.values())
                self.chON=np.array(self.ch_thresh_on.values())
                self.chOFF=np.array(self.ch_thresh_off.values())
            except:
                pass

        self.SerPortNum=SerPortNum
        
        serSleepTime=0.05
        
        try:
            self.serPort=serial.Serial(SerPortNum, writeTimeout=1, timeout=serial_timeout)
            mainLogger.info("Serial port" + str(SerPortNum) +" opened.")
        except:
            mainLogger.error("Serial Port" + str(SerPortNum) +" could not be opened!")
            print "Serial port "+str(SerPortNum) +"  could not be opened"
            Closing(self)

    
        try:
            self.serPort.writelines("NSd\r\n")
            serial_data_read=self.serRead()
            self.serPort.writelines("!A\r\n")
            serial_data_read=self.serRead()
        except:
            mainLogger.error("Serial Port" + str(SerPortNum) +" could not be written to!")
            Closing(self)

        
        for s in serial_data_read:
            if "Current" in s[0]:
                self.boardID=int(s[0].split("Current addr is:\t")[1].split("\r\n")[0])
                mainLogger.info("Serial Port " + SerPortNum + " has board ID: " + str(self.boardID))
        
        self.Blogger=logging.getLogger("Board_"+str(self.boardID)+"_Logger")
        self.Blogger.setLevel(logging.DEBUG)
        self.Blogger.addHandler(fh)
        self.Blogger.addHandler(ch)
        self.Blogger.propagate = False

        self.channelNames={}
        self.ch_thresh_off={}
        self.ch_thresh_on={}
        self.ch_max_val={}
        self.ch_min_val={}
        self.ch_state={}
        self.MIDI_keyVal={}
        
        for chan in range(0,4):
            self.serPort.writelines("Sa"+ str(chan) +"\r\n")    #get channel names (as strings)
            serial_data_read=self.serRead()
            chanName=parse_channel_name(serial_data_read,chan)
            self.channelNames[chan]= chanName       #adding new channelName to dict
            try:
                self.MIDI_keyVal[chan]=int(chanName)
            except:
                self.MIDI_keyVal[chan]=self.boardID*4+chan
                self.Blogger.warn("Channel name is non-numeric, assigning value of: " + str(self.MIDI_keyVal[chan]))

        
        
        self.serPort.writelines("kC\r\n")                       #get each key threshold
        serial_data_read=self.serRead()
        parse_channel_thresholds(serial_data_read)
        while len(self.ch_thresh_off)<4:
            serial_data_read=self.serRead()
            parse_channel_thresholds(serial_data_read)
            self.Blogger.warn("Channel thresholds not found on first pass: " + str(self.ch_thresh_off) + " and " + str(self.ch_thresh_on))
        print self.ch_thresh_on
        print self.ch_thresh_off
        
        self.serPort.writelines("Ni\r\n")
        time.sleep(.1)
        serial_data_read=self.serRead()
        

        for s in serial_data_read:
            if "IP stored: " in s[0]:
                self.IPaddr=s[0].split("IP stored: ")[1].split("\r\n")[0]
                self.Blogger.info("IP address is: " + self.IPaddr)
            elif "IP : " in s[0]:
                self.IPaddr=s[0].split("IP : ")[1].split("\r\n")[0]
                self.Blogger.info("IP address is: " + self.IPaddr)
        print "Would have gotten IP above this!"
        self.serPort.writelines("??\r\n")
        self.serPort.writelines("?c\r\n")
        serial_data_read=self.serRead()
        
        

        

        #Blink LEDs so that board is visible at startup
        while(serSleepTime>0.01):
            for ledCount in range(8):

                self.serPort.writelines("Sl"+str(ledCount)+",1\r\n")
                time.sleep(serSleepTime)
                self.serPort.writelines("Sl"+str(ledCount)+",0\r\n")

            serSleepTime=serSleepTime-0.02              
            serial_data_read=self.serRead()

        
        #Set LEDs to reflect board ID (this is not yet an internal board ID)
        #no checking is done on the internal board ID or IP address yet

        for ledCount in range(8):
                if (((2**ledCount)&self.boardID)>0):
                    self.serPort.writelines("Sl"+str(ledCount)+",1\r\n")
                else:
                    self.serPort.writelines("Sl"+str(ledCount)+",0\r\n")
                
        #This would be a good place to read in a setup script and execute it for each board
        #Then run a check to ensure that all LED-receiver pairs are working

        serial_data_read=self.serRead()
        

        self.Blogger.info("Enabling Networking")

        self.serPort.writelines("NE\r\n")
        serial_data_read=self.serRead()
                

        self.Blogger.info("Sending Ping to "+self.IPaddr+" confirm networking is enabled")

        ret=subprocess.call("ping -c 1 %s" % self.IPaddr, shell=True,stdout=open('/dev/null', 'w'),stderr=subprocess.STDOUT)
        if (ret>0): #error
            self.Blogger.error("Board at"+ str(SerPortNum) +" is not on the network!")
            Closing(self)   #Perhaps we should exit here or try again
        else:
            self.Blogger.info("Ping "+self.IPaddr+" successful, networking enabled!")
        

        # try:
        #   self.Blogger.info("Querying DNS and switching to NTP pool")
        #   self.serPort.writelines("NP"+ntpServerIP+"\r\n")
        #   time.sleep(5)
        #   serial_data_read=self.serRead()
        # except:
        #   self.Blogger.warn("Can't reach external DNS server.")
        #   time.sleep(5)
        #   serial_data_read=self.serRead()
        # try:
        #   self.Blogger.info("Query NTP from pool")
        #   self.serPort.writelines("NN\r\n")
        #   time.sleep(0.5) #wait for NTP server to respond
        #   serial_data_read=self.serRead()
        # except:
        #   self.Blogger.warn("Can't reach External NTP server.")
        #   serial_data_read=self.serRead()
        #   time.sleep(5)
        #   serial_data_read=self.serRead()

        self.Blogger.info("Switching to local NTP IP: "+ ntpServerIP)
        self.serPort.writelines("Nn"+ntpServerIP+"\r\n")
        serial_data_read=self.serRead()
        

        self.Blogger.info("Querying local NTP server")
        self.serPort.writelines("NN\r\n")
        time.sleep(.1)  #wait for NTP server to respond
        serial_data_read=self.serRead()
        
        # time.sleep(.1)    #wait for NTP server to respond
        # serial_data_read=self.serRead()
        # 

        self.Blogger.info("Getting time update.")
        
        self.getNTPtime(True)
        # self.serPort.writelines("?t\r\n")
        # self.NTPresponse=ntpc.request(ntpServerIP)
        # time.sleep(.1)    #wait for NTP server to respond
        # serial_data_read=self.serRead()
        # self.parseTime(serial_data_read)
        # self.lastSyncOffset=self.offset_seconds
        # recv_ntp_from_counter3=float(self.counter3_recv-self.counter3_lastSync)/100000.0+self.ntp_sec_float_lastSync#+self.lastSyncOffset
        # print str(float(self.counter3_recv-self.counter3_lastSync))
        # self.Blogger.info("Received time from counter 3: " + "{:.9f}".format(recv_ntp_from_counter3))
        # recv_board_ntp=self.ntp_sec_float_recv#+self.lastSyncOffset
        # self.Blogger.info("Received time from board NTP: " + "{:.9f}".format(recv_board_ntp))
        
        self.Blogger.info("Initializing data stream socket on board")
        self.serPort.writelines("NSt\r\n")
        self.Blogger.info("<NSt> command sent to board, initialized")
        # serial_data_read=self.serRead()
        # 
        time.sleep(.01)
        # serial_data_read=self.serRead()
        # 

        self.dst_port=9004
        self.dst_ip=self.IPaddr

        self.Blogger.info("Going to connect to socket on port: " + str(self.dst_port) + " and IP: " + self.dst_ip)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Don't wait here!!!
        self.sock.connect((self.dst_ip, self.dst_port))
        MESSAGE = "Hello, TCP World!"
        print "Sending message: ", MESSAGE
        print "Sending TCP message to IP: ", self.dst_ip
        print "Sending TCP message to port: ", self.dst_port


        serial_data_read=self.serRead()
        
        
        self.sock.send(MESSAGE)

        serial_data_read=self.serRead()
        
        #new_message=self.sock.recv(4096)
        #print new_message
        self.Blogger.info("Data link established---will return first sample then wait 1 seconds. Expect buffer over-run, this is normal while waiting.")
        self.get_sdata()
        time.sleep(1)
        
        self.Blogger.info("Initilization done on this board, ready to collect data!")
        #may not need to bind socket here, as already sent

    def norm_data(self,datrix):
        dshape=datrix.shape
        #print dshape
        if dshape[1]>4:
            norm_dat=(datrix[:,1:5]-self.chMin)/(self.chMax-self.chMin)
            self.norm_datrix=np.hstack((np.reshape(datrix[:,0],(-1,1)),norm_dat,datrix[:,5:]))

        elif dshape[1]==4:
            self.norm_datrix=(datrix-self.chMin)/(self.chMax-self.chMin)
        else:
            raise ValueError("Data normalization will fail due to matrix shape!")

        return self.norm_datrix

    def get_sdata(self):    #getSerial data from tcp port
        global adat


        new_message=self.sock.recv(60000)
        mlen=len(new_message)
        
        temp_list=list(unpack('iiiiI',new_message[0:20]))
        temp_list.insert(0,self.boardID)
        temp_list.append(self.NTPtoUTC(self.AddSyncOffset(self.C3toNTP(temp_list[-1]))))
        
        
        if mlen>20000:
            self.Blogger.warn("Message length is high (data corruption possible): " + str(mlen))
            #this data can be dumped to somewhere else to make sure that we even save corrupt data)
            self.Blogger.error(str(new_message)) #this is binary data, and just a quick fix to see if it works. this should be UNPACKED first
            #XXX UNPACK XXX - need to do it the way that Av has here with the first one (above) and the rest (below)
            return #don't want to save to the .npy file b/c there is too much data, so just return after dumping to log file


        # if mlen>240:  
        #   #print str(mlen)
        #   pass
        #   #print self.ndat[0]
        # else:
        self.ndat=[temp_list]
        for i in range((mlen-20)/20):
            temp_list=list(unpack('iiiiI',new_message[20+i*20:40+i*20]))
            temp_list.insert(0,self.boardID)
            temp_list.append(self.NTPtoUTC(self.AddSyncOffset(self.C3toNTP(temp_list[-1]))))
            #self.ndat=self.ndat.append(temp_list)

#           self.ndat.append(temp_list)
            self.ndat.append(temp_list)
        

        

        try:
            #adat=np.vstack((adat,self.ndat))
            #adat=np.vstack((adat,self.ndat))
            try: 
                self.all_board_ndat.extend(self.ndat)
            except:
                self.all_board_ndat=[]
                self.all_board_ndat.extend(self.ndat)

            adat.append(self.ndat)
        except:
            #adat=self.ndat
            raise
            adat=self.ndat
            

    def save_data_tofile(self,bdata_fh):
        global adat
        #print adat
        #print adat
        #self.outfile=bdata_fh
        #np.save(bdata_fh,adat)
        np.save(bdata_fh,List2Array(adat))
        #print "Len of adat: " + str(len(adat))
        print "Len of adat: " + str(len(adat))
        #self.outfile.close()
    
    def extract_velocity(self,chan,isMin):      
        #extract velocity here
        #This does not do a robust search of previous key presses, look-back should be tuned for piano gestures (i.e., tradeoff between slow gestures and )
        #If polarity is swapped, changes may be needed (-1*val)
        PLOT_ON=True#TRUE           #Debug, show plot
        SMOOTHING_COEF=1000     #0 is no smoothing, >0 smoothing (default=10)
        LOOK_BACK_SAMPLES=100   #Window size for velocity estimate (default=100) #SHOULD BE 200???
        NORM_DISTANCE=100       #100mm from released to pressed [1..0]
        self.recent_dat=self.norm_data(List2Array(self.all_board_ndat[-LOOK_BACK_SAMPLES:]))
        
        pos_csp=cspline(self.recent_dat[:,chan],SMOOTHING_COEF) #spline of position data
        vel=np.diff(pos_csp,n=1)                                #derivative (velocity) of spline
        vel_csp=cspline(vel,SMOOTHING_COEF)                 #spline of velocity data
        accel=np.diff(vel_csp,n=1)                          #derivative (acceleration) of spline
        if isMin:#Find minimum 
            #extreme_vel=np.min(vel)        #search
            ex_vel_index=np.argmin(vel)     #search
            extreme_vel=vel[ex_vel_index]   #lookup is faster than search
        else:
            #extreme_vel=np.max(vel)
            ex_vel_index=np.argmax(vel)
            extreme_vel=vel[ex_vel_index]

        time_tick=self.recent_dat[ex_vel_index][6]-self.recent_dat[ex_vel_index-1][6]   #check time base

        if PLOT_ON and not(isMin):
            plt.ion()
            plt.figure(chan+50*int(isMin))
            plt.clf()

            plt.subplot(2,1,1); #position should be in mm
            plt.plot(self.recent_dat[:,6],NORM_DISTANCE*self.recent_dat[:,chan],'b') #raw posn data
            plt.plot(self.recent_dat[:,6],NORM_DISTANCE*pos_csp,'r') #splined posn data
            plt.plot(self.recent_dat[ex_vel_index,6], NORM_DISTANCE*pos_csp[ex_vel_index],'ro')
            plt.subplot(2,1,2); #velocity should be in mm/s
            plt.plot(self.recent_dat[1:,6],NORM_DISTANCE*vel/time_tick,'g') #raw velocity data
            plt.plot(self.recent_dat[ex_vel_index,6], NORM_DISTANCE*extreme_vel/time_tick,'go')
            plt.plot(self.recent_dat[1:,6],NORM_DISTANCE*vel_csp/time_tick,'k') #splined velocity data
            #plt.plot(NORM_DISTANCE*accel,'c')
            
            #plt.plot(self.dcsp)
            #plt.show(block=False)
            plt.draw()

            #print "Extreme vel is: "+str(np.abs(NORM_DISTANCE*extreme_vel/time_tick)) 
            #print "Time tick is: "+str(time_tick)
        return np.abs(NORM_DISTANCE*extreme_vel/time_tick)



    def check_thresholds(self):
        #triggers=[]
        global adat
        
        VELOCITY_MAX=127
        for chan in range(0,4):
            if len(self.ndat)>7:
                #print type(self.ndat)
                #print str(len(self.ndat))
                #print str(self.ndat)
                
                try:    #make sure ndat is a multi-dimensional array
                #could use np.greater/np.less to compare array-wise---too slow to convert into array, mutable types
                    #print type(self.ndat)
                    #print str(len(self.ndat))
                    #print str(self.ndat)
                    for element in range(0,len(self.ndat)):

                        if self.ndat[element][chan+1]<self.ch_thresh_on[chan]:  
                            if self.ch_state[chan] is False:
                                self.ch_state[chan]=True
                                
                                try:
                                    self.vel=self.extract_velocity(chan+1,False^self.flip_thresh) #XXX remove FLIP here
                                except:
                                    self.Blogger.warn("Could not extract velocity")
                                    raise

                                try:
                                    new_onset=list(self.ndat[element])              #new onset is the key onset log in the data stream
                                    new_onset[0]=255-new_onset[0]   #this should be 255-BoardID
                                    new_onset[1]=-(chan+1)*self.flip_thresh + (not self.flip_thresh) * (chan+1)         #this corresponds to which key has been pressed, negative value denotes key release
                                    new_onset[2]=self.ndat[element][chan+1] #this is the key position/value
                                    new_onset[3]=self.vel           #this is the key velocity, to be completed
                                    new_onset[4]=0                      #this element is reserved for future use
                                    adat.append(new_onset)              #log this key onset in data stream
                                except:
                                    self.Blogger.warn("Could not log adat to stream")
                                    raise
                                print "Channel Val: " + str(self.ndat[element])
                                
                                new_trigger={"chan":chan+1, "midiID":self.MIDI_keyVal[chan], "velocity":self.vel, "transition_to_on":self.ch_state[chan]^self.flip_thresh,"BoardCounter":self.ndat[element][5],"BoardUTC":self.ndat[element][6],"ChannelVal":self.ndat[element][chan+1],"NewOnset":new_onset}
                                
                                if self.flip_thresh:
                                    self.Blogger.info("Channel: "+ str(chan+1) +" is now OFF: " + str(new_trigger))
                                else:
                                    self.Blogger.info("Channel: "+ str(chan+1) +" is now ON: " + str(new_trigger))
                                
                                #print new_trigger
                                #triggers.append(new_trigger)
                                yield new_trigger

                        if self.ndat[element][chan+1]>self.ch_thresh_off[chan]:
                            if self.ch_state[chan] is True:
                                self.ch_state[chan]=False
                                

                                try:
                                    self.vel=self.extract_velocity(chan+1,True^self.flip_thresh) #XXX remove flip here?
                                except:
                                    self.Blogger.warn("Could not extract velocity")
                                    raise
                                try:
                                    new_onset=list(self.ndat[element])              #new onset is the key onset log in the data stream
                                    new_onset[0]=255-new_onset[0]   #this should be 255-BoardID
                                    new_onset[1]=-(chan+1)* (not self.flip_thresh) +  self.flip_thresh * (chan+1)   #this corresponds to which key has been pressed
                                    new_onset[2]=self.ndat[element][chan+1] #this is the key position/value
                                    new_onset[3]=self.vel           #this is the key velocity, to be completed
                                    new_onset[4]=0                      #this element is reserved for future use
                                    adat.append(new_onset)              #log this key release in data stream
                                except:
                                    print "Could not log adat to stream"
                                    raise
                                print "Channel Val: " + str(self.ndat[element])
                                new_trigger={"chan":chan+1, "midiID":self.MIDI_keyVal[chan], "velocity":self.vel, "transition_to_on":self.ch_state[chan]^self.flip_thresh,"BoardCounter":self.ndat[element][5],"BoardUTC":self.ndat[element][6],"ChannelVal":self.ndat[element][chan+1],"NewOnset":new_onset}

                                if self.flip_thresh:
                                    self.Blogger.info("Channel: "+ str(chan+1) +" is now ON: " + str(new_trigger))
                                else:
                                    self.Blogger.info("Channel: "+ str(chan+1) +" is now OFF: " + str(new_trigger))
                            

                                
                                #print new_trigger
                                #triggers.append(new_trigger)
                                yield new_trigger
                                
                except:
                    self.Blogger.error("Threshold check ERROR on channel: " + str(chan) + " ; ndat has length: " + str(len(self.ndat)) + " ; with ndat: " + str(self.ndat))
                    #self.Blogger.error(chan)
                    #self.Blogger.error(self.ndat)
                    #self.Blogger.error(len(self.ndat))
                    #self.Blogger.error(triggers)
                    raise
                    
            #   try:#ndat is currently just a vector
            #       print "Ndat is currently just a vector"
            #       if self.ndat[chan+1]<self.ch_thresh_on[chan]:
            #           if self.ch_state[chan] is False:
            #               self.ch_state[chan]=True
            #               self.Blogger.info("Channel: "+ str(chan) +" is now ON")
            #               triggers.append([{"chan":chan},{"midiID":self.MIDI_keyVal[chan]},{"velocity":VELOCITY_MAX}, {"transition_to_on":self.ch_state[chan]}])
                            

            #       if self.ndat[chan+1]>self.ch_thresh_off[chan]:
            #           if self.ch_state[chan] is True:
            #               self.ch_state[chan]=False
            #               self.Blogger.info("Channel: "+ str(chan) +" is now OFF")
            #               triggers.append([{"chan":chan},{"midiID":self.MIDI_keyVal[chan]},{"velocity":VELOCITY_MAX}, {"transition_to_on":self.ch_state[chan]}])
            #   #pass           

            #   except: #no data to deal with
            #       print "There's not enough data yet"
            #       #print myControl.dDat['FeedbackID']
            #       #pass

        #if len(triggers)>0:
        #   self.Blogger.info(triggers)
        #return triggers

                        
                


    def close_stream(self):
        self.sock.close()
    def close_serial_port(self):
        self.serPort.close()


class control_host:
    def __init__(self,ctrlIP,ctrlPort):
        global adat
        #adat=np.zeros(7)
        adat=[]
        self.collecting=True
        self.newBlock=False
        self.ctrl_IP=ctrlIP
        self.ctrl_port=ctrlPort
        self.blockNum=-1
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ctrl_IP,self.ctrl_port))
        print("Waiting to receive connection from experimental socket")
        self.sock.listen(1)
        self.conn,self.addr=self.sock.accept()
        print("Connection received from: " + str(self.addr))

        ###PEANUT is not really ready to start yet, should wait until end of initialization of board to send confirmation
        MESSAGE = "Peanut is so ready to start initialization!"
        print("Sending UDP message: " + MESSAGE+ " to IP: " + self.ctrl_IP + " on port " + str(self.ctrl_port))
        self.conn.send(MESSAGE)
        
        recvMsg=self.conn.recv(1024)
        print("Received message from control socket: " + recvMsg)
        #self.conn.setblocking(0)   #should return immediately from a sock.recv()


    def getMessage(self):
        global adat
        self.jDat=self.conn.recv(1024)
        #self.dDat=cPickle.loads(self.pDat)
        self.dDat=json.loads(self.jDat)
        try:
            logger.info("Received message from control socket: " + str(self.dDat['StreamDat']))
            logger.info("Received Packet from control socket:{" + str(self.dDat) + "}")
        except:
            pass
        self.fileHead=myControl.dDat['SubjectID']
        oldBlockNum=self.blockNum
        self.blockNum=myControl.dDat['BlockNum']
        self.blockID=myControl.dDat['BlockID']
        self.DataStream=self.dDat['StreamDat']
        #this is conditional on it actually being a new block!
        if (oldBlockNum != self.blockNum):
            self.newBlock=True
            
        #adat=np.vstack((adat,np.array(self.DataStream)))
        adat.append(self.DataStream)

        if self.blockID=="END":
            print "Setting self.collecting to false here"
            logger.warn("Received END of experiment block!")
            self.collecting=False

#           print ("Closing Control Socket?!?")
            self.close_sock()

    def close_sock(self):
        self.conn.close()
        self.sock.close()
#END CONTROL_HOST CLASS


def getLogFileName(out_file_head):
    out_dir='data'
    #out_file_head='XXX_'
    out_file_tail='.log'
    
    out_file_time=time.strftime("%Y-%m-%d_%H-%M-%S")

    #out_file=os.path.join(os.path.curdir,out_dir,out_file_head+'_'+out_file_tail)
    if not(os.path.isdir(os.path.join(os.path.curdir,out_dir))):
        os.mkdir(os.path.join(os.path.curdir,out_dir))
    
    logfilename=os.path.join(os.path.curdir,out_dir,out_file_head+'_'+out_file_time+out_file_tail)  
    return logfilename
    #out_file=datafilename
    #outfile_handler = open(out_file,"wb")

    

def makeDataFile(out_file_head, BlockID):
    out_dir='data'
    #out_file_head='XXX_'
    out_file_tail='_data_stream.npy'
    
    out_file_time=time.strftime("%Y-%m-%d_%H-%M-%S")

    
    #out_file=os.path.join(os.path.curdir,out_dir,out_file_head+'_Block_'+BlockID+out_file_tail)
    if not(os.path.isdir(os.path.join(os.path.curdir,out_dir))):
        os.mkdir(os.path.join(os.path.curdir,out_dir))
    datafilename=os.path.join(os.path.curdir,out_dir,out_file_head+"_Block_"+BlockID+"_"+out_file_time+out_file_tail)   
    out_file=datafilename
    outfile_handler = open(out_file,"wb")

    return outfile_handler


import datetime as dt

class MyFormatter(logging.Formatter):
    converter=dt.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


myControl=control_host("",4999) #bind to port 4999, allow external connections
myControl.getMessage()
#myControl.close_sock()
myControl.conn.setblocking(0)   #should return immediately from a sock.recv()
out_file_head=myControl.fileHead


logger=logging.getLogger('Main_Logger')
logger.setLevel(logging.DEBUG)
#logfilename=os.path.join(os.path.curdir,out_dir,out_file_head+'_'+out_file_time+".log")
logfilename=getLogFileName(out_file_head)
fh=logging.FileHandler(logfilename)
fh.setLevel(logging.DEBUG)
ch=logging.StreamHandler()
ch.setLevel(logging.DEBUG)


#formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = MyFormatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d,%H:%M:%S.%f')
formatter.datefmt='%Y-%m-%d,%H:%M:%S--%s.%f'
#formatter.converter=time.gmtime
#formatter.datefmt='%s'
#formatter=logging.Formatter('%(time.mktime(time.gmtime())+2208988800)i - %(time.clock())s - %(name)s - %(levelname)s - %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)
logger.propagate =False

logger.info('Logger initialized, file: ' + logfilename)
logger.info('Day/time: ' + time.asctime())

logger.info(myControl.dDat)

ntpc=ntplib.NTPClient()
logger.info("Requesting ntp time from server: " + ntpServerIP)
ntpcheck=1
while (ntpcheck==1):

    try:
        response=ntpc.request(ntpServerIP)
        logger.info("NTP time is: " + "{:.9f}".format(response.tx_timestamp))
        #logger.info("NTP time is: " + str(response.tx_timestamp))
        logger.info("UTC time is: " +"{:.9f}".format(response.tx_timestamp-float(2208988800)))
        #logger.info("UTC time is: " + str(response.tx_timestamp-float(2208988800)))
        ntpcheck=0
    except:
        logger.error("NTP server is offline, will try to bring online")
        
        command=['sudo' , 'service' , 'ntp', 'start']
        coutput=subprocess.call(command, shell=False)
        time.sleep(.1)


myDevs=glob.glob("/dev/ttyACM*")    #get all ACM serial devices 
logger.info ("Boards found at: " + str(myDevs))
myBoards={}

#for devIndex, eachDev in enumerate(myDevs):
for myDev in myDevs:
    myBoards[myDev]=MyBoard(myDev,logger)   #this creates a dictionary: key pair of /dev/ACM# (myDev) strings with the myBoard class


midi_port_list=mido.get_output_names()
logger.info(midi_port_list)
myMIDIport=""
for mport in midi_port_list:
    if "Bluethner" in mport:    #look for Bluethner synth
        myMIDIport=mport
        break
if myMIDIport =="":         #try fluid synth's midi port if Bluethner isn't there
    for mport in midi_port_list:
        if "Synth" in mport:
            myMIDIport=mport
            break
if myMIDIport =="":         #try the default if nothing else seems to work
    myMIDIport=midi_port_list[0]
logger.info("Using MIDI port: " + str(myMIDIport))

try:
    midi_port=mido.open_output(myMIDIport)
except:
    print "Could not open MIDI port"
    raise

collecting = True

currentBlock=myControl.blockID
outfile=makeDataFile(out_file_head,currentBlock)

MESSAGE = "Peanut is so ready to start!"
print("Sending UDP message: " + MESSAGE+ " to IP: " + myControl.ctrl_IP + " on port " + str(myControl.ctrl_port))
myControl.conn.send(MESSAGE)

atexit.register(Closing,myBoards=myBoards) #setup to close the boards at exit if there is a failure (should remove the necessity to reboot devices after ctrl-c

while (collecting==True):
    try:    
        #new_message=sock.recv(4096)
        for devName in myBoards:
            if myBoards[devName].ndat>0: #ensures that we don't try to work with data that we don't have (i.e., when we have bad data)
                myBoards[devName].get_sdata()   #stacks self.ndat array
                #new_triggers=myBoards[devName].check_thresholds()
                for trig in myBoards[devName].check_thresholds():
    
                    
                    if myControl.dDat['FeedbackID']=="MIDI":
                        #for trig in new_triggers:
                        #logger.info("Sending MIDI Messages: ")
                        midi_msg=mido.Message('note_on' if trig["transition_to_on"] else 'note_off',note=trig["midiID"], velocity=scale_vel_to_midi(trig["velocity"]))
                        try:
                            
                            #midi_msg=mido.Message('note_on' if trig["transition_to_on"] else 'note_off',note=trig["midiID"], velocity=scale_vel_to_midi(trig["velocity"]))
                            midi_port.send(midi_msg)
                            logger.info("MIDI message sent: " + str(midi_msg))
    
    
                            #msg=mido.Message('note_on',note=key_dict[id])
                            #new_trigger=[{"chan":chan},{"midiID":self.MIDI_keyVal[chan]},{"velocity":VELOCITY_MAX}, {"transition_to_on":self.ch_state[chan]}]
                        except:
                            logger.error("MIDI isn't working, trying to send "+ str(midi_msg))
                            raise
                    else:
                        #no new triggers, don't do anything
                        pass
        #myboard.get_sdata()

        #iterate over multiple boards here
    

        current_block=myControl.blockID
        try:
            myControl.getMessage()

            if myControl.dDat['FeedbackID']=="TIME_SYNC":
                for devName in myBoards:
                    myBoards[devName].getNTPtime(False) #get NTP time by sending <?t> to each board, don't update offset
                    #TimeStream=np.array([128,myBoards[devName].NTPtoUTC(myBoards[devName].hostNTP),myBoards[devName].NTPtoUTC(myBoards[devName].ntp_sec_float_recv),myBoards[devName].offset_seconds,myBoards[devName].counter3_recv,myBoards[devName].NTPtoUTC(myBoards[devName].ntp_sec_float_lastSync),myBoards[devName].lastSyncOffset])
                    TimeStream=[128+myBoards[devName].boardID,myBoards[devName].NTPtoUTC(myBoards[devName].ntp_sec_float_recv),myBoards[devName].offset_seconds,myBoards[devName].counter3_recv,myBoards[devName].NTPtoUTC(myBoards[devName].ntp_sec_float_lastSync),myBoards[devName].lastSyncOffset,myBoards[devName].NTPtoUTC(myBoards[devName].hostNTP)]
                    #adat=np.vstack((adat,np.array(TimeStream)))
                    adat.append(TimeStream)

            ###***have to continue converting to dicts here
            ###this will have to be put into a loop over all boards
            # myboard.getNTPtime(False) #get NTP time by sending <?t> to each board, don't update offset
            # TimeStream=np.array([128,myboard.NTPtoUTC(myboard.hostNTP),myboard.NTPtoUTC(myboard.ntp_sec_float_recv),myboard.offset_seconds,myboard.counter3_recv,myboard.NTPtoUTC(myboard.ntp_sec_float_lastSync),myboard.lastSyncOffset])
            # adat=np.vstack((adat,np.array(TimeStream)))
            ###this will have to be put into a loop over all boards

            if myControl.collecting==False:
                logger.info("Collecting finished, Saving Block: " + current_block)
                #print adat

                np.save(outfile,List2Array(adat))

                print "Len of adat: " + str(len(adat))
                #adat=np.zeros(7)
                
                outfile.close()
                logger.info("Closed file for block: " + current_block)
                logger.warn("Finished collecting, will now close")
                collecting=False


            elif myControl.newBlock==True:
                logger.info("New block tirggered, Saving Block: " + current_block)
                #print adat
                np.save(outfile,List2Array(adat))

                print "Len of adat: " + str(len(adat))
                #adat=np.zeros(7)
                adat=[]
                outfile.close()
                logger.info("Closed file for block: " + current_block)

                
                outfile=makeDataFile(out_file_head,myControl.blockID)
                logger.info("Opened file for saving new block: " + myControl.blockID)
                myControl.newBlock=False

        except:
#           print "No New Message"
            #This is a pass-through exception as we are expecting an exception unless there's a new message
            pass

        

    except:
        #raise #commented out to make sure that we can exit cleanly
        current_block=myControl.blockID
        logger.info("Saving Block (exception): " + current_block)
        #print adat
        #self.outfile=bdata_fh
        #np.save(bdata_fh,adat)
        np.save(outfile,List2Array(adat))
        #print "Len of adat: " + str(len(adat))
        print "Len of adat: " + str(len(adat))
        
        outfile.close()
        logger.info("Closed file for block: " + current_block)
        logger.warn("Finished collecting, will now close")

        print "Closing! Exception reached."

        myControl.close_sock()
        #Closing(myboard)
        Closing(myBoards)
        #raise
        try:
            midi_port.panic()
            midi_port.close()
            logger.warn("Closed MIDI port")
        except:
            logger.warn("No MIDI port to close")
        #raise

        for hand in list(logger.handlers):
            try:
                logger.warn("Closing Logger handler: " + str(hand))
                hand.close()
                logger.removeHandler(hand)
            except:
                print "Had trouble closing logger handler: " + str(hand)

        sys.exit()
        print "Should never reach here!"

print "Closing! Finished normally."

myControl.close_sock()
#Closing(myboard)
Closing(myBoards)
try:
    midi_port.panic()
    midi_port.close()
    logger.warn("Closed MIDI port")
except:
    logger.warn("No MIDI port to close")


for hand in list(logger.handlers):
    try:
        logger.warn("Closing Logger handler: " + str(hand))
        hand.close()
        logger.removeHandler(hand)
    except:
        print "Had trouble closing logger handler: " + str(hand)


sys.exit()
print "Should never reach here!"
#   except:
#           print "no new Block"

            # plt.subplot(221)
            # plt.plot(adat[-5000:,0],'b-')
            # plt.draw()

        # print adat
        # np.save(outfile,adat)
        # print "Len of adat: " + str(len(adat))
        # outfile.close()
        # sock.close()
        # print("Output to file: " + out_file)
        #myboard.serPort.close()



    # print adat
    # np.save(outfile,adat)
    # print "Len of adat: " + str(len(adat))
    # print "Closing!"

    # outfile.close()
    # sock.close()
    # myboard.serPort.close()
    # print("Output to file: " + out_file)
    # print "Closed!"
