import maya.cmds as cmds

import Tapp.Maya.rigging.meta as meta
import Tapp.Maya.rigging.utils as mru

def switch(mode,timeRange=False,start=0,end=0):
    
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #error checking for selection count
    nodeSelection=cmds.ls(selection=True)
    
    if len(nodeSelection)>=1:
        
        #time based switching
        if timeRange:
            
            for count in xrange(start,end):
                
                cmds.currentTime(count)
                
                for node in nodeSelection:
                    point=meta.r9Meta.getConnectedMetaSystemRoot(node)
                    
                    snap(point,mode)
            
            for node in nodeSelection:
                point=meta.r9Meta.getConnectedMetaSystemRoot(node)
                
                activate(point,mode)
        
        #non time based switching
        else:
            
            for node in nodeSelection:
            
                point=meta.r9Meta.getConnectedMetaSystemRoot(node)
                
                snap(point,mode)
                
                activate(point,mode)
    
    else:
        cmds.warning('Nothing is selected!')
    
    cmds.undoInfo(closeChunk=True)

def activate(point,targetSystem):
    
    root=meta.r9Meta.getConnectedMetaSystemRoot(point.mNode)
    
    #collecting controls
    controls=root.getControls()
    for control in root.getChildControls():
        controls.append(control)
    
    #collecting systems
    systems=[]
    for control in controls:
        systems.append(control.system)
    
    systems=list(set(systems))
    
    #finding extra control
    for control in controls:
        
        if control.system=='extra':
            
            node=control.getNode()
            
            for system in systems:
                
                #activating target system
                if system==targetSystem:
                    cmds.setAttr(node+'.'+system,1)
                
                #deactivating all other systems
                if system!='extra' and system!=targetSystem:
                    cmds.setAttr(node+'.'+system,0)

def snap(point,targetSystem):
    
    socket=point.getSocket().getNode()
    
    #snapping target system control to socket
    for control in point.getControls():
        
        if control.system==targetSystem:
            
            mru.Snap(socket, control.getNode())
            cmds.setKeyframe(control.getNode())
    
    #continuing with child points
    if point.getPoints():
        for child in point.getPoints():
            snap(child,targetSystem)

def __zeroNode__(node):
    if (cmds.getAttr('%s.tx' % node,lock=True))!=True:
        cmds.setAttr('%s.tx' % node,0)
    if (cmds.getAttr('%s.ty' % node,lock=True))!=True:
        cmds.setAttr('%s.ty' % node,0)
    if (cmds.getAttr('%s.tz' % node,lock=True))!=True:
        cmds.setAttr('%s.tz' % node,0)
    if (cmds.getAttr('%s.rx' % node,lock=True))!=True:
        cmds.setAttr('%s.rx' % node,0)
    if (cmds.getAttr('%s.ry' % node,lock=True))!=True:
        cmds.setAttr('%s.ry' % node,0)
    if (cmds.getAttr('%s.rz' % node,lock=True))!=True:
        cmds.setAttr('%s.rz' % node,0)

def ZeroControl():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #zero controls
    if len(sel)>=1:
        for node in cmds.ls(sl=True):
            __zeroNode__(node)
        
        #revert selection
        cmds.select(sel)
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

'''
def ZeroLimb():
    #failsafe on non-modular nodes selected
    
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #zero limb
    if len(sel)>=1:
        modules=[]
        for node in sel:
            modules.append(mum.UpStream(node, 'module'))
        
        if len(modules)>=1:
            modules=set(modules)
            for module in modules:
                cnts=mum.DownStream(module, 'control')
                
                for cnt in cnts:
                    tn=mum.GetTransform(cnt)
                    
                    __zeroNode__(tn)
        else:
            cmds.warning('Could not find any limbs connected to the selected nodes.')
        
        #revert selection
        cmds.select(sel)
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def ZeroCharacter():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #zero character
    if len(sel)>=1:
        root=mum.UpStream(sel[0], 'root')
        
        if root!=None:
            cnts=mum.DownStream(root, 'control', allNodes=True)
            for cnt in cnts:
                tn=mum.GetTransform(cnt)
                
                __zeroNode__(tn)
        else:
            cmds.warning('Could not find any character connected to the selected nodes.')
    
        #revert selection
        cmds.select(sel)
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def KeyLimb():
    
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #key limb
    if len(sel)>=1:
        modules=[]
        for node in sel:
            modules.append(mum.UpStream(node, 'module'))
        
        if len(modules)>=1:
            modules=set(modules)
            for module in modules:
                cnts=mum.DownStream(module, 'control')
                
                for cnt in cnts:
                    tn=mum.GetTransform(cnt)
                    
                    cmds.setKeyframe(tn)
        else:
            cmds.warning('Could not find any limbs connected to the selected nodes.')
        
        #revert selection
        cmds.select(sel)
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def KeyCharacter():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #zero character
    if len(sel)>=1:
        root=mum.UpStream(sel[0], 'root')
        
        if root!=None:
            cnts=mum.DownStream(root, 'control', allNodes=True)
            for cnt in cnts:
                tn=mum.GetTransform(cnt)
                
                cmds.setKeyframe(tn)
        else:
            cmds.warning('Could not find any character connected to the selected nodes.')
        
        #revert selection
        cmds.select(sel)
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def SelectLimb():
    
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #key limb
    if len(sel)>=1:
        modules=[]
        for node in sel:
            modules.append(mum.UpStream(node, 'module'))
        
        cmds.select(cl=True)
        
        if len(modules)>=1:
            modules=set(modules)
            for module in modules:
                cnts=mum.DownStream(module, 'control')
                
                for cnt in cnts:
                    tn=mum.GetTransform(cnt)
                    
                    cmds.select(tn,add=True)
        else:
            cmds.warning('Could not find any limbs connected to the selected nodes.')
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)

def SelectCharacter():
    #undo enable
    cmds.undoInfo(openChunk=True)
    
    #getting selection
    sel=cmds.ls(sl=True)
    
    #zero character
    if len(sel)>=1:
        root=mum.UpStream(sel[0], 'root')
        
        cmds.select(cl=True)
        
        if root!=None:
            cnts=mum.DownStream(root, 'control', allNodes=True)
            for cnt in cnts:
                tn=mum.GetTransform(cnt)
                
                cmds.select(tn,add=True)
        else:
            cmds.warning('Could not find any character connected to the selected nodes.')
    else:
        cmds.warning('No nodes select!')
    
    cmds.undoInfo(closeChunk=True)
    '''