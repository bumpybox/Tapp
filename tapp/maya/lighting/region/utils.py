'''

- UI

Credits:
Author:  Ryan Trowbridge
Contact: admin@rtrowbridge.com
'''

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

class region():
    
    def __init__(self,frame,minX,maxX,minY,maxY):
        
        self.frame=frame
        self.minX=minX
        self.maxX=maxX
        self.minY=minY
        self.maxY=maxY

def getRegionDraw():
    
    minX=cmds.getAttr('defaultRenderGlobals.left')
    maxX=cmds.getAttr('defaultRenderGlobals.rght')
    minY=cmds.getAttr('defaultRenderGlobals.bot')
    maxY=cmds.getAttr('defaultRenderGlobals.top')
    
    frame=cmds.currentTime(q=True)
    
    return region(frame,minX,maxX,minY,maxY)

def getRegionNode():
    
    result=[]
    
    for layer in cmds.ls(type='renderLayer'):
        
        if not cmds.referenceQuery(layer,isNodeReferenced=True):
        
            #search for existing region nodes
            node=cmds.listConnections('%s.message' % layer,type='network')
            
            #create node if none existing
            if not node:
                node=cmds.shadingNode('network',n='regionNode_'+layer,asUtility=True)
            else:
                node=node[0]
            
            #adding attributes
            attrs=['minX','maxX','minY','maxY','renderheight','renderwidth']
            for attr in attrs:
                if not cmds.objExists(node+'.'+attr):
                    cmds.addAttr(node,ln=attr,defaultValue=0,attributeType='long',k=True)
            
            cmds.setAttr(node+'.renderheight',k=False)
            cmds.setAttr(node+'.renderwidth',k=False)
            
            #connecting to default render resolution
            if not cmds.listConnections('%s.width' % 'defaultResolution',type='network'):
                cmds.connectAttr('defaultResolution.width',node+'.renderwidth',force=True)
                cmds.connectAttr('defaultResolution.height',node+'.renderheight',force=True)
            
            #connecting to renderlayer
            if not cmds.objExists(node+'.'+'renderlayer'):
                cmds.addAttr(node,ln='renderlayer',attributeType='message')
                
                cmds.connectAttr(layer+'.message',node+'.renderlayer')
            
            #return node
            result.append(node)
    
    return result

