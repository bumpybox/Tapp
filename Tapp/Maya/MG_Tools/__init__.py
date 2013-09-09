import os
from sys import platform as _platform
import shutil

import maya.cmds as cmds

#checking existing plugin
if not cmds.pluginInfo("MG_rigToolsPro",q=1,loaded=1):

    #query os and setting pluginpath according
    if _platform == "linux" or _platform == "linux2":
        #havent got the linux version yet
        pass
        
    elif _platform == "darwin":
        # OS X
        pluginpath=os.path.dirname(__file__)+'/build/1_2/osx/'
        
    elif _platform == "win32":
        # Windows...
        pluginpath=os.path.dirname(__file__)+'/build/1_2/win/'
    
    #query maya version
    mayaversion=cmds.about(version=True)
    
    if mayaversion=='2012 x64':
        
        pluginpath+='2012x64/'
    
    elif mayaversion=='2013 x64':
        
        pluginpath+='2013x64/'
    
    elif mayaversion=='2014 x64':
        
        pluginpath+='2014x64/'
    
    #copying plugin to one of plugin paths
    path=os.environ['MAYA_PLUG_IN_PATH'].split(';')[0]
    
    #checking folder
    if not os.path.exists(path):
        os.makedirs(path)
    
    #copying plugin
    shutil.copy2(pluginpath+'MG_rigToolsPro.mll', path)
    
    #storing and replacing plugins path
    plugins=os.environ['MAYA_PLUG_IN_PATH']
    
    os.environ['MAYA_PLUG_IN_PATH']=path
    
    #load plugin
    cmds.loadPlugin(allPlugins=True,quiet=True)
    
    cmds.pluginInfo('MG_rigToolsPro.mll',e=True,a=True)
    
    #revert plugin paths back, and adding pluginpath
    os.environ['MAYA_PLUG_IN_PATH']=plugins