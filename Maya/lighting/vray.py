import maya.mel as mel
import maya.cmds as cmds
import math

import Tapp.Maya.rigging.utils as mru

cmds.loadPlugin('vrayformaya.mll',quiet=True)

def addSubdivision():
    '''
    Adds VRay subdivision to selected objets and sets the max subdiv level to 4 which is plenty for nearly every single case
    '''
    nodeList = cmds.ls(selection = True, dag=True, lf=True, type = 'mesh') # find shape nodes of current selection
    for node in nodeList:
        mel.eval('vray addAttributesFromGroup %s vray_subdivision 1' % node)
        mel.eval('vray addAttributesFromGroup %s vray_subquality 1' % node)

def setSubdivision(level):
    
    nodeList = cmds.ls(selection = True, dag=True, lf=True, type = 'mesh') # find shape nodes of current selection
    for node in nodeList:
        cmds.setAttr(node+'.vrayMaxSubdivs',level)

def addDomeLight(fileName=None,cameraSpace=False):
    
    #create light
    light=cmds.shadingNode('VRayLightDomeShape',asLight=True)
    lightShape=cmds.listRelatives(light,shapes=True)[0]
    
    #setup light
    cmds.setAttr(lightShape+".domeSpherical",1)
    cmds.setAttr(lightShape+".useDomeTex",1)
    cmds.setAttr(lightShape+".invisible",1)
    
    if fileName:
        f=cmds.shadingNode('file',asTexture=True)
        cmds.setAttr(f+'.fileTextureName',fileName,type='string')
        cmds.connectAttr(f+'.outColor',lightShape+'.domeTex')
        
        env=cmds.shadingNode('VRayPlaceEnvTex',asUtility=True)
        cmds.setAttr(env+'.mappingType',2)
        cmds.connectAttr(env+'.outUV',f+'.uvCoord')
        cmds.connectAttr(light+'.worldMatrix[0]',env+'.transform')
    
    if cameraSpace:
        #getting cameras in scene
        cams=[]
        exclude=['front','side','top']
        for cam in cmds.ls(cameras=True):
            
            tn=cmds.listRelatives(cam,parent=True)[0]
            
            if tn not in exclude:
                cams.append(tn)
        
        cams.append('Cancel')
        
        #user input
        cam=cmds.confirmDialog( title='Camera Space',
                                   message='Select camera space for dome light.',
                                   button=cams)
        
        mru.Snap(cam, light)
        cmds.parent(light,cam)
        
        cmds.setAttr(env+'.useTransform',1)
        cmds.setAttr(cam+'.v',1)

def createTechPasses():
    '''
    Creates tech passes for rendering
    zdepth, xyz, normals, gi, spec, reflection, lighting, uv
    '''

    # first we make the sampler node as we will use this twice
    samplerNodeName = 'util_sampler_node'
    if not cmds.objExists(samplerNodeName) :
        samplerNode = cmds.shadingNode('samplerInfo', asUtility=True)
        samplerNode = cmds.rename(samplerNode, samplerNodeName)
    # now we make the xyz point render element
    layerToMake = 'XYZ_tex'
    if not cmds.objExists(layerToMake) :
        renderElement = mel.eval ('vrayAddRenderElement ExtraTexElement;')
        cmds.rename (renderElement,layerToMake)
        cmds.setAttr (layerToMake + '.vray_explicit_name_extratex', 'world_xyz', type = 'string')
        cmds.setAttr (layerToMake + '.vray_considerforaa_extratex', 0)
        cmds.connectAttr (samplerNode + '.pointWorld', 'XYZ_tex.vray_texture_extratex')
    # now we make the normals render element
    layerToMake = 'normals'
    if not cmds.objExists(layerToMake) :
        renderElement = mel.eval ('vrayAddRenderElement normalsChannel;')
        cmds.rename (renderElement,layerToMake)
        cmds.setAttr(layerToMake + '.vray_filtering_normals', 0)
    # uv render element
    layerToMake = 'uv'
    if not cmds.objExists(layerToMake) :
        renderElement = mel.eval ('vrayAddRenderElement ExtraTexElement;')
        cmds.rename (renderElement,layerToMake)
        cmds.setAttr (layerToMake + '.vray_explicit_name_extratex', 'uv', type = 'string')
        cmds.connectAttr (samplerNode + '.uvCoord.uCoord', layerToMake + '.vray_texture_extratex.vray_texture_extratexR')    
        cmds.connectAttr (samplerNode + '.uvCoord.vCoord', layerToMake + '.vray_texture_extratex.vray_texture_extratexG')
        cmds.setAttr(layerToMake + '.vray_filtering_extratex', 0)
    # add zdepth unclamped and unfiltered
    layerToMake = 'zdepth'
    if not cmds.objExists(layerToMake) :
        renderElement = mel.eval('vrayAddRenderElement zdepthChannel;')
        renderElement = cmds.rename (renderElement, layerToMake)
        cmds.setAttr(renderElement + '.vray_depthClamp', 0)
        cmds.setAttr(renderElement + '.vray_filtering_zdepth', 0)
    # add zdepth filtered
    layerToMake = 'zdepthAA'
    if not cmds.objExists(layerToMake) :
        renderElement = mel.eval('vrayAddRenderElement zdepthChannel;')
        renderElement = cmds.rename (renderElement, layerToMake)
        cmds.setAttr(renderElement + '.vray_depthClamp', 0)
        cmds.setAttr(renderElement + '.vray_filtering_zdepth', 1)    
    # add base render layers for recomp
    layerToMake = 'gi'
    if not cmds.objExists(layerToMake) :
        renderElement = mel.eval('vrayAddRenderElement giChannel;')
        renderElement = cmds.rename (renderElement, layerToMake)
        cmds.setAttr (renderElement + '.vray_name_gi', layerToMake, type = 'string')
    layerToMake = 'lighting'
    if not cmds.objExists(layerToMake) :
        renderElement = mel.eval('vrayAddRenderElement lightingChannel;')
        renderElement = cmds.rename (renderElement, layerToMake)
    layerToMake = 'reflection'
    if not cmds.objExists(layerToMake) :
        renderElement = mel.eval('vrayAddRenderElement reflectChannel;')
        renderElement = cmds.rename (renderElement, layerToMake)
    layerToMake = 'specular'
    if not cmds.objExists(layerToMake) :
        renderElement = mel.eval('vrayAddRenderElement specularChannel;')
        renderElement = cmds.rename (renderElement, layerToMake)
        
    # create AO
    layerToMake = 'ao'
    if not cmds.objExists(layerToMake) :
        renderElement = mel.eval ('vrayAddRenderElement ExtraTexElement;')
        renderElement = cmds.rename (renderElement,layerToMake)
        cmds.setAttr (renderElement + '.vray_explicit_name_extratex', layerToMake, type = 'string')
        newNode = cmds.shadingNode('VRayDirt', name = 'ao_tex', asTexture=True)
        cmds.connectAttr (newNode + '.outColor', renderElement + '.vray_texture_extratex')
        cmds.setAttr (newNode + '.invertNormal', 1)
        cmds.setAttr (newNode + '.ignoreForGi', 0)
        cmds.setAttr (newNode + '.blackColor', -0.5 ,-0.5 ,-0.5, type='double3')
        cmds.setAttr (newNode + '.falloff', 5)

