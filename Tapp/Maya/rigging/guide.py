'''

- change constructor input to points which are always a list

'''

import maya.cmds as cmds

import Tapp.Maya.rigging.point as mrp
reload(mrp)

controlValues=['None','Square','FourWay','Circle',
               'Box','Pin','Sphere']
solverValues=['None','Start','End']

def constructor(data=None):
    
    def createGuide(point):
        #build
        node=cmds.createNode('implicitSphere')
        node=cmds.listRelatives(node,parent=True)
        
        if point.name:
            node=cmds.rename(node,point.name)
        else:
            node=cmds.rename(node,'guide')
        
        point.name=node
        
        cmds.addAttr(node,ln='IK_control',at='enum',k=True,enumName=':'.join(controlValues))
        cmds.addAttr(node,ln='FK_control',at='enum',k=True,enumName=':'.join(controlValues))
        if point.controlData:
            for attr in point.controlData:
                cmds.setAttr(node+'.'+attr,controlValues.index(point.controlData[attr]))
        
        cmds.addAttr(node,ln='IK_solver',at='enum',k=True,enumName=':'.join(solverValues))
        cmds.addAttr(node,ln='FK_solver',at='enum',k=True,enumName=':'.join(solverValues))
        if point.solverData:
            for attr in point.solverData:
                cmds.setAttr(node+'.'+attr,solverValues.index(point.solverData[attr]))
        
        if point.parentData:
            if isinstance(point.parentData,mrp.point):
                cmds.addAttr(node,ln='parent',at='enum',k=True,enumName=point.parentData.name)
            else:
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
            print point
            for child in point.children:
                constructor(data=child)
    
    #if no points are passed in
    if not data:
        point=mrp.point()
        
        return [createGuide(point)]
    
    if isinstance(data,list):
        
        result=[]
        for p in data:
            result.append(createGuide(p))
        
        return result
    elif isinstance(data,mrp.point):
        createGuide(data)

def destructor(obj=None):
    
    def createPoint(obj,parent=None):
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
                        p.addChild(createPoint(child,parent=p))
                    
                    return p
                else:
                    return p
    
    def findName(point,name):
        
        if point.name==name:
            
            return point
        
        if point.children:
            for child in point.children:
                return findName(child,name)
    
    def replaceParent(point,nodes):
        
        if point.parentData!='None':
            
            for node in nodes:
                result=findName(node,point.parentData)
                if result:
                    point.parentData=result
        
        if point.children:
            for child in point.children:
                replaceParent(child,nodes)
    
    result=[]      
    if not obj:
        
        roots=[]
        for node in cmds.ls(type='implicitSphere',long=True):
            roots.append(node.split('|')[1])
        
        roots=list(set(roots))
        
        for node in roots:
            result.append(createPoint(node))
        
    else:
        result.append(createPoint(obj))
    
    for point in result:
        replaceParent(point,result)
    
    return result