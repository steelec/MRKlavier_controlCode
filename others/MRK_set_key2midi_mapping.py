import serial
import glob
import numpy as np
import sys
import time
import atexit

serial_timeout=0.01
CHECKttyACCESS=True
CALIBRATION=True

class MyBoard:
	def serRead(self):
			linelist=[]
			
			while (self.serPort.inWaiting()):
				newline=self.serPort.readlines(1)
				linelist.append(newline)
				
				if (newline[0] =="\r\n") or (newline[0]=="ARM$ \n") or (newline[0]=="ARM$ "):	
					continue #don't log blank lines, continue while loop from start
				
				#try:	#just in case logger isn't yet active, don't throw an exception
					#self.Blogger.info(newline[0])
				#except:
					pass
			return linelist

	def __init__(self, SerPortNum):
		
		def parse_channel_name(serDat,chan):
			for serLine in serDat:
				if "Channel" in serLine[0]:
					chanName=serLine[0].split("name ")[1]
					print ("Board " + str(self.boardID) + ", Channel " + str(chan) + " has name " + chanName)
					return chanName
				
		def parse_channel_thresholds(serDat):
			for serLine in serDat:
				if "thresholds" in serLine[0]:	#check to make sure it's a (high/low) thres, and not a min/max
					lineSplit=serLine[0].split(" ")
					chanNum=int(lineSplit[1])
					
					self.ch_thresh_off[chanNum]=int(lineSplit[7])
					self.ch_thresh_on[chanNum]=int(lineSplit[4])
					self.ch_state[chanNum]=False
					print self.ch_thresh_off
					print self.ch_thresh_on
				elif "min" in serLine[0]:	#or else the output just has the min and max of the signal in it
					lineSplit=serLine[0].split(" ")
					chanNum=int(lineSplit[1])
					
					self.ch_max[chanNum]=int(lineSplit[7])
					self.ch_min[chanNum]=int(lineSplit[4])
					#self.ch_state[chanNum]=False
					print self.ch_max
					print self.ch_min
					#XXX need to create a reasonable slope here to use as the maximum velocity - this should probably be standardised across keys and could be based on the rate of acuisition
					# create new function
					# for each key, calculate the slope given a 50ms time period (or so?) for going between the min and max values - could base this on a real idea of the time to push a key?


		self.SerPortNum=SerPortNum
		
		serSleepTime=0.05
		
		try:
			self.serPort=serial.Serial(SerPortNum, writeTimeout=1, timeout=serial_timeout)
			print ("Serial port" + str(SerPortNum) +" opened.")
		except:
			print ("Serial Port" + str(SerPortNum) +" could not be opened!")
			print "Serial port "+str(SerPortNum) +"  could not be opened"
			Closing(self)

	
		try:
			self.serPort.writelines("NSd\r\n")
			serial_data_read=self.serRead()
			self.serPort.writelines("!A\r\n")
			serial_data_read=self.serRead()
		except:
			print ("Serial Port" + str(SerPortNum) +" could not be written to!")
			Closing(self)

		
		for s in serial_data_read:
			if "Current" in s[0]:
				self.boardID=int(s[0].split("Current addr is:\t")[1].split("\r\n")[0])
				print ("Serial Port " + SerPortNum + " has board ID: " + str(self.boardID))
		
		self.channelNames={}
		self.ch_thresh_off={}
		self.ch_thresh_on={}
		self.ch_state={}
		self.ch_max={}
		self.ch_min={}
		self.MIDI_keyVal={}
		
		for chan in range(0,4):
			self.serPort.writelines("Sa"+ str(chan) +"\r\n")	#get channel names (as strings)
			serial_data_read=self.serRead()
			chanName=parse_channel_name(serial_data_read,chan)
			self.channelNames[chan]= chanName		#adding new channelName to dict
			try:
				self.MIDI_keyVal[chan]=int(chanName)
			except:
				self.MIDI_keyVal[chan]=self.boardID*4+chan
				print ("Channel name is non-numeric, assigning value of: " + str(self.MIDI_keyVal[chan]))


		self.serPort.writelines("kC\r\n")						#get each key threshold
		serial_data_read=self.serRead()
		parse_channel_thresholds(serial_data_read)
		while len(self.ch_thresh_off)<4:
			serial_data_read=self.serRead()
			parse_channel_thresholds(serial_data_read)
			print ("Channel thresholds not found on first pass: " + str(self.ch_thresh_off) + " and " + str(self.ch_thresh_on))
		print self.ch_thresh_on
		print self.ch_thresh_off

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
	def close_stream(self):
		self.sock.close()

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
	print "Closed! Now to exit!"

