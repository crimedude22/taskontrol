#!/usr/bin/python2.7

'''
Drives the Raspberry Pi

Sets up & coordinates the multiple threads needed to function as a standalone taskontrol client
    -State Control: Managing box I/O and the state matrix
    -Audio Server
    -Communication w/ home terminal via TCP/IP

To Do (Initial, 6/22/16):
    -Build initialization method that does first setup to store location of host terminal, data, etc.
    -Build calibration method
    -Build in threading/multiprocessing
    -Sounds should be a) parameterized in the protocol file, and b) handled/defined in the sounds file
        -So the mouse object is saved with the parameters for the protocol, then RPilot loads the task template w/ those
        parameters so it is the child of RPilot, then the functions in the task template have access to RPilot methods.
'''

__version__ = '0.1'
__author__ = 'Jonny Saunders <jsaunder@uoregon.edu>'

import os
from taskontrol.settings import rpisettings as rpiset
from taskontrol.core import mouse as Mouse
import h5py
import datetime
import RPi.GPIO as GPIO
import pyo
import threading

class RPilot:
    def __init__(self, firstrun=0):
        # Init all the hardware stuff, get the RPi ready for instructions
        # Remember! All the RPi should care about is the immediate future and the near past.
        # Let the terminal deal with stuff like total number of trials, etc.
        self.licks  = rpiset.LICKS
        self.valves = rpiset.VALVES
        self.init_pins()
        self.init_pyo()
        # Synchronize system clock w/ correct time


    def init_pins(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.licks.values(), GPIO.IN, pull_up_down.GPIO.PUD_DOWN)
        GPIO.setup(self.valves.values(), GPIO.OUT, initial=GPIO.LOW)

    def pin_cb(self,pin):
        # Should be as simple as self.protocol_advance(pin) or whatever to .next() the protocol, save returned data, etc.
        pass

    def init_pyo(self):
        self.pyo_server = pyo.Server(audio='jack').boot()
        self.pyoServer.start()

    def cache_sounds(self):
        # Cache sounds to memory with pyo.SndTable(path)
        pass

    def load_mouse(self, name):
        self.subject = Mouse(name)

    def load_protocol(self):
        '''
        Parameters for setting up the protocol should be in self.subject.protocol_params
        Then we can do something like self.protocol = protocol_params.type(params)
        Since the protocol will be a cyclic iterable, running should be as simple as protocol.next(), w/ grad. criter, etc.
        '''
        pass


    def run(self):
        #first setup a TCP/IP interrupt to listen for
        #something like state_switch = statemat.phase(argin)
        #the statemat will run all the pin switches, we return here to save data & check in w/ the terminal
        #interrupts in the lower level function should call up here with a basic 2 field event ind:
            #timestamp:event
        #Then each protocol should have a dict that translates that back into human readable trial recs.
        pass

    def terminal_interpreter(self):
        #an arg in needs to be the command sent by the network
        #this is the callback for the RPi.GPIO interrupt that handles whatever message is sent

    def wait(self):
        #after init, wait for connection from the terminal
        #set up a TCP interrupt with RPi.GPIO
        pass

    def receive_matrix(self,stateMatrix):
        #basically just want to save a .py file
        pass