def getMeshRegion(pixelBuffer=2):
    '''
    Main part of this code is credited to: 
    
    Author:  Ryan Trowbridge
    Contact: admin@rtrowbridge.com
    '''

    # get current render width and height settings
    renderWidth = cmds.getAttr('defaultResolution.width')
    renderHeight = cmds.getAttr('defaultResolution.height')

    # get the active viewport
    activeView = OpenMayaUI.M3dView.active3dView()
    
    #setting camera overscan to 1
    path=OpenMaya.MDagPath()
    activeView.getCamera(path)
    
    cam=path.fullPathName()
    
    overscan=cmds.getAttr(cam+'.overscan')
    cmds.setAttr(cam+'.overscan',1)
    
    cmds.refresh()
    
    # define python api pointers to get data from api class
    xPtrInit = OpenMaya.MScriptUtil()
    yPtrInit = OpenMaya.MScriptUtil()
    widthPtrInit = OpenMaya.MScriptUtil()
    heightPtrInit = OpenMaya.MScriptUtil()
    
    xPtr = xPtrInit.asUintPtr()
    yPtr = yPtrInit.asUintPtr()
    widthPtr = widthPtrInit.asUintPtr()
    heightPtr = heightPtrInit.asUintPtr()
    
    # retreive viewport width and height
    activeView.viewport(xPtr, yPtr, widthPtr, heightPtr)
    viewWidth = widthPtrInit.getUint( widthPtr )
    viewHeight = heightPtrInit.getUint( heightPtr )
    
    # determin aspect ratio of render size
    # then determin what the viewport renderable height is
    aspectRatio = float(renderHeight) / float(renderWidth)
    viewportRenderableMax = 0
    heightDiff = 0  # actual viewport renderable pixels
    heightClip = 0    # area of user viewport not renderable
    
    if(renderWidth > renderHeight):
        viewportRenderableMax = viewWidth * aspectRatio
        heightDiff = viewHeight - viewportRenderableMax
        heightClip = heightDiff / 2
    else:
        viewportRenderableMax = viewHeight * aspectRatio
        heightDiff = viewportRenderableMax - viewHeight
        heightClip = heightDiff / 2
    
    # get the active selection
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList( selection )
    iterSel = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMesh)

    # bounding box vars
    minX = 0
    maxX = 0
    minY = 0
    maxY = 0

    iterGeoNum = 0
    
    # loop through the selected nodes
    while not iterSel.isDone():

        dagPath = OpenMaya.MDagPath()
        iterSel.getDagPath( dagPath )
        
        iterGeo = OpenMaya.MItGeometry( dagPath )

        # iterate through vertex positions
        # check each vertex position and get its x, y cordinate in the viewport
        # generate the minimum x and y position and the max x and y position
        
        while not iterGeo.isDone():

            vertexMPoint = iterGeo.position(OpenMaya.MSpace.kWorld)
            xPosShortPtrInit = OpenMaya.MScriptUtil()
            yPosShortPtrInit = OpenMaya.MScriptUtil()
            xPosShortPtr = xPosShortPtrInit.asShortPtr()
            yPosShortPtr = yPosShortPtrInit.asShortPtr()

            activeView.worldToView(vertexMPoint, xPosShortPtr, yPosShortPtr)

            xPos = xPosShortPtrInit.getShort(xPosShortPtr)
            yPos = yPosShortPtrInit.getShort(yPosShortPtr)

            if iterGeoNum == 0:
                minX = xPos
                minY = yPos

            if xPos < minX: minX = xPos
            if xPos > maxX: maxX = xPos
            if yPos < minY: minY = yPos
            if yPos > maxY: maxY = yPos
            
            iterGeoNum = iterGeoNum + 1
            iterGeo.next()
        
        # move on to next selected node
        iterSel.next()
    
    # the renderWindowCheckAndRenderRegion arguments are ymax, xmin, ymin, xmax        
    # convert the min max values to scalars between 0 and 1

    if(renderWidth > renderHeight):
        minX = int(renderWidth*(float(minX)/float(viewWidth)))
        maxX = int(renderWidth*(float(maxX)/float(viewWidth)))
    else:
        minX = int(renderWidth*(float(minX)/float(viewportRenderableMax)/aspectRatio))
        maxX = int(renderWidth*(float(maxX)/float(viewportRenderableMax)/aspectRatio))
    
    minYScalar = 0
    maxYScalar = 0
    
    if(renderWidth > renderHeight):
        minYScalar = ((float(minY)-heightClip)/float(viewWidth))
        maxYScalar = ((float(maxY)-heightClip)/float(viewWidth))
    else:
        minYScalar = ((float(minY)+heightDiff+heightClip)/aspectRatio)/float(viewportRenderableMax)
        maxYScalar = ((float(maxY)+heightDiff+heightClip)/aspectRatio)/float(viewportRenderableMax)
    
    minY=int(minYScalar*renderHeight/aspectRatio)
    maxY=int(maxYScalar*renderHeight/aspectRatio)
    
    #making sure no values are less than zero and no heigher than render resolution
    if minX<0:
        minX=0
    if minX>renderWidth:
        minX=renderWidth
    
    if maxX<0:
        maxX=0
    if maxX>renderWidth:
        maxX=renderWidth
    
    if minY<0:
        minY=0
    if minY>renderHeight:
        minY=renderHeight
    
    if maxY<0:
        maxY=0
    if maxY>renderHeight:
        maxY=renderHeight
    
    #adding pixel buffer
    if 0 < minX < renderWidth:
        if (minX-pixelBuffer)>=0:
            minX-=pixelBuffer
    
    if 0 < maxX < renderWidth:
        if (maxX+pixelBuffer)<=renderWidth:
            maxX+=pixelBuffer
    
    if 0 < minY < renderHeight:
        if (minY-pixelBuffer)>=0:
            minY-=pixelBuffer
    
    if 0 < maxY < renderHeight:
        if (maxY+pixelBuffer)<=renderHeight:
            maxY+=pixelBuffer
    
    #regions cant equal max resolution
    if minX==renderWidth:
        minX=renderWidth-1
    if maxX==renderWidth:
        maxX=renderWidth-1
    if minY==renderHeight:
        minY=renderHeight-1
    if maxY==renderHeight:
        maxY=renderHeight-1
    
    #resetting overscan
    cmds.setAttr(cam+'.overscan',overscan)
    
    #if mesh is outside view
    if minX==0 and maxX==0:
        return None
    if minX==renderWidth and maxX==renderWidth:
        return None
    if minY==0 and maxY==0:
        return None
    if minY==renderHeight and maxY==renderHeight:
        return None
    
    #return
    frame=int(cmds.currentTime(q=True))
    
    return region(frame,minX,maxX,minY,maxY)

