import maya.cmds as cmds

import Red9.core.Red9_Meta as r9Meta
import Tapp.Maya.rigging.meta as meta
import Tapp.Maya.rigging.utils as mru
reload(mru)
import Tapp.Maya.rigging.chain as mrc
reload(mrc)

def buildSystem(chain):
    
    #meta rig
    system=meta.MetaSystem()
    
    chain.addSystem(system)
    
    #storing guide data
    data=chainToDict(chain)
    system.addAttr('guideData', data)

def chainToDict(node):
    
    result=node.__dict__.copy()
    
    del(result['system'])
    del(result['parent'])
    
    if node.children:
        
        children=[]
        
        for child in node.children:
            children.append(chainToDict(child))
        
        result['children']=children
    
    return result

def dictToChain(dictionary,parent=None):
    
    node=mrc.chain()
    
    #getting data
    node.name=dictionary['name']
    node.data=dictionary['data']
    
    #transforms
    node.translation=dictionary['translation']
    node.rotation=dictionary['rotation']
    node.scale=dictionary['scale']
    
    #parent and children
    node.parent=parent
    
    children=dictionary['children']
    
    if children:
        for child in children:
            node.addChild(dictToChain(child,parent=node))
        
        return node
    else:
        return node

def deleteSource(chain):
    if chain.plug:
        
        cmds.delete(chain.plug['master'])
        chain.removePlug('master')
    
    if chain.system:
        for control in chain.system.getChildren(cAttrs='controls'):
            r9Meta.MetaClass(control).delete()
            
        for socket in chain.system.getChildren(cAttrs='sockets'):
            r9Meta.MetaClass(socket).delete()
        
        chain.system.delete()
        chain.removeSystem()

def buildChain(obj,log):
    
    check=r9Meta.MetaClass(obj)
    
    #build from system---
    if type(check)==meta.MetaSystem:
        
        log.debug('building chain from system')
        
        chain=dictToChain(check.guideData)
        
        return chain
    
    #build from guide---
    if type(check)==r9Meta.MetaClass:
        
        log.debug('building chain from guide')
        
        chain=chainFromGuide(obj)
        chain.addPlug(obj,'master')
        
        return chain

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
            metaNode=r9Meta.MetaClass(obj).getParentMetaNode()
            if metaNode:
                systems.append(metaNode.getParentMetaNode().mNode)
        
        systems=set(systems)
        for system in systems:
            system=r9Meta.MetaClass(system)
            
            controls=system.getChildren(cAttrs='controls')
            
            #transforming controls to switch system
            currentSystem=None
            for control in controls:
                
                control=r9Meta.MetaClass(control)
                
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
                    
                    control=r9Meta.MetaClass(control)
                    
                    if control.system!=currentSystem:
                        if control.hasAttr('switch'):
                            for switch in control.switch:
                                if switch.system==currentSystem:
                                    mru.Snap(switch.node[0], control.node[0])
            else:
                cmds.warning('No current system is active! Setting %s as active system.' % switchSystem)
            
            #blending to switch system
            for control in controls:
                
                control=r9Meta.MetaClass(control)
                
                if control.system=='extra':
                    if switchSystem in cmds.listAttr(control.node,userDefined=True):
                        
                        cmds.setAttr(control.node[0]+'.'+switchSystem,1)
                    else:
                        cmds.warning('System "%s" was not found!' % switchSystem)
    else:
        cmds.warning('No objects found to switch!')

#switch(cmds.ls(selection=True),'fk')