#!/usr/bin/env python

'''
Template handler set for a 2afc paradigm.
Want a bundled set of functions so the RPilot can make the task from relatively few params.
Also want it to contain details about how you should draw 2afcs in general in the terminal
Remember: have to put class name in __init__ file to import directly.
'''

import random
from taskontrol.settings import rpisettings as rpiset
import datetime
import itertools

TASK = 'Nafc'

class Nafc:
    """
    Actually 2afc, but can't have number as first character of class.
    Template for 2afc tasks. Pass in a dict. of sounds & other parameters,
    """

    # Class attributes
    PARAM_LIST = ['sounds', 'reward', 'punish', 'pct_correction', 'bias_mode']
    DATA_LIST = ['target', 'target_sound', 'response', 'correct', 'timestamp', 'bias']

    def __init__(self, sounds, reward=50, punish=2000, pct_correction=.5, bias_mode=1, assisted_assign=0):
        # Sounds are a dict like {'L': 'path/to/file.wav', 'R': 'etc'} or {'L':['path/to/sound1.wav','path/to/sound2.wav']}
        # Or like {'L':{'tone':500} etc. when that's implemented. sounds['punish'] for punish sound
        # Rewards, punish time, etc. in ms.
        # pct_correction is the % of trials that are correction trials
        # bias_correct is 1 or 0 whether you'd like bias correction enabled: eg. if mice are 65% biased towards one side,
        #     that side will only be the target 35% of the time.
        # Pass assign as 1 to be prompted for all necessary params.

        if assisted_assign:
            self.assisted_assign()
            return

        # Fixed parameters
        self.sounds = sounds
        self.sound_player = None
        self.reward = reward
        self.punish = punish
        self.pct_correction = pct_correction
        self.bias_mode = bias_mode
        self.stage_names = ["request","discrim","reinforcement"]


        # Variable Parameters
        self.target = None
        self.target_sound = None
        self.bias = None
        self.response = None
        self.correct = None

        # This allows us to cycle through the task by just repeatedly calling self.stages.next()
        self.stages = itertools.cycle([self.request,self.discrim,self.reinforcement])

        # Checking that input


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

    def assisted_assign(self):
        # This should actually be just a way to send the param_list to terminal
        # for param in self.param_list:
        pass




#################################################################################################
# Prebuilt Parameter Sets

FREQ_DISCRIM = {
    'sounds':{
        'L': {'type':'tone','frequency':500, 'duration':500,'amplitude':.1},
        'R': {'type':'tone','frequency':2000,'duration':500,'amplitude':.1}
    },
    'reward':50,
    'punish':2000,
    'pct_correction':0.5,
    'bias_mode':1
}











