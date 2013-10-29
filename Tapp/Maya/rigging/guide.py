'''
- need to involve dependant parents
'''

import maya.cmds as cmds

import Tapp.Maya.rigging.point as mrp
reload(mrp)

controlValues=['None','Square','FourWay','Circle',
               'Box','Pin','Sphere']

def constructor(points=[]):
    
    def createGuide(point):
        #build
        node=cmds.createNode('implicitSphere')
        node=cmds.listRelatives(node,parent=True)
        
        if point.name:
            node=cmds.rename(node,point.name)
        else:
            node=cmds.rename(node,'guide')
        
        point.name=node
        
        if point.controlData:
            for system in point.controlData:
                cmds.addAttr(node,ln=system+'_control',at='enum',k=True,enumName=':'.join(controlValues))
                
                if point.controlData[system]:
                    cmds.setAttr(node+'.'+system+'_control',controlValues.index(point.controlData[system]))
        else:
            cmds.addAttr(node,ln='IK_control',at='enum',k=True,enumName=':'.join(controlValues))
            cmds.addAttr(node,ln='FK_control',at='enum',k=True,enumName=':'.join(controlValues))
        
        if point.solverData:
            for system in point.solverData:
                cmds.addAttr(node,ln=system+'_solver',at='bool',k=True)
                cmds.setAttr(node+'.'+system+'_solver',point.solverData[system])
        else:
            cmds.addAttr(node,ln='IK_solver',at='bool',k=True)
            cmds.addAttr(node,ln='FK_solver',at='bool',k=True)
        
        if point.parentData:
            
            cmds.addAttr(node,ln='parent',at='enum',k=True,
                         enumName=':'.join(['None',point.parentData.longname]),defaultValue=1)
        else:
            cmds.addAttr(node,ln='parent',at='enum',k=True,enumName='None')
        
        #transforming
        cmds.xform(node,ws=True,translation=point.translation)
        cmds.xform(node,ws=True,rotation=point.rotation)
        cmds.xform(node,ws=True,scale=point.scale)
        
        #size
        cmds.addAttr(node,ln='size',at='float',k=True)
        
        shape=cmds.listRelatives(node,shapes=True,fullPath=True)[0]
        
        cmds.connectAttr(node+'.size',shape+'.radius')
        
        cmds.setAttr(node+'.size',point.size)
        
        #parenting
        if point.parent:
            point.node=cmds.parent(node,point.parent.node)
        else:
            point.node=node
        
        #children
        if point.children:
            for child in point.children:
                return constructor(points=[child])
        else:
            return node
    
    #if no points are passed in
    if not points:
        point=mrp.point()
        
        return [createGuide(point)]
    
    #if a list is passed in
    if isinstance(points,list):
        
        result=[]
        for p in points:
            result.append(createGuide(p))
        
        return result

def destructor(obj=None,preserve=False):
    
    def createPoint(obj,parent=None):
        for node in cmds.listRelatives(obj,fullPath=True):
            
            if cmds.nodeType(node)=='implicitSphere':
                
                #initialize point object
                p=mrp.point()
                
                #setting name
                p.name=obj.split('|')[-1]
                
                #setting long name
                p.longname=cmds.ls(obj,long=True)[0]
                
                #setting data
                controlData={}
                solverData={}
                parentData=None
                for attr in cmds.listAttr(obj,userDefined=True):
                    
                    if attr=='parent':
                        
                        values=cmds.attributeQuery( attr, node=obj, listEnum=True )[0].split(':')
                        parentData=values[cmds.getAttr(obj+'.'+attr)]
                    
                    if attr.split('_')[-1]=='control':
                        
                        value=controlValues[cmds.getAttr(obj+'.'+attr)]
                        
                        if value=='None':
                            controlData[attr.split('_')[0]]=None
                        else:
                            controlData[attr.split('_')[0]]=value
                    
                    if attr.split('_')[-1]=='solver':
                        
                        solverData[attr.split('_')[0]]=cmds.getAttr(obj+'.'+attr)
                
                p.controlData=controlData
                p.solverData=solverData
                p.parentData=parentData
                
                #transforms
                p.translation.set(cmds.xform(obj,q=True,ws=True,translation=True))
                p.rotation.set(cmds.xform(obj,q=True,ws=True,rotation=True))
                
                #size
                p.size=cmds.getAttr(obj+'.size')
                
                #parent and children
                p.parent=parent
                
                children=cmds.listRelatives(obj,children=True,fullPath=True,type='transform')
                
                if children:
                    for child in children:
                        p.addChild(createPoint(child,parent=p))
                    
                    return p
                else:
                    return p
    
    def findName(point,longname):
        
        if point.longname==longname:
            
            return point
        
        if point.children:
            for child in point.children:
                return findName(child,longname)
    
    def replaceParent(point,nodes):
        
        if point.parentData!='None':
            
            for node in nodes:
                result=findName(node,point.parentData)
                if result:
                    point.parentData=result
        else:
            point.parentData=None
        
        if point.children:
            for child in point.children:
                replaceParent(child,nodes)
    
    result=[]      
    if not obj:
        
        roots=[]
        for node in cmds.ls(type='implicitSphere',long=True):
            roots.append('|'+node.split('|')[1])
        
        roots=list(set(roots))
        
        for node in roots:
            result.append(createPoint(node))
        
        if not preserve:
            cmds.delete(roots)
        
    else:
        
        if isinstance(obj,list):
            for point in obj:
                result.append(createPoint(point))
        
        if not preserve:
            cmds.delete(obj)
    
    for point in result:
        replaceParent(point,result)
    
    #parent checking
    def checkParent(point):
        
        if isinstance(point.parentData,unicode):
            print 'WARNING! %s has string for parent!' % point.name
        
        if point.children:
            for child in point.children:
                checkParent(child)
    
    for point in result:
        checkParent(point)
    
    return result

'''
points=destructor(preserve=True)

def printPoint(point):
    
    print point.name
    print point.longname
    print point.controlData
    print point.solverData
    print point.parentData
    print '----'
    
    if point.children:
        for child in point.children:
            printPoint(child)
    else:
        print 'end of chain!!!!!!!!!!!!!!!!!!!!'

for point in points:
    printPoint(point)
    '''