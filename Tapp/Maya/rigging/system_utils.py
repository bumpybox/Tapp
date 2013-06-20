import maya.cmds as cmds

import Tapp.Maya.rigging.chain as mrc
reload(mrc)
import Tapp.Maya.rigging.meta as meta
reload(meta)
import Tapp.Maya.rigging.utils as mru
reload(mru)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler=logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(funcName)s - LINE: %(lineno)d - %(message)s'))
log.addHandler(handler)

def buildChain(obj):
    
    check=meta.r9Meta.MetaClass(obj)
    
    #build from guide---
    if isinstance(check,meta.r9Meta.MetaClass):
        
        log.debug('building a chain node from guide')
        
        chain=chainFromGuide(obj)
        #self.addRoot(obj,'master')
        
        return chain
        
    #build from system---
    if isinstance(check,meta.MetaSystem):
        
        log.debug('building a chain node from system')
        
        obj=meta.r9Meta.MetaClass(obj)
        
        for socket in obj.getChildMetaNodes(mAttrs='mClass=TappSocket'):
            if not socket.hasAttr('guideParent'):
                
                chain=chainFromSystem(socket)
                #chain.addRoot(obj.root,'master')
                #chain.addSystem(obj)
                
                return chain

def chainFromSystem(obj,parent=None):
    
    node=mrc.chain(obj)
    
    node.name=obj.data['name']
    
    data=obj.data
    del(data['name'])
    node.data=data
    
    #transforms
    node.translation=cmds.xform(obj.node,q=True,ws=True,translation=True)
    node.rotation=cmds.xform(obj.node,q=True,ws=True,rotation=True)
    node.scale=cmds.xform(obj.node,q=True,relative=True,scale=True)
    
    #parent and children
    node.parent=parent
    
    if obj.hasAttr('guideChildren'):
        for child in obj.guideChildren:
            node.addChild(chainFromSystem(child,parent=node))
        
        return node
    else:
        return node

def chainFromGuide(obj,parent=None):
    
    node=mrc.chain(obj)
    
    #getting name
    node.name=obj.split('|')[-1]
    
    #getting attr data
    data={}
    for attr in cmds.listAttr(obj,userDefined=True):
        data[attr]=cmds.getAttr(obj+'.'+attr)
    node.data=data
    
    #transforms
    node.translation=cmds.xform(obj,q=True,ws=True,translation=True)
    node.rotation=cmds.xform(obj,q=True,ws=True,rotation=True)
    node.scale=cmds.xform(obj,q=True,relative=True,scale=True)
    
    #parent and children
    node.parent=parent
    
    children=cmds.listRelatives(obj,children=True,fullPath=True,type='transform')
    
    if children:
        for child in children:
            node.addChild(chainFromGuide(child,parent=node))
        
        return node
    else:
        return node

#experimental---

def switch(objs,switchSystem):
    
    if objs:
        systems=[]
        for obj in objs:
            metaNode=meta.r9Meta.MetaClass(obj).getParentMetaNode()
            if metaNode:
                systems.append(metaNode.getParentMetaNode().mNode)
        
        systems=set(systems)
        for system in systems:
            system=meta.r9Meta.MetaClass(system)
            
            controls=system.getChildren(cAttrs='controls')
            
            #transforming controls to switch system
            currentSystem=None
            for control in controls:
                
                control=meta.r9Meta.MetaClass(control)
                
                if control.system=='extra':
                    for attr in cmds.listAttr(control.node,userDefined=True):
                        
                        if attr=='fk':
                            if cmds.getAttr(control.node[0]+'.fk'):
                                currentSystem='fk'
                        
                        if attr=='ik':
                            if cmds.getAttr(control.node[0]+'.ik'):
                                currentSystem='ik'
            
            if currentSystem:
                
                for control in controls:
                    
                    control=meta.r9Meta.MetaClass(control)
                    
                    if control.system!=currentSystem:
                        if control.hasAttr('switch'):
                            for switch in control.switch:
                                if switch.system==currentSystem:
                                    mru.Snap(switch.node[0], control.node[0])
            else:
                cmds.warning('No current system is active! Setting %s as active system.' % switchSystem)
            
            #blending to switch system
            for control in controls:
                
                control=meta.r9Meta.MetaClass(control)
                
                if control.system=='extra':
                    if switchSystem in cmds.listAttr(control.node,userDefined=True):
                        
                        cmds.setAttr(control.node[0]+'.'+switchSystem,1)
                    else:
                        cmds.warning('System "%s" was not found!' % switchSystem)
    else:
        cmds.warning('No objects found to switch!')

#switch(cmds.ls(selection=True),'fk')