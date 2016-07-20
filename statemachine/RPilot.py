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
from taskontrol import core
import h5py
import datetime
# import RPi.GPIO as GPIO
import pyo
import threading
from time import sleep

class RPilot:
    def __init__(self, firstrun=0):
        # Init all the hardware stuff, get the RPi ready for instructions
        # Remember! All the RPi should care about is the immediate future and the near past.
        # Let the terminal deal with stuff like total number of trials, etc.
        self.licks  = rpiset.LICKS
        self.valves = rpiset.VALVES
        # self.init_pins()
        # self.init_pyo()
        self.protocol_ready = 0
        # Synchronize system clock w/ correct time


    def init_pins(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.licks.values(), GPIO.IN, pull_up_down.GPIO.PUD_DOWN)
        GPIO.setup(self.valves.values(), GPIO.OUT, initial=GPIO.LOW)

    def pin_cb(self,pin):
        # Should be as simple as self.protocol_advance(pin) or whatever to .next() the protocol, save returned data, etc.
        pass

    def init_pyo(self):
        # sampling rate, nchan, etc. set in the JACKD_STRING
        os.system(rpiset.JACKD_STRING)
        sleep(1) # Wait to let the server start to pyo doesn't try too
        self.pyo_server = pyo.Server(audio='jack').boot()
        self.pyo_server.start()

    def load_sounds(self,sounds):
        '''
        Sounds as a param dict. understandable by one of the types in 'sounds'
        Returns a soundtable-esque packaged soundplayer capable of playing sound with .out()
        Make unique IDs for each sound for data collection, store param dicts in sound_lookup so IDs can be compared to
        the param sets that made them.
        '''
        self.pyo_sounds = dict()
        self.sound_lookup = dict()
        for k,v in sounds.items():
            # If multiple sounds on one side, 'L' val will be a list.
            if isinstance(v,list):
                self.pyo_sounds[k] = list()
                for i,z in enumerate(v):
                    # Uses the SWITCH dict in sounds to call the proper function,
                    # calls fnxn in sounds with parameter dict 'z',
                    # appends to list of 'k' sounds
                    self.pyo_sounds[k].append(core.sounds.SWITCH[z['type']](**z))
                    id = str(k) + str(i)
                    self.pyo_sounds[k][-1].id = id
                    self.sound_lookup[id] = z
            else:
                self.pyo_sounds[k] = core.sounds.SWITCH[v['type']](**v)
                self.pyo_sounds[k].id = str(k)
                self.sound_lookup[k] = v

    def load_mouse(self, name):
        self.subject = core.mouse.Mouse(name)
        # also load its protocol and sounds

    def new_mouse(self, name):
        self.subject = core.mouse.Mouse(name, new=1)

    def assign_subject_protocol(self, protocol, params):
        self.subject.assign_protocol(self.subject,protocol,params)

    def prepare_trials(self):
        # Maybe just make this part of load_mouse
        try:
            self.subject
        except NameError:
            print("Need to have a subject loaded w/ a protocol assigned to prepare trials!")

    def load_protocol(self):
        # load a mouse's protocol
        pass







    def run(self):
        #first setup a TCP/IP interrupt to listen for
        #something like state_switch = statemat.phase(argin)
        #the statemat will run all the pin switches, we return here to save data & check in w/ the terminal
        #interrupts in the lower level function should call up here with a basic 2 field event ind:
            #timestamp:event
        #Then each protocol should have a dict that translates that back into human readable trial recs.
        if self.protocol_ready == 0:
            self.prepare_trials()


    def terminal_interpreter(self):
        #an arg in needs to be the command sent by the network
        #this is the callback for the RPi.GPIO interrupt that handles whatever message is sent
        pass

    def wait(self):
        #after init, wait for connection from the terminal
        #set up a TCP interrupt with RPi.GPIO
        pass






