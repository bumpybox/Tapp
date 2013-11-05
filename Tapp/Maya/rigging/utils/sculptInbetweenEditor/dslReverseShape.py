'''
================================================================================
dslReverseShape.py - Python Script
================================================================================


by Daniel S. Lima
www.danielslima.com

This tool is a collection of influences and personal desire to have this 
functionality inside Maya since Autodesk never provided it so far. Pose 
Space Deformation allows the user to SCULPT on POSE, this method has implemented 
in many other softwares packaged before and also presented on papers by 
J.P. Lewis, Matt Cordner and Nickson Fong in 2000 Article. I give all the 
credits for these authors for these particular influence.


ACM Digital Library
http://dl.acm.org/citation.cfm?id=344862
 
daniel3d@gmail.com

*** MODIFY THIS AT YOUR WON RISK ***

DESCRIPTION: 
    CALCULATES THE POSE SPACE DEFORMATION

NOTES:
   
   NEXT VERSION:
        - Nurbs Support
    
    LIMITATIONS:
        - Polygons Only
          
REQUIRES:
    Maya BlendShape Node
    Maya SkinCluster Node or Third Party linear SkinCluster

USAGE:
    Called by dslSculptInbetweenManager

DATE: JAN/2011
RELEASE DATE: 01/13/13
LAST UPDATE: 01/10/2011
VERSION: 1.0
MAYA: 2010 ABOVE

'''

import maya.cmds as cmds
import maya.OpenMaya as om
import itertools
import time

