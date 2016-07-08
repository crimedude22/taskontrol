#!/usr/bin/env python

'''
Template handler set for a 2afc paradigm.
Want a bundled set of functions so the RPilot can make the task from relatively few params.
Also want it to contain details about how you should draw 2afcs in general in the terminal
'''

import random
from taskontrol.settings import rpisettings as rpiset
import RPi.GPIO as GPIO
import datetime
import itertools

class Twoafc:
    """
    Templace for 2afc tasks. Pass in a dict. of sounds & other parameters,
    """
    def init(self, sounds, reward=50, punish=2000, pct_correction=.5, bias_mode=1):
        # Sounds are a dict like {'L': 'path/to/file.wav', 'R': 'etc'} or {'L':['path/to/sound1.wav','path/to/sound2.wav']}
        # Or like {'L':{'tone':500} etc. when that's implemented. sounds['punish'] for punish sound
        # Rewards, punish time, etc. in ms.
        # pct_correction is the % of trials that are correction trials
        # bias_correct is 1 or 0 whether you'd like bias correction enabled: eg. if mice are 65% biased towards one side,
        #     that side will only be the target 35% of the time.

        # Fixed parameters
        self.sounds = sounds
        self.reward = reward
        self.punish = punish
        self.pct_correction = pct_correction
        self.bias_mode = bias_mode
        self.stage_names = ["request","discrim","reinforcement"]
        self.param_list = ['sounds', 'reward', 'punish', 'pct_correction', 'bias_mode']
        self.data_list = ['target', 'target_sound', 'response', 'correct', 'timestamp', 'bias']

        # Variable Parameters
        self.target = None
        self.target_sound = None
        self.bias = None
        self.response = None
        self.correct = None

        # This allows us to cycle through the task by just repeatedly calling self.stages.next()
        self.stages = itertools.cycle([self.request(),self.discrim(),self.reinforcement()])

    def request(self):
        if random.random() > .5:
            self.target = 'L'
            self.target_sound = random.choice(self.sounds['L'])
        else:
            self.target = 'R'
            self.target_sound = random.choice(self.sounds['R'])

        data = {'target':self.target,'target_sound':self.target_sound,'timestamp':datetime.datetime.now().isoformat()}
        return data

    def discrim(self):
        # Figure some way to access RPilot's sound server to play sound, or else put trigger in RPilot that plays sound from request
        # then sleep for duration of sound
        data = {'timestamp':datetime.datetime.now().isoformat()}
        return data

    def reinforcement(self,pin):
        # pin passed from callback function
        self.response = pin
        if pin == self.target:
            self.correct = 1
        else:
            self.correct = 0
            # play self.sounds["punish"]

        data = {'response':self.response, 'correct':self.correct}
        return data
        # Also calc ongoing vals. like bias.


    def give_sound_player(self,sound_player):
        # Be given the handle of the sound player by RPilot.
        # We can't *get* the sound player because we don't know where to get it from without instantiating a new Pilot.
        self.sound_player = sound_player






def setup_test():
    GPIO.setmode(GPIO.BOARD)
    for i in rpiset.INPUT_LIST:
        GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def trial_start():
    print('Here we go, fresh new trial\n')
    if np.random.rand() > .5:
        strprint = 'I just played a Right Sound!\n'
        target = 'R'
    else:
        strprint = 'I just played a Left Sound!\n'
        target = 'L'

    GPIO.wait_for_edge(rpiset.INPUTS['C'])
    print(strprint)

    # We don't want to set these up until we get a center poke
    if target == 'R':
        GPIO.add_event_detect(rpiset.INPUTS['R'],GPIO.RISING,callback=correct)
        GPIO.add_event_detect(rpiset.INPUTS['L'], GPIO.RISING, callback=incorrect)
    elif target == 'L':
        GPIO.add_event_detect(rpiset.INPUTS['R'], GPIO.RISING, callback=incorrect)
        GPIO.add_event_detect(rpiset.INPUTS['L'], GPIO.RISING, callback=correct)
    else:
        print("looks like something went wrong assigning the target\n")
        trial_start()

def incorrect(pin):
    print("INCORRECT!!!\n")
    trial_start()

def correct(pin):
    print("CORRECT :)\n")
    trial_start()

trial_start()






