import os
from sys import platform as _platform

import maya.cmds as cmds

#query os and setting pluginpath according
if _platform == "linux" or _platform == "linux2":
    #havent got the linux version yet
    pass
    
elif _platform == "darwin":
    # OS X
    pluginpath=os.path.dirname(__file__)+'/build/osx/'
    
elif _platform == "win32":
    # Windows...
    pluginpath=os.path.dirname(__file__)+'/build/win/'

plugins=os.environ['MAYA_PLUG_IN_PATH']

os.environ['MAYA_PLUG_IN_PATH']=pluginpath

#load plugin
cmds.loadPlugin(allPlugins=True,quiet=True)

#revert plugin paths back, and adding pluginpath
os.environ['MAYA_PLUG_IN_PATH']=plugins+';'+pluginpath