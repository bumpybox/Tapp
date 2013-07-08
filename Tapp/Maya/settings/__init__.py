import maya.cmds as cmds

import Tapp.utils.yaml as uy
import Tapp.Maya.window as win

def getSettings():
    
    settingsFile=cmds.internalVar(upd=True)+'Tapp.yml'
    f=open(settingsFile,'r')
    
    settings=uy.load(f)
    
    return settings

def setSettings(data):
    
    settingsFile=cmds.internalVar(upd=True)+'Tapp.yml'
    f=open(settingsFile,'w')
    
    uy.dump(data, f)

def startup():
    
    settings=getSettings()
    
    if settings['launchWindowAtStartup']==True:
        win.show()