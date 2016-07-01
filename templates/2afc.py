#!/usr/bin/env python

'''
Template handler set for a 2afc paradigm.
Want a bundled set of functions so the RPilot can make the task from relatively few params.
Also want it to contain details about how you should draw 2afcs in general in the terminal
'''


import numpy as np
# from taskontrol.settings import rpisettings as rpiset
import RPi.GPIO as GPIO


rpiset.INPUTS = {
    'L' : 11,
    'C' : 13,
    'R' : 15
}
rpiset.INPUT_LIST = [11,13,15]

# Just make a quick and dirty example, not even close to how we'll do it in reality.
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






