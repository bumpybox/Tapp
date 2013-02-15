import os
import sys

import maya.cmds as cmds

import Tapp.Maya.rigging.modules as mrm
import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.config as mrc
import Tapp.Maya.rigging.utils as mru

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

def Delete():
    
    sel=cmds.ls(selection=True)
    
    if len(sel)<=0:
        cmds.warning('No modules selected!\nSelect a module to delete.')
    else:
        
        modules=[]
        roots=[]
        
        for node in sel:
            modules.append(mum.UpStream(node, 'module'))
            roots.append(mum.UpStream(node, 'root'))
        
        for module in modules:
            if module!=None:
                mru.Detach(module, detachChildren=True)
                
                cnt=mum.DownStream(module, 'control')[0]
                tn=mum.GetTransform(cnt)
                
                cmds.delete(cmds.container(q=True,fc=tn))
        
        for root in roots:
            if root!=None:
                cnt=mum.DownStream(root, 'control')[0]
                tn=mum.GetTransform(cnt)
                
                cmds.delete(cmds.container(q=True,fc=tn))

def Create(module):
    
    __importModule__(module)
    
    return mrm.Create()

def Rig():
    ''' Rigs all modules in the scene. '''
    
    cmds.undoInfo(openChunk=True)
        
    sel=cmds.ls(selection=True)
    
    if len(sel)<=0:
        message='No modules are selected!\nDo you want to rig all modules in scene?'
        reply=cmds.confirmDialog( title='Rig Modules',
                                  message=message,
                                  button=['Yes','No'],
                                  defaultButton='Yes',
                                  cancelButton='No')
        
        if reply=='Yes':
            
            #rigging all modules in the scene
            modules=[]
            for meta in cmds.ls(type='network'):
                data=mum.GetData(meta)
                
                if data['type']=='root':
                    modules.append(meta)
            
            for module in modules:
                __rig__(module)
    
    else:
        #collecting modules
        modules=[]
        
        for node in sel:
            modules.append(mum.UpStream(node, 'root'))
        
        #removing duplicates
        modules=list(set(modules))
        
        for module in modules:
            __rig__(module)
    
    cmds.undoInfo(closeChunk=True)

def __rig__(module):
    ''' Rigs the provided module. '''
    
    cmds.undoInfo(openChunk=True)
    
    data=mum.GetData(module)
    moduleName=data['component']
    
    __importModule__(moduleName)
    
    mrm.Rig(module)
    
    cmds.undoInfo(closeChunk=True)

def SetWorld():
    ''' Sets the world for the selected modules. '''
    
    cmds.undoInfo(openChunk=True)
    
    sel=cmds.ls(selection=True)
    
    #collecting modules
    modules=[]
    
    for node in sel:
        modules.append(mum.UpStream(node, 'module'))
    
    #connecting modules
    #if no modules selected
    if len(modules)>1:
        
        #if two modules selected
        if len(modules)>2:
            
            childModules=modules[0:-1]
            parentModule=modules[-1]
            
            for module in childModules:
                
                #importing module
                data=mum.GetData(module)
                
                __importModule__(data['component'])
                
                #setting world for modules
                mrm.SetWorld(module, parentModule)
        else:
            module=modules[0]
            parentModule=modules[-1]
            
            message='Only one child module selected.\nDo you want to set world on downstream modules?'
            reply=cmds.confirmDialog( title='Set World',
                                      message=message,
                                      button=['Yes','No'],
                                      defaultButton='Yes',
                                      cancelButton='No')
            
            if reply=='Yes':
                
                #importing module
                data=mum.GetData(module)
                
                __importModule__(data['component'])
                
                #setting world for modules
                mrm.SetWorld(module, parentModule,downStream=True)
            else:
                
                #importing module
                data=mum.GetData(module)
                
                __importModule__(data['component'])
                
                #setting world for modules
                mrm.SetWorld(module, parentModule)
    else:
        cmds.warning('Not enough modules selected!')
    
    cmds.undoInfo(closeChunk=True)

def Mirror():
    ''' Mirrors modules across YZ axis. '''
    
    cmds.undoInfo(openChunk=True)
        
    sel=cmds.ls(selection=True)
    
    if len(sel)<=0:
        cmds.warning('No modules selected!\nSelect a module to mirror.')
    else:
        #collecting modules
        modules=[]
        
        for node in sel:
            modules.append(mum.UpStream(node, 'root'))
        
        #removing duplicates
        modules=list(set(modules))
        
        for module in modules:
            __mirror__(module)
    
    cmds.undoInfo(closeChunk=True)

def __mirror__(module):
    ''' Mirrors provided module across YZ axis. '''
    
    #getting module data
    mData=mum.GetData(module)
    
    cnts=mum.DownStream(module, 'control')
    
    container=cmds.container(q=True,fc=mum.GetTransform(cnts[0]))
    
    #getting imported controls
    importCnts=[]
    
    importNodes=Create(mData['component'])
    
    for node in importNodes:
        if cmds.nodeType(node)=='network':
            data=mum.GetData(node)
            if data['type']=='control':
                importCnts.append(node)
    
    #copy container values
    icontainer=cmds.container(q=True,fc=mum.GetTransform(importCnts[0]))
    
    cmds.copyAttr(container,icontainer,values=True)
    
    #pairing controls
    cntPairs={}
    
    for cnt in cnts:
        data=mum.GetData(cnt)
        for iCnt in importCnts:
            iData=mum.GetData(iCnt)
            
            if iData['component']==data['component']:
                cntPairs[cnt]=iCnt
    
    #mirroring translation and rotation
    for cnt in cntPairs:
        
        tn=mum.GetTransform(cnt)
        
        [tx,ty,tz]=cmds.xform(tn,ws=True,query=True,translation=True)
        [rx,ry,rz]=cmds.xform(tn,ws=True,query=True,rotation=True)
        
        itn=mum.GetTransform(cntPairs[cnt])
        
        cmds.xform(itn,ws=True,translation=(-tx,ty,tz))
        cmds.xform(itn,ws=True,rotation=(rx,-ry,-rz))