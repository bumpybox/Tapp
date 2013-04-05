import maya.cmds as cmds

import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru

def SkeletonParent():
    ''' Parents selection to closest joint in rig. ''' 
    
    cmds.undoInfo(openChunk=True)
    
    for obj in cmds.ls(selection=True):
        
        if cmds.nodeType(obj)=='joint':
        
            nodes={}
            for node in cmds.ls(type='network'):
                
                data=mum.GetData(node)
                if data['type']=='joint':
                    
                    tn=mum.GetTransform(node)
                    nodes[tn]=mru.Distance(tn, obj)
            
            closestJnt=min(nodes, key=nodes.get)
            
            cmds.parentConstraint(closestJnt,obj,mo=True)
            #cmds.scaleConstraint(closestJnt,obj)
            
            #scaling linking
            cmds.connectAttr(closestJnt+'.sx',obj+'.sx')
            cmds.connectAttr(closestJnt+'.sy',obj+'.sy')
            cmds.connectAttr(closestJnt+'.sz',obj+'.sz')
            
            #cmds.setAttr(obj+'.inheritsTransform',0)
            
            #cmds.setAttr(obj+'.segmentScaleCompensate',0)
    
    cmds.undoInfo(closeChunk=True)

SkeletonParent()