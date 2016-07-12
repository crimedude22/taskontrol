#!/usr/bin/python2.7

'''
classes to build sounds from parameters
use the SOUND_SWITCH to allow listing of sound types in the GUI & flexible coding from other modules
then you can call sounds like sounds.SWITCH['tone'](freq=1000, etc.)

returns
'''

import pyo

SWITCH = {
    'tone':Tone

}

def Tone(frequency,duration,amplitude=0.1,phase=0):
    '''
    The Humble Sine Wave
    '''
    tab = pyo.SquareTable()
    trig = pyo.Trig()
    tenv = pyo.TrigEnv(trig,table=tab,dur=5,mul=.3)
    fad = pyo.Fader(fadein=0.1,fadeout=0.1,dur=3,mul=.3)
    sin = pyo.Sine(300,mul=fad).out()


class Test:
    def __call__(self,str):
        print(str)

def Wav_file(path,duration,)