def addObjectID():
    
    '''
    add object id to selected objects.  check for existing object ID and add new one if there are existing.
    '''
    
    
    nodeList = cmds.ls(selection = True, dag=True, lf=True, type = 'mesh') # find shape nodes of current selection
    
    allNodes = cmds.ls(type = 'mesh') # look for meshes only in the scene
    
    existingIDs = [0]
    
    for node in allNodes: # go through and check for existing object IDs here
        attrList = cmds.listAttr(node)
        if 'vrayObjectID' in attrList:
            existingIDs.append (cmds.getAttr ('%s.vrayObjectID' % node))
    
    newObjectID = 1
    
    existingIDs.sort() # this is just for cleanliness.  not required.
    
    for id in range(max(existingIDs)+2): # look through the list and let's find an unused number if that exists we need to go one beyond the current values so we can add it if needed
        if id not in existingIDs:
            newObjectID = id
            existingIDs.append(newObjectID)
            break
    
    for node in nodeList:
        attrList = cmds.listAttr(node)
        if 'vrayObjectID' not in attrList:
            print newObjectID
            mel.eval ('vray addAttributesFromGroup %s vray_objectID 1' % node)
            cmds.setAttr('%s.vrayObjectID' % node ,newObjectID)
            renderElements = cmds.ls (type = 'VRayRenderElement')
        
    addedID = False # clear the slate here
    
    attrsToSearch = ['vray_redid_multimatte','vray_greenid_multimatte','vray_blueid_multimatte'] # just looking for these attrs
    
    multiMatteElements = [] # nice and tidy here
    
    for element in renderElements: #go through and find multi matte elements and add them to our list
        if cmds.getAttr('%s.vrayClassType' % element) == 'MultiMatteElement':
            multiMatteElements.append(element)
    
    if len(multiMatteElements) < int(math.modf((newObjectID+2)/3)[1]) : # check amount of multi matte elements against how many we can fit in a render element
        newMMate = mel.eval('vrayAddRenderElement MultiMatteElement') # add the element
        cmds.setAttr('%s.vray_considerforaa_multimatte' % newMMate, 1) #make sure it has AA on it...
        multiMatteElements.append(newMMate)
    
    for element in multiMatteElements: # go through the multimatte list
        for multimatte in attrsToSearch: # we are looking only through the id attributes
            if cmds.getAttr('%s.%s' % (element, multimatte)) == newObjectID : # if we find the ID already just try to skip the rest of the testing
                addedID = True
            if cmds.getAttr('%s.%s' % (element, multimatte)) == 0 and addedID == False : # didn't find anything eh?  good.  we add the id to the multimatte.
                cmds.setAttr('%s.%s' % (element, multimatte), newObjectID)
                addedID = True