import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru

def SkeletonParent():
    ''' Parents selection to closest joint in rig. ''' 
    
    cmds.undoInfo(openChunk=True)
    
    for jnt in cmds.ls(selection=True):
        
        nodes={}
        for node in cmds.ls(type='network'):
            
            data=mum.GetData(node)
            if data['type']=='joint':
                
                tn=mum.GetTransform(node)
                nodes[tn]=mru.Distance(tn, jnt)
        
        closestJnt=min(nodes, key=nodes.get)
        
        cmds.parentConstraint(closestJnt,jnt,mo=True)
        cmds.scaleConstraint(closestJnt,jnt,mo=True)
        
        cmds.setAttr(jnt+'.segmentScaleCompensate',0)
    
    cmds.undoInfo(closeChunk=True)