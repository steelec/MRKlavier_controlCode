def writeLog(subject, split, task, blockType, trialID, iteration, kind, position,trial, sock,trial_stuff):

	import socket
	import json
	import cPickle
	import time
	#sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#sock.connect(("",4999))
	#message=sock.recv(1024)
	#print message
	#sock.send("Ready Peanut!")
	#print "Ready Peanut? Peanut Ready!"
	#time.sleep(0.5)

	currentTime=time.time()
	currentDate=time.asctime()
	
	SubjectID=subject
	BlockID=str(split)
	BlockNum=split#task
	BlockType=blockType
	TrialID=trialID
	TrialNum=iteration#iteration
	
	TrialType=""
	
	StimNum= kind #stim kind
	StimID= trial_stuff
	FeedbackNum= task#block
	#FeedbackID="None"
	FeedbackID=""
	Count=trial#trial
	
	StreamDat=[255,BlockNum,TrialNum,StimNum,FeedbackNum,Count,currentTime]

	dDat={'time': currentTime,'date':currentDate,'SubjectID':SubjectID,'BlockID':BlockID,'BlockNum':BlockNum,'BlockType':BlockType,'TrialID':TrialID,'TrialNum':TrialNum,'TrialType':TrialType,'StimNum':StimNum,'StimID':StimID,'FeedbackNum':FeedbackNum,'FeedbackID':FeedbackID,'Count':Count,'StreamDat':StreamDat}
	#pDat=cPickle.dumps(dDat)
	jDat=json.dumps(dDat)	#alternately use JSON
	sock.send(jDat)
    

	print "Sent setup Block, waiting for reply."

