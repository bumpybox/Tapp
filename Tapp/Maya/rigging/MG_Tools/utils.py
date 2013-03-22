import maya.cmds as cmds
import maya.mel as mel

def MG_pathSpine(curve,locatorAmount,skinCurve=False):
    ''' Sets up MG_pathSpine on input curve,
        with requested amount of locators.
        
        curve (node) = spline curve
        locatorAmount (int) = amount of locators
        skinCurve (bool) = creates a joint for each cv,
                            and skins the curve
        
        usage:
        
        pathSpineLocators('curve1',5,skinCurve=True)
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
    
    #skin curve-------------------------------
    
    if skinCurve:
        #getting cv count
        degree=cmds.getAttr(curve+'.degree')
        spans=cmds.getAttr(curve+'.spans')
        
        cvCount=degree+spans
        
        #create joints
        jnts=[]
        for count in xrange(0,cvCount):
            
            #getting cv position
            pos=cmds.xform('%s.cv[%s]' % (curve,count),q=True,translation=True)
            
            #creating joint
            cmds.select(cl=True)
            jnt=cmds.joint(position=pos)
            
            jnts.append(jnt)
        
        #skinning curve
        cmds.skinCluster(jnts,curve,tsb=True)