import os
import sys

import maya.cmds as cmds

import Tapp.Maya.rigging.modules as mrm
import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.config as mrc

def __importModule__(module):
    modulesPath=mrc.config['modules'].replace('\\','/')
    modulePath=modulesPath+'/'+module+'.py'
    
    f = os.path.basename( modulePath )
    d = os.path.dirname( modulePath )
 
    toks = f.split( '.' )
    modname = toks[0]
 
    # Check if dirrectory is really a directory
    if( os.path.exists( d ) ):
 
    # Check if the file directory already exists in the sys.path array
        paths = sys.path
        pathfound = 0
        for path in paths:
            if(d == path):
                pathfound = 1
 
    # If the dirrectory is not part of sys.path add it
        if not pathfound:
            sys.path.append( d )
 
    # exec works like MEL's eval but you need to add in globals() 
    # at the end to make sure the file is imported into the global 
    # namespace else it will only be in the scope of this function
    exec ('import ' + modname+' as mrm') in globals()

def Connect():
    
    sel=cmds.ls(selection=True)
    
    #collecting modules
    modules=[]
    
    for node in sel:
        modules.append(mum.UpStream(node, 'module'))
    
    #connecting modules
    if len(modules)>1:
        
        childModules=modules[0:-1]
        parentModule=modules[-1]
        
        for module in childModules:
            
            #importing module
            data=mum.GetData(module)
            
            __importModule__(data['component'])
            
            #attaching modules
            mrm.Attach(module, parentModule)
    else:
        cmds.warning('Not enough modules selected!')

def Hide():
    for node in cmds.ls():
        if cmds.nodeType(node)=='nurbsCurve':
            p=cmds.listRelatives(node,p=True)[0]
            if (cmds.attributeQuery('metaParent',n=p,ex=True))==False:
                cmds.setAttr('%s.visibility' % node,False)
        if cmds.nodeType(node)=='locator':
            cmds.setAttr('%s.visibility' % node,False)
        if cmds.nodeType(node)=='ikHandle':
            cmds.setAttr('%s.visibility' % node,False)
        if cmds.nodeType(node)=='cluster':
            p=cmds.listConnections(node+'.matrix')[0]
            cmds.setAttr('%s.visibility' % p,False)
        if cmds.nodeType(node)=='joint':
            cmds.setAttr('%s.drawStyle' % node,2)

def Unhide():
    for node in cmds.ls():
        if cmds.nodeType(node)=='nurbsCurve':
            p=cmds.listRelatives(node,p=True)[0]
            if (cmds.attributeQuery('metaParent',n=p,ex=True))==False:
                cmds.setAttr('%s.visibility' % node,True)
        if cmds.nodeType(node)=='locator':
            cmds.setAttr('%s.visibility' % node,True)
        if cmds.nodeType(node)=='ikHandle':
            cmds.setAttr('%s.visibility' % node,True)
        if cmds.nodeType(node)=='cluster':
            p=cmds.listConnections(node+'.matrix')[0]
            cmds.setAttr('%s.visibility' % p,True)
        if cmds.nodeType(node)=='joint':
            cmds.setAttr('%s.drawStyle' % node,0)

def Unblackbox():
    
    for node in cmds.ls(type='container'):
        
        cmds.setAttr(node+'.blackBox',0)

def Blackbox():
    
    for node in cmds.ls(type='container'):
        
        cmds.setAttr(node+'.blackBox',1)