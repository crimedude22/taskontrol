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
        # TODO make this more robust for multiple tasks - saving position, etc.
        self.task = None
        if self.h5data.keys():
            last_assigned_task = self.h5data.keys()[-1]
            self.h5trial_records = self.h5data[last_assigned_task]
            self.task_type = self.h5trial_records.attrs['task_type']

            # Params can be described with a string for a template parameter set, load it if it was
            if 'param_template' in self.h5trial_records.attrs.keys():
                self.param_template = self.h5trial_records.attrs['param_template']

            param_dict = dict((key,value) for key,value in self.h5trial_records.attrs.iteritems() if not key == 'task_type')
            self.task_params = expand_dict(param_dict)

            self.load_protocol(self.task_type,self.task_params)

    def new_mouse(self,name):
        try:
            self.h5f = h5py.File(rpiset.PI_DATA_DIR + self.name + '.hdf5', 'w-')
        except:
            print("Mouse already has a file.")
            # TODO ask if user wants to redefine all params or just set new protocol.
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
        # TODO currently this would make a new dataset every time the mouse is loaded. Make this a "new protocol" function and have existing protocols loaded in a different fnxn.
        self.h5trial_records = self.h5data.create_dataset("trial_records",(10000,len(task_class.DATA_LIST)),maxshape=(None,len(task_class.DATA_LIST)))
        self.h5trial_records.attrs['task_type'] = protocol
        if isinstance(params,basestring):
            self.h5trial_records.attrs['param_template'] = params
            self.h5trial_records.attrs.update(flatten_dict(template_params))
        elif isinstance(params, dict):
            self.h5trial_records.attrs.update(flatten_dict(params))
        self.h5f.flush()

    def load_protocol(self,protocol,params):
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

    def receive_sounds(self,sounds,sound_lookup):
        # To be passed by RPilot after initing the Mouse
        self.task.sounds = sounds
        self.task.sound_lookup = sound_lookup
        # Update records with lookup table. Append date of lookup if conflicts
        if set(sound_lookup.items()).issubset(self.h5trial_records.attrs.items()):
            # Do nothing because we already have the lookup correctly stored
            pass
        elif bool(set(sound_lookup.keys()).intersection(self.h5trial_records.attrs.keys())):
            # If there are some shared keys, but the items are not a subset, then some of the values must differ or else we have new sounds.
            # Either way, we prepend date as a "proleptic Gregorian" date (day 1 of year 1 is 1, etc.) to avoid conflict.
            self.h5trial_records.attrs.update(flatten_dict(sound_lookup,parent_key="LU_{}_".format(datetime.date.today().toordinal())))
        else:
            # If nothing was in the above intersection check, we don't have any lookup data, so we just write it straight up
            self.h5trial_records.attrs.update(flatten_dict(sound_lookup,parent_key="LU_"))
        self.h5f.flush()



    def put_away(self):
        self.h5f.flush()
        self.h5f.close()


def flatten_dict(d, parent_key=''):
    """
    h5py has trouble with nested dicts which are likely to be common w/ complex params. Flatten a dict s.t.:
        {
    Lifted from : http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys/6043835#6043835
    """
    items = []
    for k, v in d.items():
        try:
            if type(v) == type([]):
                for n, l in enumerate(v):
                    items.extend(flatten_dict(l, '%s%s.%s.' % (parent_key, k, n)).items())
            else:
                items.extend(flatten_dict(v, '%s%s.' % (parent_key, k)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)


def expand_dict(d):
    """
    Recover flattened dicts
    """
    items = dict()
    for k,v in d.items():
        if len(k.split('.'))>1:
            current_level = items
            for i in k.split('.')[:-1]: #all but the last entry
                try:
                    # If we come across an integer, we make a list of dictionaries
                    i_int = int(i)
                    if not isinstance(current_level[j],list):
                        current_level[j] = list() # get the last entry and make it a list
                    if i_int >= len(current_level[j]): # If we haven't populated this part of the list yet, fill.
                        current_level[j].extend(None for _ in range(len(current_level[j]),i_int+1))
                    if not isinstance(current_level[j][i_int],dict):
                        current_level[j][i_int] = dict()
                    current_level = current_level[j][i_int]
                except ValueError:
                    # Otherwise, we make a sub-dictionary
                    try:
                        current_level = current_level[j]
                    except:
                        pass
                    if i not in current_level:
                        current_level[i] = {}
                    j = i #save this entry so we can enter it next round if it's not a list
                    # If the last entry, enter the dict
                    if i == k.split('.')[-2]:
                        current_level = current_level[i]
            current_level[k.split('.')[-1]] = v
        else:
            items[k] = v
    return items