def dslCorrectiveShape(skinGeo=None,
                       sculptGeo=None,
                       blendShapeNode=None,
                       correctiveGroup=None,
                       correctiveName=None,
                       correctiveItem=None,
                       inBetweenMode=False,
                       flatten=None,
                       keepSculpt=True):
    
    t = time.time()
    if correctiveItem == None:
        correctiveItem = int(6000)
    crPercentage = (correctiveItem - 5000) / 10
    print "crPercentage: " + str(crPercentage) + '%'
    numVtx = cmds.getAttr (skinGeo + '.vrts', s=True )
    defaultPointArray = ([numVtx] + [(0,0,0,1)] * numVtx)
    #print defaultPointArray
    ###################################
    xSculp = cmds.xform(sculptGeo + '.pnts[*]', q=True, os=True, t=True)
    sculptPts = zip(xSculp[0::3], xSculp[1::3], xSculp[2::3])
    #####################################
    iTg = '%s.inputTarget[0]' %blendShapeNode
    iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
    iTi = '.inputTargetItem[%s]' %correctiveItem
    iPt = '.inputPointsTarget'
    iCt = '.inputComponentsTarget'
    cr6000 = iTg + iTgGr + '.inputTargetItem[6000].inputPointsTarget'
    cri6000 = iTg + iTgGr + '.inputTargetItem[6000].inputComponentsTarget'
    gatherInfoFrom = iTg + iTgGr + iTi + iPt
    cmds.setAttr(gatherInfoFrom, type='pointArray', *defaultPointArray)
    xSkin = cmds.xform(skinGeo + '.pnts[*]', q=True, os=True, t=True)
    skinPts = zip(xSkin[0::3], xSkin[1::3], xSkin[2::3])
    offsetPointArray = []
    offsetPointArray.append([numVtx] + [(1,0,0,1)] * numVtx)
    offsetPointArray.append([numVtx] + [(0,1,0,1)] * numVtx)
    offsetPointArray.append([numVtx] + [(0,0,1,1)] * numVtx)
    axis = 'XYZ'
    unityDeltaXYZ = []
    unitDeltaX = []
    unitDeltaY = []
    unitDeltaZ = []
    for pArray in offsetPointArray:
        cmds.setAttr(gatherInfoFrom, type='pointArray', *pArray)
        tmpXform = cmds.xform(skinGeo + '.pnts[*]', q=True, os=True, t=True)
        unityDeltaXYZ.append(zip(tmpXform[0::3], tmpXform[1::3], tmpXform[2::3]))
        eval('unitDelta' + axis[offsetPointArray.index(pArray)]).append(unityDeltaXYZ[offsetPointArray.index(pArray)])
    if not keepSculpt:
        cmds.delete(sculptGeo)
    resultPointArray = []
    resultComponentList=[]
    calculated = []
    for v in range(numVtx):
        vectorSkin = om.MVector(*skinPts[v])
        vectorScpt = om.MVector(*sculptPts[v])
        disOnPose = vectorScpt - vectorSkin
        dispResult = (disOnPose.x, disOnPose.y, disOnPose.z)
        if dispResult != (0.0, 0.0, 0.0):
            resultComponentList.append('vtx[%s]' %v)
            calculated.append(1)
            dispOffset = vectorScpt - vectorSkin
            vectorunitDeltaX = om.MVector(*unitDeltaX[0][v])
            vectorunitDeltaY = om.MVector(*unitDeltaY[0][v])
            vectorunitDeltaZ = om.MVector(*unitDeltaZ[0][v])
            dispX = vectorunitDeltaX - vectorSkin
            dispY = vectorunitDeltaY - vectorSkin
            dispZ = vectorunitDeltaZ - vectorSkin
            listMatrix = (dispX.x, dispX.y, dispX.z, 0,
                          dispY.x, dispY.y, dispY.z, 0,
                          dispZ.x, dispZ.y, dispZ.z, 0,
                          0,0,0,1)
            matrix = om.MMatrix()
            om.MScriptUtil.createMatrixFromList(listMatrix, matrix)
            matrixInverted = om.MMatrix.inverse(matrix)
            vectorResult = (dispOffset * matrixInverted)
            if inBetweenMode != True:
                vectorRlist = (float((vectorResult.x / crPercentage ) * 100),
                               float((vectorResult.y / crPercentage ) * 100),
                               float((vectorResult.z / crPercentage ) * 100))
            else:
                vectorRlist = (float(vectorResult.x), float(vectorResult.y), float(vectorResult.z), int(1))
            resultPointArray.append(vectorRlist)
            
    #print 'resultPointtList ----> ',resultPointArray
    #print 'resultComponentList ----> ',resultComponentList
    #===========================================================================
    # ADDING FIRST VALUE TO THE RESULTS TO BE USED WITH SETATTR -TYPE
    #===========================================================================
    resultComponentList.insert(0, len(resultPointArray))
    resultPointArray.insert(0, len(resultPointArray))
    
    #allData = [resultPointArray, resultComponentList]

    
    if inBetweenMode != True:
        print '--------------IF'
        cmds.setAttr(cr6000, type='pointArray', *resultPointArray)
        cmds.setAttr(cri6000, type='componentList', *resultComponentList)
        if correctiveItem != 6000:
            cmds.removeMultiInstance(iTg + iTgGr + iTi, b=True)
            
    else:

        cmds.setAttr(gatherInfoFrom, type='pointArray', *resultPointArray)
        cmds.setAttr(iTg + iTgGr + iTi + iCt, type='componentList', *resultComponentList)

        if cmds.listAttr(cr6000) == None:
            print 'cmds.listAttr(cr6000) == None:'
            cmds.setAttr(cr6000, type='pointArray', *resultPointArray)
            cmds.setAttr(iTg + iTgGr + iTi + iCt, type='componentList', *resultComponentList)
        if flatten:
            cmds.setAttr(cr6000, type='pointArray', *resultPointArray)
            cmds.setAttr(cri6000, type='componentList', *resultComponentList)
    
    #print 'Calculation time: %s seconds -|- %s points needed to be calculated from a total of %s points of the Geo' %(round(float(time.time() - t), 2), len(calculated), numVtx)
    om.MGlobal.displayInfo('PSD calculation time: %s seconds // Points calculated: %s // Total Geo points: %s' %(round(float(time.time() - t), 2), len(calculated), numVtx))
    
    #return allData
    cmds.refresh()