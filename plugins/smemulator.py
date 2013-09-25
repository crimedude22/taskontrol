#!/usr/bin/env python

'''
State machine client emulator.

TO DO:
'''


__version__ = '0.1'
__author__ = 'Santiago Jaramillo <jara@cshl.edu>'
__created__ = '2013-09-23'

import time
import numpy as np
import datetime
from PySide import QtCore 
from PySide import QtGui 

MAXNEVENTS = 512
MAXNSTATES = 256
MAXNEXTRATIMERS = 16
MAXNINPUTS = 8
MAXNOUTPUTS = 16
MAXNACTIONS = 2*MAXNINPUTS + 1 + MAXNEXTRATIMERS


class EmulatorGUI(QtGui.QWidget):
    def __init__(self, parent=None):
        super(EmulatorGUI, self).__init__(parent)
        '''
        window = QtGui.QMainWindow(self)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        window.statusBar()
        menubar = window.menuBar()
        switchtoSchMenu = menubar.addMenu('switchtoSCHEMATIC')
        window.setGeometry(100, 600, 500, 300)
        window.setWindowTitle('Layout View')
        window.show()
        '''
        pass


class StateMachineClient(QtCore.QObject):

    def __init__(self, connectnow=True, verbose=False, parent=None):
        super(StateMachineClient, self).__init__(parent)
        # -- Variables for SM client --
        # -- These values will be set by set_sizes() --
        self.nInputs = 0
        self.nOutputs = 0
        self.nExtraTimers = 0
        self.nActions = 1

        # DO I NEED THESE?
        ###self.lastTimeOfEvents = 0
        ###self.serverTime = 0
        ###self.state = 0
        ###self.lastEvents = []

        # -- Variables for SM server --
        self.timeOfCreation = time.time()
        ###self.timeOfLastEvents = self.timeOfCreation
        self.runningState = False
        self.eventsTime = np.zeros(MAXNEVENTS)
        self.eventsCode = np.zeros(MAXNEVENTS)
        self.nEvents = 0
        self.eventsToProcess = 0
        self.currentState = 0
        self.previousState = 0 # NEEDED?
        self.nextState = np.zeros(MAXNEVENTS)

        self.sizesSetFlag = False;
        # -- The following sizes will be overwritten by this class' methods --
        self.inputValues = np.zeros(MAXNINPUTS)
        self.serialOutputs = np.zeros(MAXNSTATES)
        self.stateMatrix = np.zeros((MAXNSTATES,MAXNACTIONS))
        self.stateTimers = np.zeros(MAXNSTATES)
        self.stateOutputs = np.zeros((MAXNSTATES,MAXNOUTPUTS))
        self.extraTimers = np.zeros(MAXNEXTRATIMERS)
        self.triggerStateEachExtraTimer = np.zeros(MAXNEXTRATIMERS)
        
        self.stateTimerValue = 0;
        self.extraTimersValues = np.zeros(MAXNEXTRATIMERS)
        self.currentState = 0;

        # -- Variables for Virual Hardware --
        self.outputs = np.zeros(MAXNOUTPUTS)
        self.inputs = np.zeros(MAXNINPUTS)
        self.serialout = 0

        # -- Create timer --
        self.interval = 0.01 # Polling interval (sec)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.execute_cycle)

        self.showgui()
        
    def showgui(self):
        self.window = QtGui.QMainWindow()
        #self.window = QtGui.QWidget()
        self.window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.window.setGeometry(100, 600, 500, 300)
        self.window.setWindowTitle('State Machine Emulator')
        self.window.show()
        self.window.activateWindow()

    def send_reset(self):
        pass
    def connect(self):
        print 'EMULATOR: Connect.'
        pass
    def test_connection(self):
        pass
    def get_version(self):
        pass
    def set_sizes(self,nInputs,nOutputs,nExtraTimers):
        self.nInputs = nInputs
        self.nOutputs = nOutputs
        self.nExtraTimers = nExtraTimers
        self.nActions = 2*nInputs + 1 + nExtraTimers
        self.sizesSetFlag = True
    def get_time(self):
        serverTime = time.time()-self.timeOfCreation
        #datetime.datetime.now().second  ######## DEBUG ##########
        return round(serverTime,3)
    def get_inputs(self):
        pass
    def force_output(self,output,value):
        self.outputs[output] = value
        print 'EMULATOR: Force output {0} to {1}'.format(output,value)
        pass
    def set_state_matrix(self,stateMatrix):
        '''
        stateMatrix: [nStates][nActions]  (where nActions is 2*nInputs+1+nExtraTimers)
        See smclient.py
        '''
        # WARNING: We are not checking the validity of this matrix
        self.stateMatrix = np.array(stateMatrix)
        print 'EMULATOR: Set state matrix.'
    def send_matrix(self,someMatrix):
        pass
    def report_state_matrix(self):
        pass
    def run(self):
        self.runningState = True
        self.timer.start(1e3*self.interval) # timer takes interval in ms
        print 'EMULATOR: Run.'
    def stop(self):
        self.timer.stop()
        self.runningState = False
        print 'EMULATOR: Stop.'
    def set_state_timers(self,timerValues):
        self.stateTimers = np.array(timerValues)
        pass
    def report_state_timers(self):
        pass
    def set_extra_timers(self,extraTimersValues):
        self.extraTimers = np.array(extraTimersValues)
        pass
    def set_extra_triggers(self,stateTriggerEachExtraTimer):
        self.triggerStateEachExtraTimer = np.array(stateTriggerEachExtraTimer)
        pass
    def report_extra_timers(self):
        pass
    def set_state_outputs(self,stateOutputs):
        self.stateOutputs = np.array(stateOutputs)
        print 'EMULATOR: Set state outputs.'
        pass
    def set_serial_outputs(self,serialOutputs):
        self.serialOutputs = np.array(serialOutputs)
        pass
    def report_serial_outputs(self):
        pass
    def get_events(self):
        lastEventsTime = self.eventsTime[:self.nEvents]
        lastEventsCode = self.eventsCode[:self.nEvents]
        lastNextState = self.nextState[:self.nEvents]
        lastEvents = np.column_stack((lastEventsTime,lastEventsCode,lastNextState))
        self.nEvents = 0
        return lastEvents.tolist()
    def get_current_state(self):
        return self.currentState
        pass
    def force_state(self,stateID):
        ## FIXME: In this function, the way nextState is updated is weird (in arduino)
        #  maybe it should be closer to add_event
        self.eventsTime[self.nEvents] = self.get_time()
        self.currentState = stateID
        self.eventsCode[self.nEvents] = -1
        self.nextState[self.nEvents] = self.currentState
        self.nEvents += 1
        self.enter_state(self.currentState)
        print 'EMULATOR: Force state {0}.'.format(stateID)
    def write(self,value):
        pass
    def readlines(self):
        pass
    def read(self):
        pass
    def close(self):
        print 'EMULATOR: Close.'

    def add_event(self,thisEventCode):
        self.eventsTime[self.nEvents] = self.get_time()
        self.eventsCode[self.nEvents] = thisEventCode
        self.nEvents += 1
        self.eventsToProcess += 1

    def execute_cycle(self):
        ###### FINISH ########
        # -- Check if any input has changed, if so, add event --
        for indi in range(self.nInputs):
            # if changed
            #add_event(2*indi + previousValue);
            pass 
        currentTime = self.get_time()
        if (currentTime-self.stateTimerValue) >= self.stateTimers[self.currentState]:
            self.add_event(2*self.nInputs)
            stateTimerValue = currentTime # Restart timer
            pass

        # TODO: extratimers
        ###
            
        # -- Update state machine given last events --
        # FIXME: this is ugly (in the arduino code).
        #        update_state_machine sneakily changes a value (currentState)
        previousState = self.currentState
        self.update_state_machine()
        if self.currentState != previousState:
            self.enter_state(self.currentState)
            pass

        

    def enter_state(self,currentState):
        self.stateTimerValue = self.get_time()
        # TODO: Finish extra timers
        #for indt in range(self.nExtraTimers)
        self.outputs = self.stateOutputs[currentState,:]
        self.serialout = self.serialOutputs[currentState]

    def update_state_machine(self):
        while(self.eventsToProcess>0):
            currentEventIndex = self.nEvents-self.eventsToProcess
            currentEvent = self.eventsCode[currentEventIndex];
            self.nextState[currentEventIndex] = self.stateMatrix[self.currentState,currentEvent]
            self.currentState = self.nextState[currentEventIndex]
            self.eventsToProcess -= 1