myDevs=glob.glob("/dev/ttyACM*")	#get all ACM serial devices 
myBoards={}

for myDev in myDevs:
	myBoards[myDev]=MyBoard(myDev)	#this creates a dictionary: key pair of /dev/ACM# (myDev) strings with the myBoard class

#atexit.register(Closing,myBoards=myBoards) #setup to close the boards at exit if there is a failure (should remove the necessity to reboot devices after ctrl-c

#load the key mapping
#bk2midi=np.loadtxt("../documentation/board_key_2_midi_mapping.txt",dtype=np.int)

#boardID, chan, MIDIcode
bk2midi=np.array([[ 1,  1, 58],
		  [ 1,  2, 59],
		  [ 1,  3, 60],
		  [ 1,  4, 61],
		  [ 2,  1, 62],
		  [ 2,  2, 63],
		  [ 2,  3, 64],
		  [ 2,  4, 65],
		  [ 3,  1, 66],
		  [ 3,  2, 67],
		  [ 3,  3, 68],
		  [ 3,  4, 69],
		  [ 4,  1, 70],
		  [ 4,  2, 71],
		  [ 4,  3, 72],
		  [ 4,  4, 73],
		  [ 5,  1, 74],
		  [ 5,  2, 75],
		  [ 5,  3, 76],
		  [ 5,  4, 77],
		  [ 6,  1, 78],
		  [ 6,  2, 79],
		  [ 6,  3, 80],
		  [ 6,  4, 81],
		  [ 7,  1, 82],
		  [ 7,  2, 83],
		  [ 7,  3, 84],
		  [ 7,  4, 0]])

#check if we can access all of the boards
if CHECKttyACCESS:
    print("================== Trying to access each of the boards through ttyACM* ==================")
    for key in sorted(myBoards.keys()):
	currentBoard=myBoards[key]
	currentBoard.serPort.writelines("Ni\r\n") #query network address
	time.sleep(0.05)
	print(currentBoard.serRead())
	

#tell the keys what their midi values should be
for key in sorted(myBoards.keys()): #sorted the dictionary so that we change the MIDI vals of the first one first, simply for claurity of display
    currentBoard=myBoards[key]
    thisBoardMapping=bk2midi[bk2midi[:,0]==currentBoard.boardID,:]
#    print thisBoardMapping
    print "================== Setting MIDI key values for board: " + str(currentBoard.boardID) + " =================="
    for chan in range(0,4):
	thisMIDIval=thisBoardMapping[thisBoardMapping[:,1]==chan+1,2]
	currentBoard.serPort.writelines("Sa"+ str(chan) + "," + str(thisMIDIval[0]) + "\r\n")
	print("Sa"+ str(chan) + "," + str(thisMIDIval[0]))
	time.sleep(.1)
    currentBoard.serPort.writelines("!ES0" + "\r\n") #save
    time.sleep(.1)
    currentBoard.serRead()
    if not(CALIBRATION):
	currentBoard.serPort.writelines("kC" + "\r\n")
	print(currentBoard.serRead())
    
    
print ("Boards were found at: " + str(myDevs))
print ""

if CALIBRATION: #this is when the user needs to get going with that calibration typing...
    print "Lets calibrate some key thresholds for the MIDI signal!!!"
    for key in sorted(myBoards.keys()):
	currentBoard=myBoards[key]    #calibrate
	currentBoard.serPort.writelines("kc" + "\r\n")
	time.sleep(.05)
    print "Please depress each key once in a controlled manner. You have 30s to complete the the entire keyboard."
    time.sleep(30)
    
    print "================== Thresholds for board: " + str(currentBoard.boardID) + " =================="
    currentBoard.serPort.writelines("kC" + "\r\n")
    print(currentBoard.serRead())
    time.sleep(.05)


print ("Closing all boards. Have a nice day.")
print ""
Closing(myBoards)