def getMeshAnimation():
    
    startFrame=int(cmds.playbackOptions(min=True,q=True))
    endFrame=int(cmds.playbackOptions(max=True,q=True))
    
    result=[]
    for f in range(startFrame,endFrame+1):
        
        cmds.currentTime(f)
        
        result.append(getMeshRegion())
    
    return result

def setRegionNode(node,region):
    
    cmds.setKeyframe( node, attribute='minX',v=region.minX, t=region.frame )
    cmds.setKeyframe( node, attribute='maxX',v=region.maxX, t=region.frame )
    cmds.setKeyframe( node, attribute='minY',v=region.minY, t=region.frame )
    cmds.setKeyframe( node, attribute='maxY',v=region.maxY, t=region.frame )

def clampMax(inputAttr,maxAttr,outputAttr):
    
    clp=cmds.shadingNode('clamp',asUtility=True)
    pms=cmds.shadingNode('plusMinusAverage',asUtility=True)
    
    cmds.addAttr(clp,ln='maxDiff',defaultValue=-1)
    cmds.connectAttr(inputAttr,clp+'.inputR')
    cmds.connectAttr(clp+'.outputR',outputAttr)
    
    cmds.connectAttr(maxAttr,pms+'.input1D[0]')
    cmds.connectAttr(clp+'.maxDiff',pms+'.input1D[1]')
    cmds.connectAttr(pms+'.output1D',clp+'.maxR')
    
    return [clp,pms]

def connectPreview():
    
    nodes=getRegionNode()
    
    if len(nodes)>1:
        for node in nodes:
            renderlayer=cmds.listConnections(node+'.renderlayer')[0]
            if renderlayer!='defaultRenderLayer':
                
                cmds.editRenderLayerAdjustment( 'defaultRenderGlobals.left',
                                                'defaultRenderGlobals.rght',
                                                'defaultRenderGlobals.bot',
                                                'defaultRenderGlobals.top',
                                                layer=renderlayer )
    
    for node in nodes:
        
        #activating renderlayer
        renderlayer=cmds.listConnections(node+'.renderlayer')[0]
        
        cmds.editRenderLayerGlobals( currentRenderLayer=renderlayer)
        cmds.refresh()
        
        #create container
        container=cmds.container(n=node+'_previewConnection')
        
        cmds.addAttr(container,ln='minX',defaultValue=1)
        cmds.addAttr(container,ln='minY',defaultValue=1)
        
        #connect to preview
        cmds.connectAttr(node+'.minX',container+'.minX')
        cmds.connectAttr(container+'.minX','defaultRenderGlobals.left')
        
        cmds.connectAttr(node+'.minY',container+'.minY')
        cmds.connectAttr(container+'.minY','defaultRenderGlobals.bot')
        
        [clp,pms]=clampMax(node+'.maxX',node+'.renderwidth','defaultRenderGlobals.rght')
        cmds.container(container,e=True,addNode=[clp,pms])
        [clp,pms]=clampMax(node+'.maxY',node+'.renderheight','defaultRenderGlobals.top')
        cmds.container(container,e=True,addNode=[clp,pms])

