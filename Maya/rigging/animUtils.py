import maya.cmds as cmds

import Tapp.Maya.rigging.utils as mru
import Tapp.Maya.rigging.meta as meta
reload(meta)

sel=cmds.ls(selection=True)

def switch(point,targetSystem):
    
    socket=point.getSocket().getNode()
    
    #snapping target system control to socket
    for control in point.getControls():
        
        if control.system==targetSystem:
            mru.Snap(socket, control.getNode())
    
    #continuing with child points
    if point.getPoints():
        for child in point.getPoints():
            switch(child,targetSystem)
    #setting target system as active system
    else:
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

for node in sel:
    
    point=meta.r9Meta.getConnectedMetaSystemRoot(node)
    
    switch(point,'FK')