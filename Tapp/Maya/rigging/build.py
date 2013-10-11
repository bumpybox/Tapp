'''
- plug parenting
- test switching
- test leg build
- better namespaces
- organize code better
- fails when not building any controls
- scaling feature
- build spline solver
'''

import Tapp.Maya.rigging.guide as mrg
reload(mrg)
import Tapp.Maya.rigging.solvers as mrs
reload(mrs)
import Tapp.Maya.rigging.meta as meta
reload(meta)
import Tapp.Maya.rigging.point as mrp

def constructor(points):
    
    #build system
    def getSolverPoints(point,ik=[],fk=[],points=[]):
        
        #adding to fk list
        if point.solverData['FK'] or point.controlData['FK']!='None':
            fk.append(point)
        
        #adding to ik list
        if point.solverData['IK'] or point.controlData['IK']!='None':
            ik.append(point)
        
        #adding to all list
        points.append(point)
        
        if point.children:
            for child in point.children:
                return getSolverPoints(child,ik=ik,fk=fk,points=points)
        else:
            return {'IK':ik,'FK':fk,'points':points}
    
    for point in points:
        mrs.system(point)
        mrs.replaceParentData(point)
        
        chains=getSolverPoints(point,ik=[],fk=[],points=[])
        
        index=points.index(point)
        
        if chains['IK']:
            mrs.IK(chains['IK'],'ik_%s_' % index)
        
        if chains['FK']:
            mrs.FK(chains['FK'],'fk_%s_' % index)
    
        #build blend
        mrs.blend(chains['points'], 'bld_%s_' % index)
    
    #static parenting
    for point in points:
        mrs.parent(point)

import maya.mel as mel
import maya.cmds as cmds

def destructor(preserve=False):
    
    points=meta.r9Meta.getMetaNodes(mTypes=['MetaPoint'])
    
    newPoints=[]
    for point in points:
        
        #creating point
        p=mrp.point()
        p.name=point.mNodeID
        
        #setting transform values
        socket=point.getChildMetaNodes(mAttrs='mClass=MetaSocket')[0]
        socketNode=socket.getNode()
        
        p.translation.set(cmds.xform(socketNode,q=True,ws=True,translation=True))
        p.rotation.set(cmds.xform(socketNode,q=True,ws=True,rotation=True))
        p.scale.set(cmds.xform(socketNode,q=True,ws=True,scale=True))
        
        #setting children
        children=point.getChildren(walk=False, cAttrs=['points'])
        for child in children:
            p.addChild(meta.r9Meta.MetaClass(child).mNodeID)
        
        #setting data
        p.controlData=point.controlData
        p.solverData=point.solverData
        
        if point.getChildren(walk=False, cAttrs=['parentData']):
            parent=point.getChildren(walk=False, cAttrs=['parentData'])[0]
            p.parentData=meta.r9Meta.MetaClass(parent).mNodeID
        
        newPoints.append(p)
    
    #replacing children and parentData
    for point in newPoints:
        
        for p in newPoints:
            if point.parentData==p.name:
                point.parentData=p
        
        for child in point.children:
            for p in newPoints:
                if child==p.name:
                    for n,i in enumerate(point.children):
                        if i==child:
                            point.children[n]=p
    
    #setting parent
    #possible very computational---
    def setParent(point,parent=None):
        
        if parent:
            point.parent=parent
        
        if point.children:
            for child in point.children:
                setParent(child,parent=point)
    
    for point in newPoints:
        setParent(point)
    
    result=[]
    for point in newPoints:
        if not point.parent:
            result.append(point)
    
    #deletion of nodes
    if not preserve:
        nodes=meta.r9Meta.getMetaNodes(mTypes=['MetaPoint','MetaSocket'])
        
        roots=[]    
        for node in nodes:
            
            metaNodes=meta.r9Meta.getConnectedMetaNodes(node.mNode,mTypes=['MetaPlug','MetaSocket','MetaControl'])
            
            if metaNodes:
                roots.append(mel.eval('rootOf("%s");' % metaNodes[0].getNode()))
            else:
                roots.append(mel.eval('rootOf("%s");' % node.getNode()))
        
        roots=list(set(roots))
        for root in roots:
            cmds.delete(root)
    
    return result

#points=destructor()
#mrg.constructor(points)
points=mrg.destructor()
constructor(points)