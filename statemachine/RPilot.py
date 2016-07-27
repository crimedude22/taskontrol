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
import subprocess
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
        # Remember! All the RPi should care about is the immediate future and the recent past.
        # Let the terminal deal with stuff like total number of trials, etc.
        self.licks  = rpiset.LICKS
        self.valves = rpiset.VALVES
        self.licks_inv = {v: k for k,v in self.licks.items()} #So we can translate pin # to 'L', etc.
        self.data = dict()
        self.triggers = None
        self.timers = None
        self.wait = None
        # self.init_pins()
        # self.init_pyo()
        self.protocol_ready = 0


        # Init TCP/IP connection
        # TODO TCP/IP communication w/ terminal
        # Synchronize system clock w/ time from terminal.
        # Send message back to terminal that we're all good.

    #################################################################
    # Hardware Init
    #################################################################
    def init_pins(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.licks.values(), GPIO.IN, pull_up_down.GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.licks.values(), GPIO.RISING, callback=self.pin_cb, bouncetime = 500) # Bouncetime is ms unresponsive after trigger
        GPIO.setup(self.valves.values(), GPIO.OUT, initial=GPIO.LOW)

    def init_pyo(self):
        # sampling rate, nchan, etc. set in the JACKD_STRING
        # check if jackd is running, if so kill it and restart
        try:
            procnum = int(subprocess.Popen('pidof jackd', shell=True, stdout=subprocess.PIPE).communicate()[0])
            if os.path.exists("/proc/{}".format(procnum)):
                os.system('killall jackd')
        except ValueError:
            # if jackd not running, should be a ValueError b/c we try to convert None to int
            pass

        os.system(rpiset.JACKD_STRING)
        sleep(1) # Wait to let the server start to pyo doesn't try too
        self.pyo_server = pyo.Server(audio='jack',nchnls=rpiset.NUM_CHANNELS).boot()
        self.pyo_server.start()

    #################################################################
    # Mouse and Protocol Management
    #################################################################
    def load_mouse(self, name):
        # Task should be assigned in the Mouse object such that subject.stages.next() should run the next stage.
        self.subject = core.mouse.Mouse(name)
        # We have to make the sounds for the task so the task class can remain agnostic to the sound implementation
        # TODO: Check if task is assigned before trying to load sounds.
        self.load_sounds(self.subject.task.soundict)
        self.subject.receive_sounds(self.pyo_sounds,self.sound_lookup)

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

    def new_mouse(self, name):
        self.subject = core.mouse.Mouse(name, new=1)

    def assign_subject_protocol(self, protocol, params):
        self.subject.assign_protocol(self.subject, protocol, params)

    #################################################################
    # Trial Running and Management
    #################################################################
    def run(self,pin = None):
        """
        Refresher on the terminology that's been adopted: a "Protocol" is a collection of "Steps", each of which is a "Task" with promotion criteria to the next step.
            Each task is composed of "stages" which are the individual points of decision and response that the RPi and mouse engage in.
        Tasks are run "stagewise," where the run function calls next() on the iterator that contains the stage functions.
            Tasks are only recognized as such when an "end_trial" trigger is returned by the stage function, prompting the
            RPilot to save the trial's data. Otherwise they are run continuously.
        Each run cycle proceeds:
            -check_ready(): checks if everything has been prepared for the trial. The Task should provide a list of things to check (not implemented yet)
            -subject.task.next(): computes the logic for the next trial stage, returns data, triggers, and timers.
            -handle_triggers(): if triggers aren't returned as callable functions (rewards, for example, can't be
                returned as functions b/c the task doesn't know about the reward hardware), we make them callable.
            -

        pin passes the triggered pin (if any) back to the task class
        """
        if not self.check_ready():
            # TODO Make more verbose as check_ready is populated
            raise Exception("Our check didn't turn out which is weird because it doesn't check anything yet")

        # Calculate the next stage
        data,triggers,timers = self.subject.task.next(pin)

        # Check if our triggers are functions or need to be made functions
        for k,v in triggers.items():
            if not callable(v):
                triggers[k] = self.wrap_triggers(k,v)

        # Set up a timer thread to handle timers -
            # for example, a too early timer would replace the triggers with the too_early_sound until the dur. of the stim is up
            # then change it back when the time is up.
            # wrap sound trigger in function that sets an event when the sound is finished playing
                #trig = tabobj['trig'], trigfunc(trig, switch_trigs)

        self.handle_timers(timers)

        # TODO Check if any of our triggers ask us to wait before making the next stage's triggers available (eg. punish delay)
        # TODO Implement the 'immediate' timer to immediately call next stage
        # like make the function a new thread, and then check for the thread's completion before assigning the next round's triggers

        # Make triggers available to pin_cb function - which will do the calling in a separate thread
        self.triggers = triggers

        # Add returned data to trial data dict. If this is the last stage in the trial, save the data.
        if "task_end" in triggers.keys():
            self.data.update(data)
            self.subject.save_trial(self.data)
        else:
            self.data.update(data)


        # TODO: Wait for any timers

        # We then implicitly wait for run to get called again by pin_cb()

    def check_ready(self):
        # Put preflight error checking here as needed.
        # Return True if good to go, for now we'll hardcode it
        return True

    def pin_cb(self,pin):
        # Call the appropriate trigger
        try:
            self.triggers[self.licks_inv[pin]]()
            self.triggers = None # clear triggers so no double taps
            self.run(self.licks_inv[pin])
        except:
            # If the port doesn't have a trigger assigned to it...
            pass

    def handle_triggers(self):
        """
        When the pins can't speak for themselves...
        :return:
        """
        pass

    def handle_timers(self,timerdict):
        # Handle timers depending on type (key of timerdict)
        if not isinstance(timerdict,dict):
            raise TypeError("Timers need to be returned as a dictionary of form {'type':params}")
        for k,v in timerdict.items():
            if k == 'too_early':
                # Assumes a single pyo soundTable trigger,
            else:
                # TODO implement timeout
                raise RuntimeError("Don't know how to handle this type of timer")

    def wrap_triggers(self,key,val):
        # TODO: redo this, this is dumb. we can't open ports this way. Just make a handling function that returns a function for christ's sake.
        """
        Some triggers can't be passed as as already-made bound methods. We can handle that without breaking the generality of run()
        Map a trigger to a handling function which can then be called independently.
        eg. x = wrap_trigger(trigger={'playsound':'yowza!'} - (everybody's favorite sound)
            y = wrap_trigger(trigger={'playsound':'dy-no-mite!'} - (yuck, who let you in my house?)
        x() and y() can then be used separately as triggers that the task instance is unable to make itself.
        """
        if key == 'task_end':
            trigger = None

        return trigger

    def terminal_interpreter(self):
        #an arg in needs to be the command sent by the network
        #this is the callback for the RPi.GPIO interrupt that handles whatever message is sent
        pass

    def wait(self):
        #after init, wait for connection from the terminal
        #set up a TCP interrupt with RPi.GPIO
        pass






