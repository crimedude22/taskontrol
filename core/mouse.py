#!/usr/bin/python2.7

'''
Base Mouse Class.
Methods for storing data like mass, DOB, etc. as well as assigned protocols and trial data
'''

from taskontrol.settings import rpisettings as rpiset
from taskontrol import templates
import os
import h5py
import datetime
from importlib import import_module
import json

class Mouse:
    """Mouse object for managing protocol, parameters, and data"""
    # hdf5 structure is split into two groups, mouse info and trial data.

    def __init__(self, name, new=0):
        self.name = str(name)
        if new or not os.path.isfile(rpiset.PI_DATA_DIR + self.name + '.hdf5'):
            self.new_mouse(name)
            return

        self.h5f = h5py.File(rpiset.PI_DATA_DIR + self.name + '.hdf5', 'r+')
        self.h5info = self.h5f['info']
        self.h5data = self.h5f['data']

        # Get mouse attributes from hdf5 file
        self.__dict__.update(dict(self.h5f["info"].attrs.items()))

        # Load Task if Exists
        if self.h5data.keys():
            last_assigned_task = self.h5data.keys()[-1]
            self.h5trial_records = self.h5data[last_assigned_task]
            self.task_type = self.h5trial_records.attrs['task_type']

            # Params can be described with a string for a template parameter set or a dict of params.
            if 'template_params' in self.h5trial_records.attrs.keys():
                self.task_params = self.h5trial_records.attrs['template_params']
            else:
                param_dict = dict((key,value) for key,value in self.h5trial_records.attrs.iteritems() if not key == 'task_type')
                self.task_params = param_dict

            self.assign_protocol(self.task_type,self.task_params)

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

    def assign_protocol(self,protocol,params):
        # Will need to change this to be protocols rather than individual steps, developing the skeleton.
        #Condition the size of numvars on the number of vars to be stored
        # Assign the names of columns as .attrs['column names']
        self.task_type = protocol
        self.task_params = params

        # Import the task class from its module
        template_module = import_module('taskontrol.templates.{}'.format(protocol))
        task_class = getattr(template_module,template_module.TASK)

        # Check if params are a dict of params or a string referring to a premade parameter set
        if isinstance(params, basestring):
            template_params = getattr(template_module, params)
            self.task = task_class(**template_params)
        elif isinstance(params, dict):
            self.task = task_class(**params)
        else:
            raise TypeError('Not sure what to do with your Params, need dict or string reference to parameter set in template')

        # Make dataset in the hdf5 file to store trial records. When protocols are multiple steps, this will be multiple datasets
        self.h5trial_records = self.h5data.create_dataset("trial_records",(10000,len(task_class.DATA_LIST)),maxshape=(None,len(task_class.DATA_LIST)))
        self.h5trial_records.attrs['task_type'] = protocol
        if isinstance(params,basestring):
            self.h5trial_records.attrs['template_params'] = params
        elif isinstance(params, dict):
            self.h5trial_records.attrs.update(params)

        self.h5f.flush()


    def put_away(self):
        self.h5f.flush()
        self.h5f.close()



