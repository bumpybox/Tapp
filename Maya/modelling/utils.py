import maya.cmds as cmds

import Tapp.Maya.rigging.utils as mru

def MidPosition(posA,posB):
    ''' Calculates the middle position between posA and posB '''
    
    posX=(posA[0]+posB[0])/2
    posY=(posA[1]+posB[1])/2
    posZ=(posA[2]+posB[2])/2
    
    midPos=[posX,posY,posZ]
    
    return midPos

def triangulatePivot(posVerts,upvectorVert,locatorPivot=True,meshPivot=True):
    
    cmds.undoInfo(openChunk=True)
    
    posA=cmds.xform(posVerts[0],q=True,ws=True,translation=True)
    posB=cmds.xform(posVerts[1],q=True,ws=True,translation=True)
    posC=cmds.xform(upvectorVert,q=True,ws=True,translation=True)
    
    pivotPos=MidPosition(posA, posB)
    
    crs=mru.CrossProduct(posA, posB, posC)
    
    grp=cmds.group(empty=True)
    cmds.xform(grp,worldSpace=True,translation=posA)
    
    if locatorPivot:
        
        loc=cmds.spaceLocator()
        
        cmds.xform(loc,ws=True,translation=pivotPos)
        cmds.aimConstraint(grp,loc,worldUpType='vector',worldUpVector=crs)
    
    if meshPivot:
        
        posGrp=cmds.group(empty=True)
        
        cmds.xform(posGrp,ws=True,translation=pivotPos)
        cmds.aimConstraint(grp,posGrp,worldUpType='vector',worldUpVector=crs)
        
        pivotTranslate = cmds.xform (posGrp, q = True, ws = True, rotatePivot = True)
        
        shape=cmds.listRelatives(upvectorVert,parent=True)
        transform=cmds.listRelatives(shape,parent=True)
        parent=cmds.listRelatives(transform,parent=True)
        
        cmds.parent(transform, posGrp)
        cmds.makeIdentity(transform, a = True, t = True, r = True, s = True)
        cmds.xform (transform, ws = True, pivots = pivotTranslate)
        
        if parent!=None:
            cmds.parent(transform,parent)
        else:
            cmds.parent(transform,w=True)
        
        cmds.delete(posGrp)
    
    cmds.delete(grp)
    
    cmds.undoInfo(closeChunk=True)