def disconnectPreview():
    
    for node in getRegionNode():
        
        renderlayer=cmds.listConnections(node+'.renderlayer')[0]
        
        cmds.editRenderLayerGlobals( currentRenderLayer=renderlayer)
        cmds.refresh()
    
        for n in cmds.listConnections('defaultRenderGlobals.left',type='container'):
        
            cmds.delete(n)

def connectArnold():
    
    nodes=getRegionNode()
    if len(nodes)>1:
        for node in nodes:
            renderlayer=cmds.listConnections(node+'.renderlayer')[0]
            if renderlayer!='defaultRenderLayer':
                
                cmds.editRenderLayerAdjustment( 'defaultArnoldRenderOptions.regionMinX',
                                                'defaultArnoldRenderOptions.regionMaxX',
                                                'defaultArnoldRenderOptions.regionMinY',
                                                'defaultArnoldRenderOptions.regionMaxY',
                                                layer=renderlayer )
    
    for node in nodes:
    
        #create container
        container=cmds.container(n=node+'_arnoldConnection')
        
        cmds.addAttr(container,ln='minX',defaultValue=1)
        
        #create utility nodes
        minpms=cmds.shadingNode('plusMinusAverage',asUtility=True)
        maxpms=cmds.shadingNode('plusMinusAverage',asUtility=True)
        
        cmds.container(container,e=True,addNode=[minpms,maxpms])
        
        #setup nodes
        cmds.setAttr(minpms+'.operation',2)
        cmds.connectAttr(node+'.renderheight',minpms+'.input1D[0]')
        cmds.connectAttr(node+'.maxY',minpms+'.input1D[1]')
        
        cmds.setAttr(maxpms+'.operation',2)
        cmds.connectAttr(node+'.renderheight',maxpms+'.input1D[0]')
        cmds.connectAttr(node+'.minY',maxpms+'.input1D[1]')
        
        cmds.connectAttr(node+'.minX',container+'.minX')
        
        #connect to arnold
        renderlayer=cmds.listConnections(node+'.renderlayer')[0]
        
        cmds.editRenderLayerGlobals( currentRenderLayer=renderlayer)
        cmds.refresh()
        
        cmds.connectAttr(container+'.minX','defaultArnoldRenderOptions.regionMinX')
        cmds.connectAttr(minpms+'.output1D','defaultArnoldRenderOptions.regionMinY')
        
        [clp,pms]=clampMax(node+'.maxX',node+'.renderwidth','defaultArnoldRenderOptions.regionMaxX')
        cmds.container(container,e=True,addNode=[clp,pms])
        [clp,pms]=clampMax(maxpms+'.output1D',node+'.renderheight','defaultArnoldRenderOptions.regionMaxY')
        cmds.container(container,e=True,addNode=[clp,pms])

def disconnectArnold():
    
    for node in getRegionNode():
        
        renderlayer=cmds.listConnections(node+'.renderlayer')[0]
        
        cmds.editRenderLayerGlobals( currentRenderLayer=renderlayer)
        cmds.refresh()
    
        for n in cmds.listConnections('defaultArnoldRenderOptions.regionMinX',type='container'):
        
            cmds.delete(n)

#connectPreview()
#connectArnold()
#disconnectPreview()
#disconnectArnold()

'''
regions=getMeshAnimation()

for node in getRegionNode():
    
    for r in regions:
        if r:
            
            setRegionNode(node, r)
            '''