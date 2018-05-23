import socket
import json
import cPickle
import time
print 'ciao piano'

def startExp(subject, sock):
	currentTime=time.time()
	currentDate=time.asctime()
	SubjectID=subject
	BlockID="START"
	BlockNum=99#task
	BlockType=""
	TrialID=""
	TrialNum=99#iteration
	
	TrialType=""
	
	StimNum= 99 #stim kind
	StimID= ""
	FeedbackNum= 99#block
	#FeedbackID="None"
	FeedbackID=""
	Count=99#trial

	StreamDat=[255,BlockNum,TrialNum,StimNum,FeedbackNum,Count,currentTime]
	dDat={'time': currentTime,'date':currentDate,'SubjectID':SubjectID,'BlockID':BlockID,'BlockNum':BlockNum,'BlockType':BlockType,'TrialID':TrialID,'TrialNum':TrialNum,'TrialType':TrialType,'StimNum':StimNum,'StimID':StimID,'FeedbackNum':FeedbackNum,'FeedbackID':FeedbackID,'Count':Count,'StreamDat':StreamDat}
	#pDat=cPickle.dumps(dDat)
	jDat=json.dumps(dDat)	#alternately use JSON
	sock.send(jDat)
    

	print "Now start!"
