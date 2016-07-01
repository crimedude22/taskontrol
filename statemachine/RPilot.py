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
    -
'''

__version__ = '0.1'
__author__ = 'Jonny Saunders <jsaunder@uoregon.edu>'

import os
from taskontrol.settings import rpisettings as rpiset
import h5py
import datetime


# try: #...to get existing settings
#     from taskontrol.settings import rpisettings as rpiset
#     DATA_DIR = rigsettings.DATA_DIR
# except ImportError:
#     f = open('{}/rpisettings.py'.format(os.path.dirname(taskontrol.settings.__file__)),'w+')
#     DATA_DIR = '/var/tmp/data'
#     f.write('DATA_DIR = \'/var/tmp/data\'\n')



class RPilot:
    def __init__(self, firstrun=0):
        # Init all the hardware stuff, get the RPi ready for instructions
        # Remember! All the RPi should care about is the immediate future and the near past.
        # Let the terminal deal with stuff like total number of trials, etc.
        self.ntrials =

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

    def load_mouse(self, mouse):
        # load mouse object from file, load their protocol
        pass




class Mouse:
    """Mouse object for managing protocol, parameters, and data"""
    # hdf5 structure is split into two groups, mouse info and trial data.

    def __init__(self, name, new=0):
        self.name = name
        if new:
            self.new_mouse(name)
            return

        self.h5f = h5py.File(rpiset.PI_DATA_DIR + self.name + '.hdf5', 'r+')



    def new_mouse(self,name):
        try:
            self.h5f = h5py.File(rpiset.PI_DATA_DIR + self.name + '.hdf5', 'w-')
        except:
            print("Mouse already has a file.")
            return

        # Basic info about the mouse
        self.startdate = datetime.today()

        # Since the type of protocol will determine what we want to save, get it and its info first
        numvars = None #will be the number variables we want to save

        # Save info to hdf5
        self.info = self.h5f.create_group("info")
        self.data = self.h5f.create_group("data")
        self.trial_records = self.data.create_dataset("trial_records",maxshape=(none,numvars))
        self.info["startdate"] = self.startdate



