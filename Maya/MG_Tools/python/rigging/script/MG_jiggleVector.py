import maya.cmds as cmds
import maya.mel as mel

def MG_jiggleVector(targetNode=None,outputNode=None):
    ''' Creates a basic setup of MG_jiggleVector.
        
        input description:
        
        targetNode (node) = transform
        outputNode (node) = transform
        
        returns:
        
        (dict) Dicationary with all created nodes,
                categorized by function type
        
        usage:
        
        
    '''
    
    #return variables
    result={}
    
    #undo start
    cmds.undoInfo(openChunk=True)
    
    #loading plugin
    cmds.loadPlugin('MG_rigToolsPro.mll',quiet=True)
    
    #create targetNode
    if targetNode==None:
        targetNode=cmds.spaceLocator(n='target')[0]
    
    result['target']=targetNode
    
    #create outputNode
    if outputNode==None:
        outputNode=cmds.spaceLocator(n='output')[0]
    
    result['output']=outputNode
    
    #create MG_twist
    jiggle=mel.eval('createNode MG_jiggleVector;')
    
    #setup MG_twist
    cmds.connectAttr(targetNode+'.worldMatrix[0]',jiggle+'.targetMatrix')
    
    cmds.connectAttr(jiggle+'.output',outputNode+'.translate')
    
    cmds.connectAttr('time1.outTime',jiggle+'.time')
    
    cmds.setAttr(jiggle+'.damping',0.2)
    cmds.setAttr(jiggle+'.stiffness',0.2)
    
    cmds.setAttr(jiggle+'.targetVectorX',0)
    cmds.setAttr(jiggle+'.targetVectorY',1)
    cmds.setAttr(jiggle+'.targetVectorZ',0)
    
    cmds.setAttr(jiggle+'.useLocalOutput',0)

    #return---
    #undo end
    cmds.undoInfo(closeChunk=True)
    
    #return
    return result