#!/usr/bin/python2.7

'''
Base Mouse Class.
Methods for storing data like mass, DOB, etc. as well as assigned protocols and trial data
'''

from taskontrol.settings import rpisettings as rpiset
import os
import h5py
import datetime

class Mouse:
    """Mouse object for managing protocol, parameters, and data"""
    # hdf5 structure is split into two groups, mouse info and trial data.

    def __init__(self, name, new=0):
        self.name = str(name)
        if new or not os.path.isfile(rpiset.PI_DATA_DIR + self.name + '.hdf5'):
            self.new_mouse(name)
            return

        self.h5f = h5py.File(rpiset.PI_DATA_DIR + self.name + '.hdf5', 'r+')

        # Get mouse attributes from hdf5 file
        self.__dict__.update(dict(self.h5f["info"].attrs.items()))

    def new_mouse(self,name):
        try:
            self.h5f = h5py.File(rpiset.PI_DATA_DIR + self.name + '.hdf5', 'w-')
        except:
            print("Mouse already has a file.")
            return

        # Basic info about the mouse
        self.startdate = datetime.date.today().isoformat()

        try:
            self.baseline_mass = float(raw_input("\nWhat is {}'s baseline mass?\n    >".format(self.name)))
            self.minimum_mass = float(raw_input("\nAnd what is {}'s minimum mass? (eg. 80% of baseline?)\n    >".format(self.name)))
            self.box = int(raw_input("\nWhat box will {} be run in?\n    >".format(self.name)))
        except ValueError:
            print "\nNumber must be convertible to a float, input only numbers in decimal format like 12.3.\nTrying again..."
            self.baseline_mass = float(raw_input("\nWhat is {}'s baseline mass?\n    >".format(self.name)))
            self.minimum_mass = float(raw_input("\nAnd what is {}'s minimum mass? (eg. 80% of baseline?)\n    >".format(self.name)))
            self.box = int(raw_input("\nWhat box will {} be run in?\n    >".format(self.name)))

        # Make and Save info to hdf5
        self.h5info = self.h5f.create_group("info")
        self.h5data = self.h5f.create_group("data")

        self.h5info.attrs["name"] = self.name
        self.h5info.attrs["startdate"] = self.startdate
        self.h5info.attrs["baseline_mass"] = self.baseline_mass
        self.h5info.attrs["minimum_mass"] = self.minimum_mass
        self.h5info.attrs["box"] = self.box

        self.h5f.flush()

    def assign_protocol(self,protocol):
        #Condition the size of numvars on the number of vars to be stored
        # Assign the names of columns as .attrs['column names']
        self.trial_records = self.data.create_dataset("trial_records",maxshape=(none,numvars))
        # Give mouse a job
        pass

    def put_away(self):
        self.h5f.flush()
        self.h5f.close()



