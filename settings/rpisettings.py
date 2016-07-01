#!/usr/bin/python2.7

'''
Storage of variables specific to the way the Raspberry Pi is set up in your rig.
eg. Pin numbers, IP addresses (host terminal and RPi client), directories, etc.

Loaded by RPilot when it is instantiated.

'''

__author__ = 'Jonny Saunders <jsaunder@uoregon.edu>'
__created__ = '2016-06-29'

#############################################
# Local
#############################################

# Which Raspberry Pi is this?
PI_NUM = 1

# Where is the speaker calibration file?
SPEAKER_CALIBRATION = None

# Where should we store data?
PI_DATA_DIR = '/var/tmp/data/'

# Address pins with Board numbers or BCM numbers?
PIN_MODE = "BOARD"
#PIN_MODE = "BCM"

# How are we hooked up?
INPUTS = {
    'L' : 11,
    'C' : 13,
    'R' : 15
}
INPUT_LIST = [11,13,15]
## Note: this code assumes your inputs are Pull-down, that's hardcoded in the RPilot init

#: Name for each output line.
OUTPUTS = {
    'LWater' : None,
    'CWater' : None,
    'RWater' : None
}
OUTPUT_LIST = [None]




#############################################
# Network
#############################################

# What should I set my static IP to?
MY_IP = None

# Where is the terminal that we report to?
HOST_IP = None

