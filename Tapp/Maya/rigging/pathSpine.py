import maya.cmds as cmds
import maya.mel as mel

def pathSpineLocators(curve,locatorAmount):
    ''' Sets up MG_pathSpine on input curve,
        with requested amount of locators
        
        curve = spline curve (node)
        locatorAmount = amount of locators (int)
        
        usage:
        
        pathSpineLocators('curve1',5)
    '''
    
    #loading plugin
    cmds.loadPlugin('MG_toolsPro.mll')
    
    #create MG_pathSpine
    ps=mel.eval('createNode MG_pathSpine;')
    
    #setup MG_pathSpine
    cmds.connectAttr(curve+'.worldSpace[0]',ps+'.inputCurve')
    
    cmds.setAttr(ps+'.numberOfOutput',locatorAmount)
    
    cmds.setAttr(ps+'.startLength',cmds.arclen(curve))
    
    #locators-------------------
    for count in xrange(0,locatorAmount):
        
        #create locator
        loc=cmds.spaceLocator()[0]
        
        #setup locator
        cmds.connectAttr(ps+'.outputTranslate[%s]' % count,loc+'.translate')
        cmds.connectAttr(ps+'.outputRotate[%s]' % count,loc+'.rotate')
        cmds.connectAttr(ps+'.outputScale[%s]' % count,loc+'.scale')