#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy2 Experiment Builder (v1.81.03), Tue Aug 11 15:09:56 2015
If you publish work using this script please cite the relevant PsychoPy publications
  Peirce, JW (2007) PsychoPy - Psychophysics software in Python. Journal of Neuroscience Methods, 162(1-2), 8-13.
  Peirce, JW (2009) Generating stimuli for neuroscience using PsychoPy. Frontiers in Neuroinformatics, 2:10. doi: 10.3389/neuro.11.010.2008
"""

from __future__ import division  # so that 1/3=0.333 instead of 1/3=0
from psychopy import visual, core, data, event, logging, sound, gui
from psychopy.constants import *  # things like STARTED, FINISHED
import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import sin, cos, tan, log, log10, pi, average, sqrt, std, deg2rad, rad2deg, linspace, asarray
from numpy.random import random, randint, normal, shuffle
import os  # handy system and path functions

#piano host stuff
import socket
import json
import cPickle
import time
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.connect(("",4999))
message=sock.recv(1024)
print message
sock.send("Ready Peanut!")
print "Ready Peanut? Peanut Ready!"
time.sleep(0.5)

import start_piano
import end_piano
import write_to_piano

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# Store info about the experiment session
expName = 'motor_recursion'  # from the Builder filename that created this script
expInfo = {'participant':'', 'session':'001'}
dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False: core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = _thisDir + os.sep + 'data/%s_%s_%s' %(expInfo['participant'], expName, expInfo['date'])

#store variables to PIANO
subject = expInfo['participant']
#blockID = 'I1'
#task=1 #1 iteration, 2 recursion 3 similarity
blockType = expName
position = 1 #position of block (session) in the testing day [1,2,3 (day1) 4,5,6 (day2)]

#start PIANO initialization
start_piano.startExp(subject, sock)


# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=None,
    savePickle=True, saveWideText=True,
    dataFileName=filename)
#save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

endExpNow = False  # flag for 'escape' or other condition => quit the exp

# Start Code - component code to be run before the window creation

# Setup the Window
win = visual.Window(size=(1280, 800), fullscr=True, screen=0, allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    )
# store frame rate of monitor if we can measure it successfully
expInfo['frameRate']=win.getActualFrameRate()
if expInfo['frameRate']!=None:
    frameDur = 1.0/round(expInfo['frameRate'])
else:
    frameDur = 1.0/60.0 # couldn't get a reliable measure so guess

# Initialize components for Routine "Instructions"
InstructionsClock = core.Clock()
Instructions_c = visual.TextStim(win=win, ori=0, name='Instructions_c',
    text='Instructions\n\nIn this experiment you will be presented with sequences of finger movements on a keyboard.\nYou will be exposed to sequence 1 and 2.\nDuring the first 2 sequences, please pay attention to each finger movement and try to reproduce it in the keyboard.\nPlease use the correct fingers for each movement, as denoted by the color circles matching the color of your fingers.\n\nAfter the first 2 sequences, there will be a "response phase".\nDuring the response phase you will execute the correct continuation of the first two sequences, i.e., the sequence number 3.\n\nPress space key if you are ready to start.',    font='Arial',
    pos=[0, 0], height=0.05, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "trialType"
trialTypeClock = core.Clock()
trialType_img = visual.TextStim(win=win, ori=0, name='trialType_img',
    text='default text',    font=u'Arial',
    pos=[0, 0], height=0.3, wrapWidth=None,
    color=u'white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "iteration1_2"
iteration1_2Clock = core.Clock()
it1_pause_4 = visual.ImageStim(win=win, name='it1_pause_4',
    image='stimuli_refs/K0F0.jpeg', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
it1_key11_c_4 = visual.ImageStim(win=win, name='it1_key11_c_4',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
it1_key21_c_4 = visual.ImageStim(win=win, name='it1_key21_c_4',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
it1_key31_c_4 = visual.ImageStim(win=win, name='it1_key31_c_4',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
metronome_c3_4 = sound.Sound('stimuli_refs/metronome_22050.wav', secs=11.5)
metronome_c3_4.setVolume(1)

# Initialize components for Routine "iteration1"
iteration1Clock = core.Clock()
it1_key1_c = visual.ImageStim(win=win, name='it1_key1_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
metronome_c1 = sound.Sound('stimuli_refs/metronome_22050.wav', secs=11.5)
metronome_c1.setVolume(1)

# Initialize components for Routine "iteration3"
iteration3Clock = core.Clock()
it3_pause = visual.ImageStim(win=win, name='it3_pause',
    image='stimuli_refs/K0F0.jpeg', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
it3_key11_c = visual.ImageStim(win=win, name='it3_key11_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
it3_key12_c = visual.ImageStim(win=win, name='it3_key12_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
it3_key13_c = visual.ImageStim(win=win, name='it3_key13_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
it3_key21_c = visual.ImageStim(win=win, name='it3_key21_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-4.0)
it3_key22_c = visual.ImageStim(win=win, name='it3_key22_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-5.0)
it3_key23_c = visual.ImageStim(win=win, name='it3_key23_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-6.0)
it3_key31_c = visual.ImageStim(win=win, name='it3_key31_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-7.0)
it3_key32_c = visual.ImageStim(win=win, name='it3_key32_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-8.0)
it3_key33_c = visual.ImageStim(win=win, name='it3_key33_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-9.0)
metronome_c3 = sound.Sound('stimuli_refs/metronome_22050.wav', secs=11.5)
metronome_c3.setVolume(1)

# Initialize components for Routine "cross1"
cross1Clock = core.Clock()
crosshair1 = visual.ImageStim(win=win, name='crosshair1',
    image=u'stimuli_refs/crosshair.png', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)

# Initialize components for Routine "iteration2_2"
iteration2_2Clock = core.Clock()
it2_pause_3 = visual.ImageStim(win=win, name='it2_pause_3',
    image='stimuli_refs/K0F0.jpeg', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
it2_key11_c_3 = visual.ImageStim(win=win, name='it2_key11_c_3',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
it2_key12_c_3 = visual.ImageStim(win=win, name='it2_key12_c_3',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
it2_key21_c_3 = visual.ImageStim(win=win, name='it2_key21_c_3',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
it2_key22_c_3 = visual.ImageStim(win=win, name='it2_key22_c_3',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-4.0)
it2_key31_c_3 = visual.ImageStim(win=win, name='it2_key31_c_3',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-5.0)
it2_key32_c_3 = visual.ImageStim(win=win, name='it2_key32_c_3',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-6.0)
metronome_c3_3 = sound.Sound('stimuli_refs/metronome_22050.wav', secs=11.5)
metronome_c3_3.setVolume(1)

# Initialize components for Routine "iteration2"
iteration2Clock = core.Clock()
it2_pause = visual.ImageStim(win=win, name='it2_pause',
    image='stimuli_refs/K0F0.jpeg', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
it2_key1_c = visual.ImageStim(win=win, name='it2_key1_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
it2_key2_c = visual.ImageStim(win=win, name='it2_key2_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
it2_key3_c = visual.ImageStim(win=win, name='it2_key3_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
metronome_c2 = sound.Sound('stimuli_refs/metronome_22050.wav', secs=11.5)
metronome_c2.setVolume(1)

# Initialize components for Routine "iteration3"
iteration3Clock = core.Clock()
it3_pause = visual.ImageStim(win=win, name='it3_pause',
    image='stimuli_refs/K0F0.jpeg', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)
it3_key11_c = visual.ImageStim(win=win, name='it3_key11_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)
it3_key12_c = visual.ImageStim(win=win, name='it3_key12_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-2.0)
it3_key13_c = visual.ImageStim(win=win, name='it3_key13_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-3.0)
it3_key21_c = visual.ImageStim(win=win, name='it3_key21_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-4.0)
it3_key22_c = visual.ImageStim(win=win, name='it3_key22_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-5.0)
it3_key23_c = visual.ImageStim(win=win, name='it3_key23_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-6.0)
it3_key31_c = visual.ImageStim(win=win, name='it3_key31_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-7.0)
it3_key32_c = visual.ImageStim(win=win, name='it3_key32_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-8.0)
it3_key33_c = visual.ImageStim(win=win, name='it3_key33_c',
    image='sin', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-9.0)
metronome_c3 = sound.Sound('stimuli_refs/metronome_22050.wav', secs=11.5)
metronome_c3.setVolume(1)

# Initialize components for Routine "RJitter_c_2"
RJitter_c_2Clock = core.Clock()
text = visual.TextStim(win=win, ori=0, name='text',
    text=None,    font='Arial',
    pos=[0, 0], height=0.1, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Initialize components for Routine "cross2"
cross2Clock = core.Clock()
image = visual.ImageStim(win=win, name='image',
    image='stimuli_refs/crosshair.png', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=0.0)

# Initialize components for Routine "response"
responseClock = core.Clock()
metronome_c4 = sound.Sound('stimuli_refs/metronome_22050.wav', secs=11.5)
metronome_c4.setVolume(1)
it4_pause = visual.ImageStim(win=win, name='it4_pause',
    image='stimuli_refs/K0F0.jpeg', mask=None,
    ori=0, pos=[0, 0], size=None,
    color=[1,1,1], colorSpace='rgb', opacity=1,
    flipHoriz=False, flipVert=False,
    texRes=128, interpolate=True, depth=-1.0)

# Initialize components for Routine "thank_you"
thank_youClock = core.Clock()
end_xp = visual.TextStim(win=win, ori=0, name='end_xp',
    text='End of experiment\n\nThank you for your participation!',    font='Arial',
    pos=[0, 0], height=0.1, wrapWidth=None,
    color='white', colorSpace='rgb', opacity=1,
    depth=0.0)

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine 

#------Prepare to start Routine "Instructions"-------
t = 0
InstructionsClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
key_resp_3 = event.BuilderKeyResponse()  # create an object of type KeyResponse
key_resp_3.status = NOT_STARTED
# keep track of which components have finished
InstructionsComponents = []
InstructionsComponents.append(Instructions_c)
InstructionsComponents.append(key_resp_3)
for thisComponent in InstructionsComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "Instructions"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = InstructionsClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
    # update/draw components on each frame
    
    # *Instructions_c* updates
    if t >= 0.0 and Instructions_c.status == NOT_STARTED:
        # keep track of start time/frame for later
        Instructions_c.tStart = t  # underestimates by a little under one frame
        Instructions_c.frameNStart = frameN  # exact frame index
        Instructions_c.setAutoDraw(True)
    if Instructions_c.status == STARTED and (key_resp_3=='space'):
        Instructions_c.setAutoDraw(False)
    
    # *key_resp_3* updates
    if t >= 0.0 and key_resp_3.status == NOT_STARTED:
        # keep track of start time/frame for later
        key_resp_3.tStart = t  # underestimates by a little under one frame
        key_resp_3.frameNStart = frameN  # exact frame index
        key_resp_3.status = STARTED
        # keyboard checking is just starting
        key_resp_3.clock.reset()  # now t=0
        event.clearEvents(eventType='keyboard')
    if key_resp_3.status == STARTED:
        theseKeys = event.getKeys(keyList=['space'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            key_resp_3.keys = theseKeys[-1]  # just the last key pressed
            key_resp_3.rt = key_resp_3.clock.getTime()
            # a response ends the routine
            continueRoutine = False
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in InstructionsComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()
    else:  # this Routine was not non-slip safe so reset non-slip timer
        routineTimer.reset()

#-------Ending Routine "Instructions"-------
for thisComponent in InstructionsComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
# check responses
if key_resp_3.keys in ['', [], None]:  # No response was made
   key_resp_3.keys=None
# store data for thisExp (ExperimentHandler)
thisExp.addData('key_resp_3.keys',key_resp_3.keys)
if key_resp_3.keys != None:  # we had a response
    thisExp.addData('key_resp_3.rt', key_resp_3.rt)
thisExp.nextEntry()

# set up handler to look after randomisation of conditions etc
trials = data.TrialHandler(nReps=1, method='random', 
    extraInfo=expInfo, originPath=None,
    trialList=data.importConditions(u'Session1.csv'),
    seed=None, name='trials')
thisExp.addLoop(trials)  # add the loop to the experiment
thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
# abbreviate parameter names if possible (e.g. rgb=thisTrial.rgb)
if thisTrial != None:
    for paramName in thisTrial.keys():
        exec(paramName + '= thisTrial.' + paramName)


trial_count=0
split=0
    
for thisTrial in trials:
    
    #print thisTrial
    trial_stuff=str(thisTrial)
    trial_count = trial_count + 1
    trialID2=thisTrial
    currentLoop = trials
    '''
    print trial_count
    
    if trial_count<11:
        split = 0
    elif 10< trial_count<21:
        split=1
    elif 20< trial_count<31:
        split=2
    elif 30< trial_count<41:
        split=3
    elif  trial_count>40:
        split=4
        
    print trial_count, split
    
    #print trial_count, split, 'before'
    #if trial_count==2: split +=1
    #print trial_count, split, 'after1'   
    #if trial_count==3: split +=1
    #print trial_count, split, 'after2'
'''
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
    if thisTrial != None:
        for paramName in thisTrial.keys():
            exec(paramName + '= thisTrial.' + paramName)
    
    #------Prepare to start Routine "trialType"-------
    t = 0
    trialTypeClock.reset()  # clock 
    frameN = -1
    routineTimer.add(1.000000)
    # update component parameters for each repeat
    trialType_img.setText(trialType_csv)
    # keep track of which components have finished
    trialTypeComponents = []
    trialTypeComponents.append(trialType_img)
    for thisComponent in trialTypeComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "trialType"-------
    continueRoutine = True
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = trialTypeClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *trialType_img* updates
        if t >= 0.0 and trialType_img.status == NOT_STARTED:
            # keep track of start time/frame for later
            trialType_img.tStart = t  # underestimates by a little under one frame
            trialType_img.frameNStart = frameN  # exact frame index
            trialType_img.setAutoDraw(True)
        if trialType_img.status == STARTED and t >= (0.0 + (1-win.monitorFramePeriod*0.75)): #most of one frame period left
            trialType_img.setAutoDraw(False)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineTimer.reset()  # if we abort early the non-slip timer needs reset
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in trialTypeComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #-------Ending Routine "trialType"-------
    for thisComponent in trialTypeComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)

    blockID = trialType_csv
    if blockID == 'I' : task =1
    if blockID == 'R' : task =2
    if blockID == 'S' : task =3
    


    if trialType_csv =='I':
        #------Prepare to start Routine "iteration1_2"-------
        t = 0
        iteration1_2Clock.reset()  # clock 
        frameN = -1
        routineTimer.add(12.000000)
        # update component parameters for each repeat
        it1_key11_c_4.setImage(it3_key11)
        it1_key21_c_4.setImage(it3_key21)
        it1_key31_c_4.setImage(it3_key31)
        # keep track of which components have finished
        iteration1_2Components = []
        iteration1_2Components.append(it1_pause_4)
        iteration1_2Components.append(it1_key11_c_4)
        iteration1_2Components.append(it1_key21_c_4)
        iteration1_2Components.append(it1_key31_c_4)
        iteration1_2Components.append(metronome_c3_4)
        for thisComponent in iteration1_2Components:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
            
        
        #-------Start Routine "iteration1_2"-------
        continueRoutine = True
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = iteration1_2Clock.getTime()
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *it1_pause_4* updates
            if t >= 0 and it1_pause_4.status == NOT_STARTED:
                # keep track of start time/frame for later
                it1_pause_4.tStart = t  # underestimates by a little under one frame
                it1_pause_4.frameNStart = frameN  # exact frame index
                it1_pause_4.setAutoDraw(True)
                
                #ITERATION1_PIANO
            
                trial_ID = str(trialID2['Direction']) + '_' +str(trialID2['ToneDistance'])
                if trial_ID =='A_1':kind=1
                if trial_ID =='A_2':kind=2
                if trial_ID =='D_1':kind=3
                if trial_ID =='D_2':kind=4
                
                trial= trial_count
                iteration=1
                
                #print trialType
                #write_to_piano.writeLog(subject, blockID,task, blockType, trial_ID, iteration, kind, position,trial, sock,trial_stuff)
                #write_to_piano.writeLog(subject,split, task, blockType, trial_ID, iteration, kind, position,trial, sock,trial_stuff)
                
            if it1_pause_4.status == STARTED and t >= (0 + (12-win.monitorFramePeriod*0.75)): #most of one frame period left
                it1_pause_4.setAutoDraw(False)
            
            # *it1_key11_c_4* updates
            if t >= 0.15 and it1_key11_c_4.status == NOT_STARTED:
                # keep track of start time/frame for later
                it1_key11_c_4.tStart = t  # underestimates by a little under one frame
                it1_key11_c_4.frameNStart = frameN  # exact frame index
                it1_key11_c_4.setAutoDraw(True)
            if it1_key11_c_4.status == STARTED and t >= (0.15 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it1_key11_c_4.setAutoDraw(False)
            
            # *it1_key21_c_4* updates
            if t >= 4.15 and it1_key21_c_4.status == NOT_STARTED:
                # keep track of start time/frame for later
                it1_key21_c_4.tStart = t  # underestimates by a little under one frame
                it1_key21_c_4.frameNStart = frameN  # exact frame index
                it1_key21_c_4.setAutoDraw(True)
            if it1_key21_c_4.status == STARTED and t >= (4.15 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it1_key21_c_4.setAutoDraw(False)
            
            # *it1_key31_c_4* updates
            if t >= 8.15 and it1_key31_c_4.status == NOT_STARTED:
                # keep track of start time/frame for later
                it1_key31_c_4.tStart = t  # underestimates by a little under one frame
                it1_key31_c_4.frameNStart = frameN  # exact frame index
                it1_key31_c_4.setAutoDraw(True)
            if it1_key31_c_4.status == STARTED and t >= (8.15 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it1_key31_c_4.setAutoDraw(False)
            # start/stop metronome_c3_4
            if t >= 0.0 and metronome_c3_4.status == NOT_STARTED:
                # keep track of start time/frame for later
                metronome_c3_4.tStart = t  # underestimates by a little under one frame
                metronome_c3_4.frameNStart = frameN  # exact frame index
                metronome_c3_4.play()  # start the sound (it finishes automatically)
            if metronome_c3_4.status == STARTED and t >= (0.0 + (11.5-win.monitorFramePeriod*0.75)): #most of one frame period left
                metronome_c3_4.stop()  # stop the sound (if longer than duration)
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineTimer.reset()  # if we abort early the non-slip timer needs reset
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in iteration1_2Components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # check for quit (the Esc key)
            if endExpNow or event.getKeys(keyList=["escape"]):
                core.quit()
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        #-------Ending Routine "iteration1_2"-------
        for thisComponent in iteration1_2Components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
    
    if trialType_csv =='R':
        #------Prepare to start Routine "iteration1"-------
        t = 0
        iteration1Clock.reset()  # clock 
        frameN = -1
        routineTimer.add(12.000000)
        # update component parameters for each repeat
        it1_key1_c.setImage(it1_key1)
        # keep track of which components have finished
        iteration1Components = []
        iteration1Components.append(it1_key1_c)
        iteration1Components.append(metronome_c1)
        for thisComponent in iteration1Components:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        
        #-------Start Routine "iteration1"-------
        continueRoutine = True
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = iteration1Clock.getTime()
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *it1_key1_c* updates
            if t >= 0.0 and it1_key1_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it1_key1_c.tStart = t  # underestimates by a little under one frame
                it1_key1_c.frameNStart = frameN  # exact frame index
                it1_key1_c.setAutoDraw(True)
                
                trial_ID = str(trialID2['Direction']) + '_' +str(trialID2['ToneDistance'])
                if trial_ID =='A_1':kind=1
                if trial_ID =='A_2':kind=2
                if trial_ID =='D_1':kind=3
                if trial_ID =='D_2':kind=4
                
                trial= trial_count
                iteration=1
                
                #print trialType
                #write_to_piano.writeLog(subject,split, task, blockType, trial_ID, iteration, kind, position,trial, sock,trial_stuff)
                
            if it1_key1_c.status == STARTED and t >= (0.0 + (12-win.monitorFramePeriod*0.75)): #most of one frame period left
                it1_key1_c.setAutoDraw(False)
            # start/stop metronome_c1
            if t >= 0.0 and metronome_c1.status == NOT_STARTED:
                # keep track of start time/frame for later
                metronome_c1.tStart = t  # underestimates by a little under one frame
                metronome_c1.frameNStart = frameN  # exact frame index
                metronome_c1.play()  # start the sound (it finishes automatically)
            if metronome_c1.status == STARTED and t >= (0.0 + (11.5-win.monitorFramePeriod*0.75)): #most of one frame period left
                metronome_c1.stop()  # stop the sound (if longer than duration)
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineTimer.reset()  # if we abort early the non-slip timer needs reset
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in iteration1Components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # check for quit (the Esc key)
            if endExpNow or event.getKeys(keyList=["escape"]):
                core.quit()
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        #-------Ending Routine "iteration1"-------
        for thisComponent in iteration1Components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
    
    if trialType_csv =='S':
        #------Prepare to start Routine "iteration3"-------
        t = 0
        iteration3Clock.reset()  # clock 
        frameN = -1
        routineTimer.add(12.000000)
        # update component parameters for each repeat
        it3_key11_c.setImage(it3_key11)
        it3_key12_c.setImage(it3_key12)
        it3_key13_c.setImage(it3_key13)
        it3_key21_c.setImage(it3_key21)
        it3_key22_c.setImage(it3_key22)
        it3_key23_c.setImage(it3_key23)
        it3_key31_c.setImage(it3_key31)
        it3_key32_c.setImage(it3_key32)
        it3_key33_c.setImage(it3_key33)
        # keep track of which components have finished
        iteration3Components = []
        iteration3Components.append(it3_pause)
        iteration3Components.append(it3_key11_c)
        iteration3Components.append(it3_key12_c)
        iteration3Components.append(it3_key13_c)
        iteration3Components.append(it3_key21_c)
        iteration3Components.append(it3_key22_c)
        iteration3Components.append(it3_key23_c)
        iteration3Components.append(it3_key31_c)
        iteration3Components.append(it3_key32_c)
        iteration3Components.append(it3_key33_c)
        iteration3Components.append(metronome_c3)
        for thisComponent in iteration3Components:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        
        #-------Start Routine "iteration3"-------
        continueRoutine = True
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = iteration3Clock.getTime()
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *it3_pause* updates
            if t >= 0 and it3_pause.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_pause.tStart = t  # underestimates by a little under one frame
                it3_pause.frameNStart = frameN  # exact frame index
                it3_pause.setAutoDraw(True)
                
                trial_ID = str(trialID2['Direction']) + '_' +str(trialID2['ToneDistance'])
                if trial_ID =='A_1':kind=1
                if trial_ID =='A_2':kind=2
                if trial_ID =='D_1':kind=3
                if trial_ID =='D_2':kind=4
                
                trial= trial_count
                iteration=1
                
                #print trialType
                #write_to_piano.writeLog(subject,split, task, blockType, trial_ID, iteration, kind, position,trial, sock,trial_stuff)
                
            if it3_pause.status == STARTED and t >= (0 + (12-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_pause.setAutoDraw(False)
            
            # *it3_key11_c* updates
            if t >= 0.1 and it3_key11_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key11_c.tStart = t  # underestimates by a little under one frame
                it3_key11_c.frameNStart = frameN  # exact frame index
                it3_key11_c.setAutoDraw(True)
            if it3_key11_c.status == STARTED and t >= (0.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key11_c.setAutoDraw(False)
            
            # *it3_key12_c* updates
            if t >= 1.1 and it3_key12_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key12_c.tStart = t  # underestimates by a little under one frame
                it3_key12_c.frameNStart = frameN  # exact frame index
                it3_key12_c.setAutoDraw(True)
            if it3_key12_c.status == STARTED and t >= (1.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key12_c.setAutoDraw(False)
            
            # *it3_key13_c* updates
            if t >= 2.1 and it3_key13_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key13_c.tStart = t  # underestimates by a little under one frame
                it3_key13_c.frameNStart = frameN  # exact frame index
                it3_key13_c.setAutoDraw(True)
            if it3_key13_c.status == STARTED and t >= (2.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key13_c.setAutoDraw(False)
            
            # *it3_key21_c* updates
            if t >= 4.1 and it3_key21_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key21_c.tStart = t  # underestimates by a little under one frame
                it3_key21_c.frameNStart = frameN  # exact frame index
                it3_key21_c.setAutoDraw(True)
            if it3_key21_c.status == STARTED and t >= (4.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key21_c.setAutoDraw(False)
            
            # *it3_key22_c* updates
            if t >= 5.1 and it3_key22_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key22_c.tStart = t  # underestimates by a little under one frame
                it3_key22_c.frameNStart = frameN  # exact frame index
                it3_key22_c.setAutoDraw(True)
            if it3_key22_c.status == STARTED and t >= (5.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key22_c.setAutoDraw(False)
            
            # *it3_key23_c* updates
            if t >= 6.1 and it3_key23_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key23_c.tStart = t  # underestimates by a little under one frame
                it3_key23_c.frameNStart = frameN  # exact frame index
                it3_key23_c.setAutoDraw(True)
            if it3_key23_c.status == STARTED and t >= (6.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key23_c.setAutoDraw(False)
            
            # *it3_key31_c* updates
            if t >= 8.1 and it3_key31_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key31_c.tStart = t  # underestimates by a little under one frame
                it3_key31_c.frameNStart = frameN  # exact frame index
                it3_key31_c.setAutoDraw(True)
            if it3_key31_c.status == STARTED and t >= (8.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key31_c.setAutoDraw(False)
            
            # *it3_key32_c* updates
            if t >= 9.1 and it3_key32_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key32_c.tStart = t  # underestimates by a little under one frame
                it3_key32_c.frameNStart = frameN  # exact frame index
                it3_key32_c.setAutoDraw(True)
            if it3_key32_c.status == STARTED and t >= (9.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key32_c.setAutoDraw(False)
            
            # *it3_key33_c* updates
            if t >= 10.1 and it3_key33_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key33_c.tStart = t  # underestimates by a little under one frame
                it3_key33_c.frameNStart = frameN  # exact frame index
                it3_key33_c.setAutoDraw(True)
            if it3_key33_c.status == STARTED and t >= (10.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key33_c.setAutoDraw(False)
            # start/stop metronome_c3
            if t >= 0.0 and metronome_c3.status == NOT_STARTED:
                # keep track of start time/frame for later
                metronome_c3.tStart = t  # underestimates by a little under one frame
                metronome_c3.frameNStart = frameN  # exact frame index
                metronome_c3.play()  # start the sound (it finishes automatically)
            if metronome_c3.status == STARTED and t >= (0.0 + (11.5-win.monitorFramePeriod*0.75)): #most of one frame period left
                metronome_c3.stop()  # stop the sound (if longer than duration)
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineTimer.reset()  # if we abort early the non-slip timer needs reset
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in iteration3Components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # check for quit (the Esc key)
            if endExpNow or event.getKeys(keyList=["escape"]):
                core.quit()
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        #-------Ending Routine "iteration3"-------
        for thisComponent in iteration3Components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
    
    #------Prepare to start Routine "cross1"-------
    t = 0
    cross1Clock.reset()  # clock 
    frameN = -1
    routineTimer.add(1.000000)
    # update component parameters for each repeat
    # keep track of which components have finished
    cross1Components = []
    cross1Components.append(crosshair1)
    for thisComponent in cross1Components:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "cross1"-------
    continueRoutine = True
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = cross1Clock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *crosshair1* updates
        if t >= 0.0 and crosshair1.status == NOT_STARTED:
            # keep track of start time/frame for later
            crosshair1.tStart = t  # underestimates by a little under one frame
            crosshair1.frameNStart = frameN  # exact frame index
            crosshair1.setAutoDraw(True)
        if crosshair1.status == STARTED and t >= (0.0 + (1-win.monitorFramePeriod*0.75)): #most of one frame period left
            crosshair1.setAutoDraw(False)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineTimer.reset()  # if we abort early the non-slip timer needs reset
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in cross1Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #-------Ending Routine "cross1"-------
    for thisComponent in cross1Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    
    if trialType_csv =='I':
        #------Prepare to start Routine "iteration2_2"-------
        t = 0
        iteration2_2Clock.reset()  # clock 
        frameN = -1
        routineTimer.add(12.000000)
        # update component parameters for each repeat
        it2_key11_c_3.setImage(it3_key11)
        it2_key12_c_3.setImage(it3_key12)
        it2_key21_c_3.setImage(it3_key21)
        it2_key22_c_3.setImage(it3_key22)
        it2_key31_c_3.setImage(it3_key31)
        it2_key32_c_3.setImage(it3_key32)
        # keep track of which components have finished
        iteration2_2Components = []
        iteration2_2Components.append(it2_pause_3)
        iteration2_2Components.append(it2_key11_c_3)
        iteration2_2Components.append(it2_key12_c_3)
        iteration2_2Components.append(it2_key21_c_3)
        iteration2_2Components.append(it2_key22_c_3)
        iteration2_2Components.append(it2_key31_c_3)
        iteration2_2Components.append(it2_key32_c_3)
        iteration2_2Components.append(metronome_c3_3)
        for thisComponent in iteration2_2Components:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        
        #-------Start Routine "iteration2_2"-------
        continueRoutine = True
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = iteration2_2Clock.getTime()
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *it2_pause_3* updates
            if t >= 0 and it2_pause_3.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_pause_3.tStart = t  # underestimates by a little under one frame
                it2_pause_3.frameNStart = frameN  # exact frame index
                it2_pause_3.setAutoDraw(True)
                
                #ITERATION2_PIANO
            
                trial_ID = str(trialID2['Direction']) + '_' +str(trialID2['ToneDistance'])
                if trial_ID =='A_1':kind=1
                if trial_ID =='A_2':kind=2
                if trial_ID =='D_1':kind=3
                if trial_ID =='D_2':kind=4
                
                trial= trial_count
                iteration=2
                
                #print trialType
                #write_to_piano.writeLog(subject,split, task, blockType, trial_ID, iteration, kind, position,trial, sock,trial_stuff)
                
            if it2_pause_3.status == STARTED and t >= (0 + (12-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_pause_3.setAutoDraw(False)
            
            # *it2_key11_c_3* updates
            if t >= 0.15 and it2_key11_c_3.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_key11_c_3.tStart = t  # underestimates by a little under one frame
                it2_key11_c_3.frameNStart = frameN  # exact frame index
                it2_key11_c_3.setAutoDraw(True)
            if it2_key11_c_3.status == STARTED and t >= (0.15 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_key11_c_3.setAutoDraw(False)
            
            # *it2_key12_c_3* updates
            if t >= 1.15 and it2_key12_c_3.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_key12_c_3.tStart = t  # underestimates by a little under one frame
                it2_key12_c_3.frameNStart = frameN  # exact frame index
                it2_key12_c_3.setAutoDraw(True)
            if it2_key12_c_3.status == STARTED and t >= (1.15 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_key12_c_3.setAutoDraw(False)
            
            # *it2_key21_c_3* updates
            if t >= 4.15 and it2_key21_c_3.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_key21_c_3.tStart = t  # underestimates by a little under one frame
                it2_key21_c_3.frameNStart = frameN  # exact frame index
                it2_key21_c_3.setAutoDraw(True)
            if it2_key21_c_3.status == STARTED and t >= (4.15 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_key21_c_3.setAutoDraw(False)
            
            # *it2_key22_c_3* updates
            if t >= 5.15 and it2_key22_c_3.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_key22_c_3.tStart = t  # underestimates by a little under one frame
                it2_key22_c_3.frameNStart = frameN  # exact frame index
                it2_key22_c_3.setAutoDraw(True)
            if it2_key22_c_3.status == STARTED and t >= (5.15 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_key22_c_3.setAutoDraw(False)
            
            # *it2_key31_c_3* updates
            if t >= 8.15 and it2_key31_c_3.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_key31_c_3.tStart = t  # underestimates by a little under one frame
                it2_key31_c_3.frameNStart = frameN  # exact frame index
                it2_key31_c_3.setAutoDraw(True)
            if it2_key31_c_3.status == STARTED and t >= (8.15 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_key31_c_3.setAutoDraw(False)
            
            # *it2_key32_c_3* updates
            if t >= 9.15 and it2_key32_c_3.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_key32_c_3.tStart = t  # underestimates by a little under one frame
                it2_key32_c_3.frameNStart = frameN  # exact frame index
                it2_key32_c_3.setAutoDraw(True)
            if it2_key32_c_3.status == STARTED and t >= (9.15 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_key32_c_3.setAutoDraw(False)
            # start/stop metronome_c3_3
            if t >= 0.0 and metronome_c3_3.status == NOT_STARTED:
                # keep track of start time/frame for later
                metronome_c3_3.tStart = t  # underestimates by a little under one frame
                metronome_c3_3.frameNStart = frameN  # exact frame index
                metronome_c3_3.play()  # start the sound (it finishes automatically)
            if metronome_c3_3.status == STARTED and t >= (0.0 + (11.5-win.monitorFramePeriod*0.75)): #most of one frame period left
                metronome_c3_3.stop()  # stop the sound (if longer than duration)
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineTimer.reset()  # if we abort early the non-slip timer needs reset
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in iteration2_2Components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # check for quit (the Esc key)
            if endExpNow or event.getKeys(keyList=["escape"]):
                core.quit()
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        #-------Ending Routine "iteration2_2"-------
        for thisComponent in iteration2_2Components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
    
    if trialType_csv =='R':
        #------Prepare to start Routine "iteration2"-------
        t = 0
        iteration2Clock.reset()  # clock 
        frameN = -1
        routineTimer.add(12.100000)
        # update component parameters for each repeat
        it2_key1_c.setImage(it2_key1)
        it2_key2_c.setImage(it2_key2)
        it2_key3_c.setImage(it2_key3)
        # keep track of which components have finished
        iteration2Components = []
        iteration2Components.append(it2_pause)
        iteration2Components.append(it2_key1_c)
        iteration2Components.append(it2_key2_c)
        iteration2Components.append(it2_key3_c)
        iteration2Components.append(metronome_c2)
        for thisComponent in iteration2Components:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        
        #-------Start Routine "iteration2"-------
        continueRoutine = True
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = iteration2Clock.getTime()
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *it2_pause* updates
            if t >= 0 and it2_pause.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_pause.tStart = t  # underestimates by a little under one frame
                it2_pause.frameNStart = frameN  # exact frame index
                it2_pause.setAutoDraw(True)
                
                #ITERATION2_PIANO
            
                trial_ID = str(trialID2['Direction']) + '_' +str(trialID2['ToneDistance'])
                if trial_ID =='A_1':kind=1
                if trial_ID =='A_2':kind=2
                if trial_ID =='D_1':kind=3
                if trial_ID =='D_2':kind=4
                
                trial= trial_count
                iteration=2
                
                #print trialType
                #write_to_piano.writeLog(subject,split, task, blockType, trial_ID, iteration, kind, position,trial, sock,trial_stuff)
                
            if it2_pause.status == STARTED and t >= (0 + (12.1-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_pause.setAutoDraw(False)
            
            # *it2_key1_c* updates
            if t >= 0.0 and it2_key1_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_key1_c.tStart = t  # underestimates by a little under one frame
                it2_key1_c.frameNStart = frameN  # exact frame index
                it2_key1_c.setAutoDraw(True)
            if it2_key1_c.status == STARTED and t >= (0.0 + (3-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_key1_c.setAutoDraw(False)
            
            # *it2_key2_c* updates
            if t >= 4 and it2_key2_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_key2_c.tStart = t  # underestimates by a little under one frame
                it2_key2_c.frameNStart = frameN  # exact frame index
                it2_key2_c.setAutoDraw(True)
            if it2_key2_c.status == STARTED and t >= (4 + (3-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_key2_c.setAutoDraw(False)
            
            # *it2_key3_c* updates
            if t >= 8 and it2_key3_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it2_key3_c.tStart = t  # underestimates by a little under one frame
                it2_key3_c.frameNStart = frameN  # exact frame index
                it2_key3_c.setAutoDraw(True)
            if it2_key3_c.status == STARTED and t >= (8 + (3-win.monitorFramePeriod*0.75)): #most of one frame period left
                it2_key3_c.setAutoDraw(False)
            # start/stop metronome_c2
            if t >= 0.0 and metronome_c2.status == NOT_STARTED:
                # keep track of start time/frame for later
                metronome_c2.tStart = t  # underestimates by a little under one frame
                metronome_c2.frameNStart = frameN  # exact frame index
                metronome_c2.play()  # start the sound (it finishes automatically)
            if metronome_c2.status == STARTED and t >= (0.0 + (11.5-win.monitorFramePeriod*0.75)): #most of one frame period left
                metronome_c2.stop()  # stop the sound (if longer than duration)
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineTimer.reset()  # if we abort early the non-slip timer needs reset
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in iteration2Components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # check for quit (the Esc key)
            if endExpNow or event.getKeys(keyList=["escape"]):
                core.quit()
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        #-------Ending Routine "iteration2"-------
        for thisComponent in iteration2Components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
    
    if trialType_csv =='S':
        #------Prepare to start Routine "iteration3"-------
        t = 0
        iteration3Clock.reset()  # clock 
        frameN = -1
        routineTimer.add(12.000000)
        # update component parameters for each repeat
        it3_key11_c.setImage(it3_key11)
        it3_key12_c.setImage(it3_key12)
        it3_key13_c.setImage(it3_key13)
        it3_key21_c.setImage(it3_key21)
        it3_key22_c.setImage(it3_key22)
        it3_key23_c.setImage(it3_key23)
        it3_key31_c.setImage(it3_key31)
        it3_key32_c.setImage(it3_key32)
        it3_key33_c.setImage(it3_key33)
        # keep track of which components have finished
        iteration3Components = []
        iteration3Components.append(it3_pause)
        iteration3Components.append(it3_key11_c)
        iteration3Components.append(it3_key12_c)
        iteration3Components.append(it3_key13_c)
        iteration3Components.append(it3_key21_c)
        iteration3Components.append(it3_key22_c)
        iteration3Components.append(it3_key23_c)
        iteration3Components.append(it3_key31_c)
        iteration3Components.append(it3_key32_c)
        iteration3Components.append(it3_key33_c)
        iteration3Components.append(metronome_c3)
        for thisComponent in iteration3Components:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        
        #-------Start Routine "iteration3"-------
        continueRoutine = True
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = iteration3Clock.getTime()
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *it3_pause* updates
            if t >= 0 and it3_pause.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_pause.tStart = t  # underestimates by a little under one frame
                it3_pause.frameNStart = frameN  # exact frame index
                it3_pause.setAutoDraw(True)
                
                #ITERATION2_PIANO
            
                trial_ID = str(trialID2['Direction']) + '_' +str(trialID2['ToneDistance'])
                if trial_ID =='A_1':kind=1
                if trial_ID =='A_2':kind=2
                if trial_ID =='D_1':kind=3
                if trial_ID =='D_2':kind=4
                
                trial= trial_count
                iteration=2
                
                #print trialType
               # write_to_piano.writeLog(subject,split, task, blockType, trial_ID, iteration, kind, position,trial, sock,trial_stuff)
                
            if it3_pause.status == STARTED and t >= (0 + (12-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_pause.setAutoDraw(False)
            
            # *it3_key11_c* updates
            if t >= 0.1 and it3_key11_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key11_c.tStart = t  # underestimates by a little under one frame
                it3_key11_c.frameNStart = frameN  # exact frame index
                it3_key11_c.setAutoDraw(True)
            if it3_key11_c.status == STARTED and t >= (0.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key11_c.setAutoDraw(False)
            
            # *it3_key12_c* updates
            if t >= 1.1 and it3_key12_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key12_c.tStart = t  # underestimates by a little under one frame
                it3_key12_c.frameNStart = frameN  # exact frame index
                it3_key12_c.setAutoDraw(True)
            if it3_key12_c.status == STARTED and t >= (1.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key12_c.setAutoDraw(False)
            
            # *it3_key13_c* updates
            if t >= 2.1 and it3_key13_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key13_c.tStart = t  # underestimates by a little under one frame
                it3_key13_c.frameNStart = frameN  # exact frame index
                it3_key13_c.setAutoDraw(True)
            if it3_key13_c.status == STARTED and t >= (2.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key13_c.setAutoDraw(False)
            
            # *it3_key21_c* updates
            if t >= 4.1 and it3_key21_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key21_c.tStart = t  # underestimates by a little under one frame
                it3_key21_c.frameNStart = frameN  # exact frame index
                it3_key21_c.setAutoDraw(True)
            if it3_key21_c.status == STARTED and t >= (4.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key21_c.setAutoDraw(False)
            
            # *it3_key22_c* updates
            if t >= 5.1 and it3_key22_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key22_c.tStart = t  # underestimates by a little under one frame
                it3_key22_c.frameNStart = frameN  # exact frame index
                it3_key22_c.setAutoDraw(True)
            if it3_key22_c.status == STARTED and t >= (5.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key22_c.setAutoDraw(False)
            
            # *it3_key23_c* updates
            if t >= 6.1 and it3_key23_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key23_c.tStart = t  # underestimates by a little under one frame
                it3_key23_c.frameNStart = frameN  # exact frame index
                it3_key23_c.setAutoDraw(True)
            if it3_key23_c.status == STARTED and t >= (6.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key23_c.setAutoDraw(False)
            
            # *it3_key31_c* updates
            if t >= 8.1 and it3_key31_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key31_c.tStart = t  # underestimates by a little under one frame
                it3_key31_c.frameNStart = frameN  # exact frame index
                it3_key31_c.setAutoDraw(True)
            if it3_key31_c.status == STARTED and t >= (8.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key31_c.setAutoDraw(False)
            
            # *it3_key32_c* updates
            if t >= 9.1 and it3_key32_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key32_c.tStart = t  # underestimates by a little under one frame
                it3_key32_c.frameNStart = frameN  # exact frame index
                it3_key32_c.setAutoDraw(True)
            if it3_key32_c.status == STARTED and t >= (9.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key32_c.setAutoDraw(False)
            
            # *it3_key33_c* updates
            if t >= 10.1 and it3_key33_c.status == NOT_STARTED:
                # keep track of start time/frame for later
                it3_key33_c.tStart = t  # underestimates by a little under one frame
                it3_key33_c.frameNStart = frameN  # exact frame index
                it3_key33_c.setAutoDraw(True)
            if it3_key33_c.status == STARTED and t >= (10.1 + (0.75-win.monitorFramePeriod*0.75)): #most of one frame period left
                it3_key33_c.setAutoDraw(False)
            # start/stop metronome_c3
            if t >= 0.0 and metronome_c3.status == NOT_STARTED:
                # keep track of start time/frame for later
                metronome_c3.tStart = t  # underestimates by a little under one frame
                metronome_c3.frameNStart = frameN  # exact frame index
                metronome_c3.play()  # start the sound (it finishes automatically)
            if metronome_c3.status == STARTED and t >= (0.0 + (11.5-win.monitorFramePeriod*0.75)): #most of one frame period left
                metronome_c3.stop()  # stop the sound (if longer than duration)
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineTimer.reset()  # if we abort early the non-slip timer needs reset
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in iteration3Components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # check for quit (the Esc key)
            if endExpNow or event.getKeys(keyList=["escape"]):
                core.quit()
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        #-------Ending Routine "iteration3"-------
        for thisComponent in iteration3Components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
    
    #------Prepare to start Routine "RJitter_c_2"-------
    t = 0
    RJitter_c_2Clock.reset()  # clock 
    frameN = -1
    # update component parameters for each repeat
    # keep track of which components have finished
    RJitter_c_2Components = []
    RJitter_c_2Components.append(text)
    for thisComponent in RJitter_c_2Components:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "RJitter_c_2"-------
    continueRoutine = True
    while continueRoutine:
        # get current time
        t = RJitter_c_2Clock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text* updates
        if t >= 0.0 and text.status == NOT_STARTED:
            # keep track of start time/frame for later
            text.tStart = t  # underestimates by a little under one frame
            text.frameNStart = frameN  # exact frame index
            text.setAutoDraw(True)
        if text.status == STARTED and t >= (0.0 + (RJitter-win.monitorFramePeriod*0.75)): #most of one frame period left
            text.setAutoDraw(False)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineTimer.reset()  # if we abort early the non-slip timer needs reset
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in RJitter_c_2Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
        else:  # this Routine was not non-slip safe so reset non-slip timer
            routineTimer.reset()
    
    #-------Ending Routine "RJitter_c_2"-------
    for thisComponent in RJitter_c_2Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    
    #------Prepare to start Routine "cross2"-------
    t = 0
    cross2Clock.reset()  # clock 
    frameN = -1
    routineTimer.add(2.000000)
    # update component parameters for each repeat
    # keep track of which components have finished
    cross2Components = []
    cross2Components.append(image)
    for thisComponent in cross2Components:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "cross2"-------
    continueRoutine = True
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = cross2Clock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *image* updates
        if t >= 0.0 and image.status == NOT_STARTED:
            # keep track of start time/frame for later
            image.tStart = t  # underestimates by a little under one frame
            image.frameNStart = frameN  # exact frame index
            image.setAutoDraw(True)
        if image.status == STARTED and t >= (0.0 + (2-win.monitorFramePeriod*0.75)): #most of one frame period left
            image.setAutoDraw(False)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineTimer.reset()  # if we abort early the non-slip timer needs reset
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in cross2Components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #-------Ending Routine "cross2"-------
    for thisComponent in cross2Components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    
    #------Prepare to start Routine "response"-------
    t = 0
    responseClock.reset()  # clock 
    frameN = -1
    routineTimer.add(12.000000)
    # update component parameters for each repeat
    # keep track of which components have finished
    responseComponents = []
    responseComponents.append(metronome_c4)
    responseComponents.append(it4_pause)
    for thisComponent in responseComponents:
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    
    #-------Start Routine "response"-------
    continueRoutine = True
    while continueRoutine and routineTimer.getTime() > 0:
        # get current time
        t = responseClock.getTime()
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        # start/stop metronome_c4
        if t >= 0 and metronome_c4.status == NOT_STARTED:
            # keep track of start time/frame for later
            metronome_c4.tStart = t  # underestimates by a little under one frame
            metronome_c4.frameNStart = frameN  # exact frame index
            metronome_c4.play()  # start the sound (it finishes automatically)
        if metronome_c4.status == STARTED and t >= (0 + (12-win.monitorFramePeriod*0.75)): #most of one frame period left
            metronome_c4.stop()  # stop the sound (if longer than duration)
        
        # *it4_pause* updates
        if t >= 0.0 and it4_pause.status == NOT_STARTED:
            # keep track of start time/frame for later
            it4_pause.tStart = t  # underestimates by a little under one frame
            it4_pause.frameNStart = frameN  # exact frame index
            it4_pause.setAutoDraw(True)
            
            #ITERATION3_PIANO
        
            trial_ID = str(trialID2['Direction']) + '_' +str(trialID2['ToneDistance'])
            if trial_ID =='A_1':kind=1
            if trial_ID =='A_2':kind=2
            if trial_ID =='D_1':kind=3
            if trial_ID =='D_2':kind=4
            
            trial= trial_count
            iteration=3
            
            #print trialType
            write_to_piano.writeLog(subject,split, task, blockType, trial_ID, iteration, kind, position,trial, sock,trial_stuff)
            
        if it4_pause.status == STARTED and t >= (0.0 + (12-win.monitorFramePeriod*0.75)): #most of one frame period left
            it4_pause.setAutoDraw(False)
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineTimer.reset()  # if we abort early the non-slip timer needs reset
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in responseComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # check for quit (the Esc key)
        if endExpNow or event.getKeys(keyList=["escape"]):
            core.quit()
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    #-------Ending Routine "response"-------
    for thisComponent in responseComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.nextEntry()
    
# completed 1 repeats of 'trials'


#------Prepare to start Routine "thank_you"-------
t = 0
thank_youClock.reset()  # clock 
frameN = -1
# update component parameters for each repeat
end_key = event.BuilderKeyResponse()  # create an object of type KeyResponse
end_key.status = NOT_STARTED
# keep track of which components have finished
thank_youComponents = []
thank_youComponents.append(end_xp)
thank_youComponents.append(end_key)
for thisComponent in thank_youComponents:
    if hasattr(thisComponent, 'status'):
        thisComponent.status = NOT_STARTED

#-------Start Routine "thank_you"-------
continueRoutine = True
while continueRoutine:
    # get current time
    t = thank_youClock.getTime()
    frameN = frameN + 1  # number of completed frames (so 0 is the first frame)

    # update/draw components on each frame
    
    # *end_xp* updates
    if t >= 0.0 and end_xp.status == NOT_STARTED:
        # keep track of start time/frame for later
        end_xp.tStart = t  # underestimates by a little under one frame
        end_xp.frameNStart = frameN  # exact frame index
        end_xp.setAutoDraw(True)
    if end_xp.status == STARTED and (end_key == 'space'): #most of one frame period left
        end_xp.setAutoDraw(False)
    
    # *end_key* updates
    if t >= 0.0 and end_key.status == NOT_STARTED:
        # keep track of start time/frame for later
        end_key.tStart = t  # underestimates by a little under one frame
        end_key.frameNStart = frameN  # exact frame index
        end_key.status = STARTED
        # keyboard checking is just starting
        end_key.clock.reset()  # now t=0
        event.clearEvents(eventType='keyboard')
    if end_key.status == STARTED:
        theseKeys = event.getKeys(keyList=['space'])
        
        # check for quit:
        if "escape" in theseKeys:
            endExpNow = True
        if len(theseKeys) > 0:  # at least one key was pressed
            end_key.keys = theseKeys[-1]  # just the last key pressed
            end_key.rt = end_key.clock.getTime()
            # a response ends the routine
            continueRoutine = False
    
    # check if all components have finished
    if not continueRoutine:  # a component has requested a forced-end of Routine
        routineTimer.reset()  # if we abort early the non-slip timer needs reset
        break
    continueRoutine = False  # will revert to True if at least one component still running
    for thisComponent in thank_youComponents:
        if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
            continueRoutine = True
            break  # at least one component has not yet finished
    
    # check for quit (the Esc key)
    if endExpNow or event.getKeys(keyList=["escape"]):
        core.quit()
    
    # refresh the screen
    if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
        win.flip()
    else:  # this Routine was not non-slip safe so reset non-slip timer
        routineTimer.reset()

#-------Ending Routine "thank_you"-------
for thisComponent in thank_youComponents:
    if hasattr(thisComponent, "setAutoDraw"):
        thisComponent.setAutoDraw(False)
        end_piano.endExp(sock) 
# check responses
if end_key.keys in ['', [], None]:  # No response was made
   end_key.keys=None
# store data for thisExp (ExperimentHandler)
thisExp.addData('end_key.keys',end_key.keys)
if end_key.keys != None:  # we had a response
    thisExp.addData('end_key.rt', end_key.rt)
thisExp.nextEntry()

#end_piano.endExp(sock) 
win.close()
core.quit()
