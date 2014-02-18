import maya.cmds as cmds
import maya.mel as mel

def MG_twist(startMatrix,endMatrix,locatorAmount,twistAxis='X'):
    ''' Creates a basic setup of MG_twist,
        with requested amount of locators.
        
        input description:
        
        startMatrix (node) = transform
        endMatrix (node) = transform
        locatorAmount (int) = amount of locators
        spreadTrans (bool) = distributes locators between start and end matrix
        spreadRot (bool) = distributes rotation locators between start and end matrix
        twistAxis (string) = indicates which axis to twist
        
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
    
    #create startMatrix
    if startMatrix==None:
        startMatrix=cmds.spaceLocator(n='start')[0]
    
    result['startMatrix']=startMatrix
    
    #create endMatrix
    if endMatrix==None:
        endMatrix=cmds.spaceLocator(n='end')[0]
    
    result['endMatrix']=endMatrix
    
    #create MG_twist
    twist=mel.eval('createNode MG_twist;')
    
    #setup MG_twist
    cmds.connectAttr(startMatrix+'.worldMatrix[0]',twist+'.matrix1')
    
    cmds.connectAttr(endMatrix+'.worldMatrix[0]',twist+'.matrix2')
    
    cmds.setAttr(twist+'.numberOfOutputs',locatorAmount)
    
    if twistAxis=='X':
        cmds.setAttr(twist+'.twistAxis',0)
    elif twistAxis=='Y':
        cmds.setAttr(twist+'.twistAxis',1)
    elif twistAxis=='Z':
        cmds.setAttr(twist+'.twistAxis',2)
    
    #locators---
    locs=[]
    if locatorAmount!=0:
        for count in xrange(0,locatorAmount):
            
            #create locator
            loc=cmds.spaceLocator(name='loc1')[0]
            
            locs.append(loc)
            
            #setup locator
            cmds.connectAttr(twist+'.outputTranslate[%s]' % count,loc+'.translate')
            cmds.connectAttr(twist+'.outputRotate[%s]' % count,loc+'.rotate')
    
    result['locators']=locs
    
    #return---
    #undo end
    cmds.undoInfo(closeChunk=True)
    
    #return
    return result