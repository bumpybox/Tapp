import maya.cmds as cmds
import maya.mel as mel


def MG_softIk(joints,startMatrix=None,endMatrix=None,ikHandle=None,root=None):
    
    #return variables
    result={}
    
    #undo start
    cmds.undoInfo(openChunk=True)
    
    #loading plugin
    cmds.loadPlugin('MG_rigToolsPro.mll',quiet=True)
    
    #create start matrix
    if startMatrix==None:
        startMatrix=cmds.spaceLocator()[0]
        
    result['startMatrix']=startMatrix
    
    #create end matrix
    if endMatrix==None:
        endMatrix=cmds.spaceLocator()[0]
    
    result['endMatrix']=endMatrix
    
    #create ik
    if ikHandle==None:
        ikHandle=cmds.ikHandle(sj=joints[0],ee=joints[-1],sol='ikRPsolver')[0]
    
    result['ikHandle']=ikHandle
    
    #create MG_softIk
    softIk=mel.eval('createNode MG_softIk;')
    
    result['softIk']=softIk
    
    #setup start matrix
    cmds.delete(cmds.parentConstraint(joints[0],startMatrix))
    
    cmds.connectAttr(startMatrix+'.worldMatrix[0]',softIk+'.startMatrix')
    
    #setup end matrix
    cmds.delete(cmds.parentConstraint(joints[-1],endMatrix))
    
    cmds.connectAttr(endMatrix+'.worldMatrix[0]',softIk+'.endMatrix')
    
    #setup ik
    cmds.connectAttr(softIk+'.outputTranslate',ikHandle+'.translate')
    
    #setup joints
    cmds.connectAttr(softIk+'.upScale',joints[0]+'.scaleX')
    cmds.connectAttr(softIk+'.downScale',joints[1]+'.scaleX')
    
    #setup softIk
    dist=__distance__(joints[0], joints[1])
    cmds.setAttr(softIk+'.upInitLength',dist)
    
    dist=__distance__(joints[1], joints[-1])
    cmds.setAttr(softIk+'.downInitLength',dist)
    
    cmds.setAttr(softIk+'.globalScale',1)
    cmds.setAttr(softIk+'.softDistance',0.001)
    cmds.setAttr(softIk+'.stretch',1)
    
    #root parent
    if root:
        cmds.parent(ikHandle,root)
        cmds.parent(startMatrix,root)
        cmds.parent(endMatrix,root)
    
    #return --------------------------------------
    #undo end
    cmds.undoInfo(closeChunk=True)
    
    #return
    return result

def __distance__(objA,objB ):
    ''' Returns distance between two nodes. '''
    
    from math import sqrt,pow
    
    At=cmds.xform(objA,ws=True,q=True,t=True)
    Ax=At[0]
    Ay=At[1]
    Az=At[2]
    
    Bt=cmds.xform(objB,ws=True,q=True,t=True)
    Bx=Bt[0]
    By=Bt[1]
    Bz=Bt[2]
 
    return sqrt(  pow(Ax-Bx,2) + pow(Ay-By,2) + pow(Az-Bz,2)  )