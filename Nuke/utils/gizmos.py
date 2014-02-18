'''
- set gizmo path > export path to yaml file in same dir as this file (config.yml)
- read from config file
'''

import os

import nuke

import Tapp.System.yaml as uy

#method for setting gizmosPath
def setPath():
    gizmosPath=nuke.getFilename('Locate Gizmos directory.')
    
    if gizmosPath:
        data={}
        data['gizmosPath']=gizmosPath
        f=open(os.path.dirname(__file__)+'/'+'config.yml','w')
        uy.dump(data, f)
        f.close()
        
        gizmoMenuItems(gizmosPath)
        
def gizmoMenuItems(gizmosPath):
    #add gizmosPath
    nuke.pluginAddPath(gizmosPath)
    
    #adding menu items
    menubar = nuke.menu("Nuke")
    
    #removing existing menu
    if menubar.findItem('Tapp/Gizmos'):
        tappmenu=menubar.findItem('Tapp')
        tappmenu.removeItem('Gizmos')
    
    #building menu items
    for item in os.listdir(gizmosPath):
        name=item.split('.')[0]
        
        nuke.menu('Nuke').addCommand('Tapp/Gizmos/%s' % name,'nuke.createNode(\'%s\')' % name)

def loadGizmos():
    configFile=os.path.dirname(__file__)+'/'+'config.yml'
    
    if os.path.exists(configFile):
        f=open(configFile,'r')
        data=uy.load(f)
        
        if os.path.exists(data['gizmosPath']):
            gizmoMenuItems(data['gizmosPath'])
        else:
            nuke.message('Gizmos Path in config file is not valid!')
    else:
        nuke.message('No config file were found for Tapp Gizmos!')

#adding menu items
menubar = nuke.menu("Nuke")

nuke.menu('Nuke').addCommand('Tapp/Set Gizmos Path',setPath)
nuke.menu('Nuke').addCommand('Tapp/Load Gizmos',loadGizmos)

#loading gizmos
loadGizmos()