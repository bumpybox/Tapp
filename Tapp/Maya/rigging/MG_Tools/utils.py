import maya.cmds as cmds
import maya.mel as mel

def MG_pathSpine(curve,locatorAmount,skinCurve=False,defaultValues=False):
    ''' Sets up MG_pathSpine on input curve,
        with requested amount of locators.
        
        input description:
        
        curve (node) = spline curve
        locatorAmount (int) = amount of locators
        skinCurve (bool) = creates a joint for each cv,
                            and skins the curve
        defaultValues (bool) = sets up some default values,
                                on stretch, squash and twist
        
        returns:
        
        (dict) Dicationary with all created nodes,
                categorized by function type
        
        usage:
        
        MG_pathSpine('curve1',5,skinCurve=True,defaultValues=True)
    '''
    
    #return variables
    result={}
    
    #undo start
    cmds.undoInfo(openChunk=True)
    
    #loading plugin
    cmds.loadPlugin('MG_toolsPro.mll')
    
    #create MG_pathSpine
    ps=mel.eval('createNode MG_pathSpine;')
    
    #setup MG_pathSpine
    cmds.connectAttr(curve+'.worldSpace[0]',ps+'.inputCurve')
    
    cmds.setAttr(ps+'.numberOfOutput',locatorAmount)
    cmds.setAttr(ps+'.numberOfSamples',locatorAmount*2)
    
    cmds.setAttr(ps+'.startLength',cmds.arclen(curve))
    
    #return value
    result['MG_pathSpine']=ps
    
    #default values
    if defaultValues:
        
        #stretch values
        cmds.setAttr(ps+'.stretchShape[0].stretchShape_Interp',2)    
        cmds.setAttr(ps+'.stretchShape[1].stretchShape_Interp',2)
        cmds.setAttr(ps+'.stretchShape[1].stretchShape_Position',1)
        cmds.setAttr(ps+'.stretchShape[1].stretchShape_FloatValue',0)
        cmds.setAttr(ps+'.stretchShape[2].stretchShape_FloatValue',1)
        cmds.setAttr(ps+'.stretchShape[2].stretchShape_Position',0.5)
        cmds.setAttr(ps+'.stretchShape[2].stretchShape_Interp',2)
        
        #squash values
        cmds.setAttr(ps+'.squashShape[0].squashShape_Interp',2)
        cmds.setAttr(ps+'.squashShape[1].squashShape_Interp',2)
        cmds.setAttr(ps+'.squashShape[1].squashShape_Position',1)
        cmds.setAttr(ps+'.squashShape[1].squashShape_FloatValue',0)
        cmds.setAttr(ps+'.squashShape[2].squashShape_FloatValue',1)
        cmds.setAttr(ps+'.squashShape[2].squashShape_Position',0.5)
        cmds.setAttr(ps+'.squashShape[2].squashShape_Interp',2)
        
        #twist values
        cmds.setAttr(ps+'.twistShape[1].twistShape_Interp',1)
        cmds.setAttr(ps+'.twistShape[1].twistShape_Position',1)
        cmds.setAttr(ps+'.twistShape[1].twistShape_FloatValue',1)
    
    #locators-------------------
    #create start twist locator
    loc=mel.eval('createNode implicitBox;')
    loc=cmds.listRelatives(parent=True)[0]
    
    result['twist_start']=loc
    
    #setup start twist locator
    pos=cmds.xform('%s.cv[%s]' % (curve,0),q=True,translation=True)
    cmds.xform(loc,translation=pos)
    
    cmds.connectAttr(loc+'.ry',ps+'.twist1')
    
    #middle locators
    locs=[]
    for count in xrange(0,locatorAmount):
        
        #create locator
        loc=cmds.spaceLocator()[0]
        
        locs.append(loc)
        
        #setup locator
        cmds.connectAttr(ps+'.outputTranslate[%s]' % count,loc+'.translate')
        cmds.connectAttr(ps+'.outputRotate[%s]' % count,loc+'.rotate')
        cmds.connectAttr(ps+'.outputScale[%s]' % count,loc+'.scale')
        
    #return value
    result['locators']=locs
    
    #create end twist locator
    loc=mel.eval('createNode implicitBox;')
    loc=cmds.listRelatives(parent=True)[0]
    
    result['twist_end']=loc
    
    #setup start twist locator
    degree=cmds.getAttr(curve+'.degree')
    spans=cmds.getAttr(curve+'.spans')
    
    cvCount=degree+spans
    
    pos=cmds.xform('%s.cv[%s]' % (curve,cvCount),q=True,translation=True)
    cmds.xform(loc,translation=pos)
    
    cmds.connectAttr(loc+'.ry',ps+'.twist2')
    
    #skin curve-------------------------------
    jnts=[]
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
        
    #return value
    result['joints']=jnts
    
    #undo end
    cmds.undoInfo(closeChunk=True)
    
    #return
    return result

MG_pathSpine('curve1',5,skinCurve=True,defaultValues=True)