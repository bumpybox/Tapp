import maya.cmds as cmds
import maya.mel as mel

def MG_pathSpine(curve,locatorAmount,skinCurve=False,defaultValues=True,rootNode='default'):
    ''' Creates a basic setup of MG_pathSpine on input curve,
        with requested amount of locators.
        
        input description:
        
        curve (node) = spline curve
        locatorAmount (int) = amount of locators
        skinCurve (bool) = creates a joint for each cv,
                            and skins the curve
        defaultValues (bool) = sets up some default values,
                                on stretch, squash and twist
        rootNode (node) = parent transform for setup,
                            defaults to create a group node
        
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
    cmds.loadPlugin('MG_rigToolsPro.mll',quiet=True)
    
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
    #curve locators
    locs=[]
    for count in xrange(0,locatorAmount):
        
        #create locator
        loc=cmds.spaceLocator(name='curve_loc1')[0]
        
        locs.append(loc)
        
        #setup locator
        cmds.connectAttr(ps+'.outputTranslate[%s]' % count,loc+'.translate')
        cmds.connectAttr(ps+'.outputRotate[%s]' % count,loc+'.rotate')
        cmds.connectAttr(ps+'.outputScale[%s]' % count,loc+'.scale')
    
    #twist nodes---
    #create start twist locator
    twiststart=mel.eval('createNode implicitBox;')
    twiststart=cmds.listRelatives(twiststart,parent=True)[0]
    twiststart=cmds.rename(twiststart,'twistStart')
    
    result['twist_start']=twiststart
    
    #setup start twist locator
    pos=cmds.xform('%s.cv[%s]' % (curve,0),q=True,translation=True)
    cmds.xform(twiststart,translation=pos)
    
    cmds.setAttr(twiststart+'.rotateOrder',1)
    
    cmds.delete(cmds.aimConstraint(locs[-1],twiststart,aimVector=[0,1,0],upVector=[0,0,1],worldUpType='scene'))
    
    cmds.connectAttr(twiststart+'.ry',ps+'.twist1')
    
    #create end twist locator
    twistend=mel.eval('createNode implicitBox;')
    twistend=cmds.listRelatives(twistend,parent=True)[0]
    twistend=cmds.rename(twistend,'twistEnd')
    
    result['twist_end']=twistend
    
    #setup end twist locator
    degree=cmds.getAttr(curve+'.degree')
    spans=cmds.getAttr(curve+'.spans')
    
    cvCount=degree+spans
    
    pos=cmds.xform('%s.cv[%s]' % (curve,cvCount),q=True,translation=True)
    cmds.xform(twistend,translation=pos)
    
    cmds.setAttr(twistend+'.rotateOrder',1)
    
    cmds.delete(cmds.orientConstraint(twiststart,twistend))
    
    cmds.connectAttr(twistend+'.ry',ps+'.twist2')
    
    #create up vector locators
    locA=cmds.spaceLocator(name='up_loc1')[0]
    locB=cmds.spaceLocator(name='up_loc2')[0]
    
    result['up_vector']=[locA,locB]
    
    #setup up vector locators
    cmds.delete(cmds.parentConstraint(twiststart,locA))
    cmds.delete(cmds.parentConstraint(twiststart,locB))
    
    cmds.move(0,0,1,locB,r=True,os=True)
    
    vector=mel.eval('createNode MG_vector;')
    
    cmds.connectAttr(locA+'.worldMatrix[0]',vector+'.inputMatrix1')
    cmds.connectAttr(locB+'.worldMatrix[0]',vector+'.inputMatrix2')
    
    cmds.connectAttr(vector+'.outputVector',ps+'.firstUpVec')
    
    result['vector']=vector
    
    #return value
    result['locators']=locs
    
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
            jnt=cmds.joint(position=pos,name='curve_jnt1')
            
            #aligning joints with twiststart
            cmds.delete(cmds.orientConstraint(twiststart,jnt))
            
            jnts.append(jnt)
        
        #skinning curve
        cmds.skinCluster(jnts,curve,tsb=True)
        
    #return value
    result['joints']=jnts
    
    #root node -------------------------------------
    #create root
    root=''
    if rootNode=='default':
        
        root=cmds.group(empty=True,name='root')
    else:
        
        root=rootNode
    
    result['root']=root
    
    #setup root
    cmds.parent(twiststart,root)
    cmds.parent(twistend,root)
    cmds.parent(locA,root)
    cmds.parent(locB,root)
    
    if skinCurve:
        cmds.parent(jnts,root)
    
    #return --------------------------------------
    #undo end
    cmds.undoInfo(closeChunk=True)
    
    #return
    return result