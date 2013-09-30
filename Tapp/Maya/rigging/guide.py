import maya.cmds as cmds

import Tapp.Maya.rigging.point as mrp
reload(mrp)

controlValues=['None','Square','FourWay','Circle',
               'Box','Pin','Sphere']
solverValues=['None','Start','End']

def constructor(point=None):
    
    #if no points are passed in
    if not point:
        point=mrp.point()
    
    #build
    node=cmds.createNode('implicitSphere')
    node=cmds.listRelatives(node,parent=True)
    
    if point.name:
        node=cmds.rename(node,point.name)
    else:
        node=cmds.rename(node,'guide')
    
    cmds.addAttr(node,ln='IK_control',at='enum',k=True,enumName=':'.join(controlValues))
    cmds.addAttr(node,ln='FK_control',at='enum',k=True,enumName=':'.join(controlValues))
    if point.controlData:
        for attr in point.controlData:
            cmds.setAttr(node+'.'+attr,controlValues.index(point.controlData[attr]))
    
    cmds.addAttr(node,ln='IK_solver',at='enum',k=True,enumName=':'.join(solverValues))
    if point.solverData:
        for attr in point.solverData:
            cmds.setAttr(node+'.'+attr,solverValues.index(point.solverData[attr]))
    
    if point.parentData:
        cmds.addAttr(node,ln='parent',at='enum',k=True,enumName=point.parentData)
    else:
        cmds.addAttr(node,ln='parent',at='enum',k=True,enumName='None')
    
    #transforming
    cmds.xform(node,ws=True,translation=point.translation)
    cmds.xform(node,ws=True,rotation=point.rotation)
    cmds.xform(node,ws=True,scale=point.scale)
    
    #parenting
    if point.parent:
        point.node=cmds.parent(node,point.parent.node)
    else:
        point.node=node
    
    #children
    if point.children:
        
        for child in point.children:
            constructor(point=child)

def destructor(obj,parent=None):
    
    for node in cmds.listRelatives(obj):
        
        if cmds.nodeType(node)=='implicitSphere':
            
            #initialize point object
            p=mrp.point()
            
            #setting name
            p.name=obj.split('|')[-1]
            
            #setting data
            controlData={}
            solverData={}
            parentData=None
            for attr in cmds.listAttr(obj,userDefined=True):
                
                if attr=='parent':
                    
                    values=cmds.attributeQuery( attr, node=obj, listEnum=True )[0].split(':')
                    parentData=values[cmds.getAttr(obj+'.'+attr)]
                
                if attr.split('_')[-1]=='control':
                    
                    controlData[attr]=controlValues[cmds.getAttr(obj+'.'+attr)]
                
                if attr.split('_')[-1]=='solver':
                    
                    solverData[attr]=solverValues[cmds.getAttr(obj+'.'+attr)]
            
            p.controlData=controlData
            p.solverData=solverData
            p.parentData=parentData
            
            #transforms
            p.translation.set(cmds.xform(obj,q=True,ws=True,translation=True))
            p.rotation.set(cmds.xform(obj,q=True,ws=True,rotation=True))
            p.scale.set(cmds.xform(obj,q=True,relative=True,scale=True))
            
            #parent and children
            p.parent=parent
            
            children=cmds.listRelatives(obj,children=True,fullPath=True,type='transform')
            
            if children:
                for child in children:
                    p.addChild(destructor(child,parent=p))
                
                return p
            else:
                return p

node=destructor('|clavicle')

constructor(node)
constructor()