import socket
import json
import cPickle
import time

sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(("127.0.0.1",4999))
message=sock.recv(1024)
print message
sock.send("Ready Peanut!")
print "Ready Peanut? Peanut Ready!"
time.sleep(0.5)



currentTime=time.time()
currentDate=time.asctime()
SubjectID="IMPRS_5min"
BlockID="SETUP"
BlockNum=0
BlockType="Baseline"
TrialID="SETUP"
TrialNum=0
TrialType="No_Stim/No_Feedback"
StimNum=0
StimID="None"
FeedbackNum=0
FeedbackID="None"
Count=0
StreamDat=[255,BlockNum,TrialNum,StimNum,FeedbackNum,Count,currentTime]

dDat={'time': currentTime,'date':currentDate,'SubjectID':SubjectID,'BlockID':BlockID,'BlockNum':BlockNum,'BlockType':BlockType,'TrialID':TrialID,'TrialNum':TrialNum,'TrialType':TrialType,'StimNum':StimNum,'StimID':StimID,'FeedbackNum':FeedbackNum,'FeedbackID':FeedbackID,'Count':Count,'StreamDat':StreamDat}
#pDat=cPickle.dumps(dDat)
jDat=json.dumps(dDat)	#alternately use JSON
sock.send(jDat)

print "Sent setup Block, waiting for reply."

message=sock.recv(1024)
print "Received init reply:"
print message
time.sleep(1)

#should make condition on successful/bad setup received from control


currentTime=time.time()
currentDate=time.asctime()
SubjectID="IMPRS_5min"
BlockID="PLAY"
BlockNum=1
BlockType="Baseline"
TrialID="Trial_1"
TrialNum=1
TrialType="No_Stim/No_Feedback"
StimNum=0
StimID="None"
FeedbackNum=0
FeedbackID="TIME_SYNC"
FeedbackID="MIDI"
Count=1
StreamDat=[255,BlockNum,TrialNum,StimNum,FeedbackNum,Count,currentTime]

dDat={'time': currentTime,'date':currentDate,'SubjectID':SubjectID,'BlockID':BlockID,'BlockNum':BlockNum,'BlockType':BlockType,'TrialID':TrialID,'TrialNum':TrialNum,'TrialType':TrialType,'StimNum':StimNum,'StimID':StimID,'FeedbackNum':FeedbackNum,'FeedbackID':FeedbackID,'Count':Count,'StreamDat':StreamDat}
#pDat=cPickle.dumps(dDat)
jDat=json.dumps(dDat)	#alternately use JSON
sock.send(jDat)

print "Sent first Block"
#***************
time.sleep(900)
#***************

#***************
time.sleep(5)
#***************
#Test End experiment
#***************
print "Sending END block"
BlockID="END"
BlockNum=3
Count =5
currentTime=time.time()
currentDate=time.asctime()
StreamDat=[255,BlockNum,TrialNum,StimNum,FeedbackNum,Count,currentTime]
dDat={'time': currentTime,'date':currentDate,'SubjectID':SubjectID,'BlockID':BlockID,'BlockNum':BlockNum,'BlockType':BlockType,'TrialID':TrialID,'TrialNum':TrialNum,'TrialType':TrialType,'StimNum':StimNum,'StimID':StimID,'FeedbackNum':FeedbackNum,'FeedbackID':FeedbackID,'Count':Count,'StreamDat':StreamDat}
#pDat=cPickle.dumps(dDat)
jDat=json.dumps(dDat)	#alternately use JSON
sock.send(jDat)

sock.close()

print "Closing!"
