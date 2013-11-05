'''
================================================================================
dslDeltaOptions.py - Python Script
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
    PROVIDE ALL FUNCTIONS TO MIRROR AND EDIT DELTAS OF 
    THE SCULPT INBETWEEN EDITOR TOOL

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

DATE: JAN/2012
RELEASE DATE: 01/13/13
LAST UPDATE: 06/06/2012
VERSION: 1.0
MAYA: 2010 ABOVE

'''

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.mel as mm
from functools import partial
from maya.OpenMaya import MVector
import itertools
import re
import bisect
import time




def statusBarWindow(maxValue=None, text='', selfDelete=False, edit=False, step=1, **args):

    if selfDelete:
        cmds.deleteUI('Processing', wnd=True)
    
    else:
        if edit:
            cmds.progressBar('progressBar', e=edit, s=step)
            cmds.text('textProg', e=True, label=text)
        else:
            cmds.window('Processing', wh=[310, 45], sizeable=False)
            cmds.formLayout('formProgressBar', height=30, parent='Processing')
            cmds.progressBar('progressBar', maxValue=maxValue, s=step, width=300, parent='formProgressBar', **args)
            cmds.text('textProg', label=text, parent='formProgressBar')
            cmds.formLayout('formProgressBar', e=True, af=[('progressBar', 'top', 5),
                                                           ('progressBar', 'left', 5),
                                                           ('progressBar', 'right', 5),
                                                           ('textProg', 'left', 10),
                                                           ('textProg', 'bottom', 5),
                                                           ('textProg', 'right', 10)])
            cmds.showWindow('Processing')
    
def createMirrorList(blendShapeNode, mirrorPlane='ZY', 
                     tolerance=0.00001, 
                     #checkPointsNotFound=False
                     ):
    #t = time.time()
    #===========================================================================
    # CREATE AN MIRROR WARNING WHEN GEOMETRY ISNT SYMMETRICAL
    #===========================================================================
    
    if mirrorPlane == 1:
        mirrorPlane = 'XY'
    elif mirrorPlane == 2:
        mirrorPlane = 'YZ'
    elif mirrorPlane == 3:
        mirrorPlane = 'XZ'

    geoName = getGeoNameFromNode(blendShapeNode)
    # Extract orgiShape to later get the mirror Sublists
    geoBase = cmds.ls(cmds.listRelatives(geoName), et='mesh',
                      intermediateObjects=True)
    
    #print '------geoBase-------> ', geoBase
    
    # If there is more than one origShape, select the right one
    if len(geoBase) != 1:
        for i in geoBase:
            listCon = cmds.listConnections(i, c=True)
            try:
                for c in listCon:
                    if '.worldMesh' in c: 
                        geoBase = i
                        break
            except:
                print 'Unused origShape: ', i
                pass
    else:
        geoBase = geoBase[0]
    #print '-------------> ', geoBase
    xListB = cmds.xform(geoBase + '.cp[*]', q=True, os=True, t=True)
    # Turn om the StatusBar
    
    countComp = int(len(xListB)/3)
    listString = []

    for x in xrange(countComp):
        listString.append(x)
    axis = mirrorPlaneReturn(mirrorPlane, mode='axis')

    # StatusBar Creation
    statusBarWindow(maxValue=countComp)
    cmds.refresh()

    '''
    geoBasePoints = zip(xListB[0::3],
                        xListB[1::3],
                        xListB[2::3],
                        listString * countComp)
    '''
    
    '''
    geoBasePoints = itertools.izip(xListB[0::3], 
                                   xListB[1::3], 
                                   xListB[2::3], 
                                   list(range(countComp))[0::])
    '''
    
    geoBasePoints = []
    subPoint = []
    lastValue = xListB[-1]
    for i in xrange(len(xListB)):
        #print i
        if len(subPoint) < 3:
            subPoint.append(xListB[i])
            if xListB[i] == lastValue and i == int(len(xListB)-1):
                #print 'vtx: %s = %s' %(i, xListB[i])
                #print 'OPAAAAA!'
                subPoint.append(len(geoBasePoints))
                geoBasePoints.append(subPoint)
        else:
            subPoint.append(len(geoBasePoints))
            geoBasePoints.append(subPoint)
            subPoint = []
            subPoint.append(xListB[i])
    #'''
    
    #print '....GeoBase: ', geoBasePoints
    #sorting
    lfunc = lambda c: c[axis]
    geoBasePoints.sort(key=lfunc)
    # Just the values corresponded to the axis
    geoAxisPoints = xListB[axis::3] 
    geoAxisPoints.sort()
    
    matchList = []
    labelText = 'Creating mirror table...'
    for v in xrange(len(geoBasePoints)):
        
        statusBarWindow(selfDelete=False, edit=True, step=1, text=labelText)
        pointA = (geoBasePoints[v][0], geoBasePoints[v][1], geoBasePoints[v][2])
        
        valueAxis = abs(pointA[axis])
        rList = bisectList(geoAxisPoints, valueAxis, tolerance)
        for p in range(rList[0], rList[1]):
            pointB = (geoBasePoints[p][0], geoBasePoints[p][1], geoBasePoints[p][2])

            if isMirrorPy(pointA, pointB, mirrorPlane, tolerance):
                #matchList.append([geoBasePoints[p][3], geoBasePoints[v][3]])
                #break
                if pointA[0] >= 0:
                    matchList.append([geoBasePoints[p][3], geoBasePoints[v][3]])
                else:
                    matchList.append([geoBasePoints[p][3], geoBasePoints[v][3]])
                break
    
    
    #print 'LEN matchList: ', len(matchList)
    #print 'matchList: ', matchList
    statusBarWindow(selfDelete=True, edit=False, step=1)
    #print "Time: %s" %(time.time() - t)
#    if checkPointsNotFound:
#        print '=== ', matchList
#        selectVtxFromMirrorList(blendShapeNode, mirrorList=matchList, mode='unmatched')
    
    
    return matchList

def checkMirrorList(blendShapeNode, mirrorList, check=True, sectionSelection='all'):
    #print 'def selectVtxFromMirrorList'
    
    allIndxFound = []
    positiveIndx = []
    negativeIndx = []
    centerIndx = []
    
    for i in mirrorList:
        if i[0] != i[1]:
            positiveIndx.append(i[0])
            negativeIndx.append(i[1])
            allIndxFound.append(i[0])
            allIndxFound.append(i[1])
        else:
            centerIndx.append(i[0])
            allIndxFound.append(i[0])
    
    '''
    print 'allIndxFound---> ',allIndxFound
    print 'positiveIndx---> ',positiveIndx
    print 'negativeIndx---> ',negativeIndx
    print 'centerIndx---> ',centerIndx
    '''
            
    cmds.select(cl=True)
    selectVtxFromIndices(blendShapeNode, listIndice=allIndxFound)
    mm.eval('invertSelection;')
    try:
        unmatchedVtx = cmds.ls(sl=True)
        if unmatchedVtx == []:
            unmatchedVtx = None
    except:
        unmatchedVtx = None
    
    cmds.select(cl=True)
    
    if check:
        if sectionSelection == 'all':
            print 'ALL'
            selectVtxFromIndices(blendShapeNode, listIndice=allIndxFound)
        elif sectionSelection == 'pos':
            selectVtxFromIndices(blendShapeNode, listIndice=positiveIndx)
        elif sectionSelection == 'neg':
            selectVtxFromIndices(blendShapeNode, listIndice=negativeIndx)
        elif sectionSelection == 'center':    
            selectVtxFromIndices(blendShapeNode, listIndice=centerIndx)
        elif sectionSelection == 'unmatched':
            cmds.select(unmatchedVtx)
    
    if unmatchedVtx:
        return False
    else:
        return True
    
def posNegCenterIndex(blendShapeNode, mirrorPlane='ZY', tolerance=0.00001):
    #print 'def posNegCenterIndex'

    #t = time.time()
    geoName = getGeoNameFromNode(blendShapeNode)
    # Extract orgiShape to later get the mirror Sublists
    geoBase = cmds.ls(cmds.listRelatives(geoName), et='mesh',
                      intermediateObjects=True)[0]
    
    xListB = cmds.xform(geoBase + '.cp[*]', q=True, os=True, t=True)
    # Turn om the StatusBar
    #statusBarWindow(maxValue=len(xListB)/3)
    
    countComp = int(len(xListB)/3)
    listString = []
    
    for x in xrange(countComp):
        listString.append(x)
    
    axis = mirrorPlaneReturn(mirrorPlane, mode='axis')
    
    '''
    geoBasePoints = zip(xListB[0::3],
                        xListB[1::3],
                        xListB[2::3],
                        listString * countComp)
    '''
    
    
    geoBasePoints = []
    subPoint = []
    lastValue = xListB[-1]
    for i in xrange(len(xListB)):
        if len(subPoint) < 3:
            subPoint.append(xListB[i])
            if xListB[i] == lastValue and i == int(len(xListB)-1):
                subPoint.append(len(geoBasePoints))
                geoBasePoints.append(subPoint)
        else:
            subPoint.append(len(geoBasePoints))
            geoBasePoints.append(subPoint)
            subPoint = []
            subPoint.append(xListB[i])
    
    pos = []
    neg = []
    center = []
    for pi in xrange(len(geoBasePoints)):
        if geoBasePoints[pi][axis] > tolerance:
            pos.append(pi)
        elif geoBasePoints[pi][axis] < -tolerance:
            neg.append(pi)
        else:
            center.append(pi)
    pnc = [pos, neg, center]
    #print "Time: %s" %(time.time() - t)
    return pnc
     
def bisectList(listPoint, axisValue, tolerance):
    
    rangeList = []
    minValue = axisValue - tolerance
    maxValue = axisValue + tolerance        
    rangeList.append(bisect.bisect_left(listPoint, minValue))
    rangeList.append(bisect.bisect_left(listPoint, maxValue))        
    
    return rangeList
    

def isMirrorOpen(A, B, mirrorPlane, tolerance):
    
    nAxis = mirrorPlaneReturn(mirrorPlane, mode='nAxis')
    A = (nAxis[0] * A[0], nAxis[1] * A[1], nAxis[2] * A[2])
    mvA = MVector(*A)
    mvB = MVector(*B)
    diffVector = mvA - mvB
    if diffVector.length() < tolerance:
        return True
    else:
        return False
        
def isMirrorPy(A, B, mirrorPlane, tolerance):
    
    nAxis = mirrorPlaneReturn(mirrorPlane, mode='nAxis')
    mirrorA = (nAxis[0] * A[0], nAxis[1] * A[1], nAxis[2] * A[2])
    for i in range(3):
        if abs(mirrorA[i] - B[i]) > tolerance:
            return False
    
    return True

def mirrorPlaneReturn(mirrorPlane, mode='nAxis'):
    
    if mirrorPlane == 'ZY' or mirrorPlane == 'YZ':
        axis = 0
        nAxis = (-1.0, 1.0, 1.0)
        zAxis = (0, 1.0, 1.0) 
    elif mirrorPlane == 'ZX' or mirrorPlane == 'XZ':
        axis = 1
        nAxis = (1.0, -1.0, 1.0)
        zAxis = (1.0, 0, 1.0) 
    elif mirrorPlane == 'XY' or mirrorPlane == 'YX':
        axis = 2
        nAxis = (1.0, 1.0, -1.0)
        zAxis = (1.0, 1.0, 0) 

    if mode == 'nAxis':
        return nAxis
    elif mode == 'axis':
        return axis
    elif mode == 'zAxis':
        return zAxis
def getGeoNameFromNode(blendShapeNode=None, arg=None): 
    # Ja existe no dslCorrectiveManager
       
    hist = cmds.listHistory(blendShapeNode, f=True)
    shapeGeo = cmds.ls(hist, type='mesh')
    geoName = cmds.listRelatives(shapeGeo, ap=True)[0]
    
    return geoName

    
def combinePointIndex(blendShapeNode=None, correctiveGroup=None, correctiveItem=None):
    #print 'def combinePointIndex'
    # Combine the Point and Indexes into sublist (X, Y, Z, vtxNumber), ex: (-0.2749, 0.22717, 0.0, 92)

    pointData = getApplyPI(blendShapeNode, correctiveGroup, correctiveItem, mode='getPoint')
    componentData = getApplyPI(blendShapeNode, correctiveGroup, correctiveItem, mode='getIndex')
    
    try:
        pointIndex = []
        for p in xrange(len(pointData)):
            pointIndex.append((pointData[p][0], pointData[p][1], pointData[p][2], componentData[p]))
    except:
        cmds.select(cl=True)
        pass
                    
    return pointIndex

def prepareWeightsToBake(blendShapeNode=None, correctiveGroup=None, correctiveItem=None, type='prepareTargetWeights'):
    print 'def prepareWeightsToBake'
    

def wipeOutWeights(blendShapeNode=None, correctiveGroup=None, correctiveItem=None, type='wipeTargetWeights'):
    
    iTg = '%s.inputTarget[0]' %blendShapeNode
    iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
    bsW = '.baseWeights'
    tW = '.targetWeights'
    
    if type == 'wipeTargetWeights':
        stringList = cmds.listAttr(iTg + iTgGr + tW, m=True)
        for i in xrange(len(stringList)):
            cmds.removeMultiInstance(blendShapeNode + '.' + stringList[i])
    elif type == 'wipeBaseWeights':
        stringList = cmds.listAttr(iTg + bsW, m=True)
        for i in xrange(len(stringList)):
            #print i
            cmds.removeMultiInstance(blendShapeNode + '.' + stringList[i])

def getApplyPI(blendShapeNode=None, correctiveGroup=None, correctiveItem=None, 
               mode='getPoint', pointData=None, componentData=None, weightData=None):
    #print 'def getIndex'
    # Get Point or unflatten Indexes of the target. Ex: [(x, y, z)] // [2,3,4,5,78,79,80...]
    iTg = '%s.inputTarget[0]' %blendShapeNode
    iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
    iTi = '.inputTargetItem[%s]' %correctiveItem
    iPt = '.inputPointsTarget'
    iCt = '.inputComponentsTarget'
    bsW = '.baseWeights'
    tW = '.targetWeights'
    
    #===========================================================================
    # GET MODES
    #===========================================================================
    
    if mode == 'getPoint':
        return cmds.getAttr(iTg + iTgGr + iTi + iPt)
    elif mode == 'getIndex':
        componentData = cmds.getAttr(iTg + iTgGr + iTi + iCt)
        return unflattenList(stringList=componentData)
    elif mode == 'getBaseWeights':
        #print 'getBaseWeights'
        tgtWeights = cmds.getAttr(iTg + bsW)[0]
        tgtIndex = cmds.getAttr(iTg + bsW, mi=True)
        tgtIndexWeights = []
        try:
            for i in xrange(len(tgtIndex)):
                tWi = '.baseWeights[%s]' %i
                subList = (tgtIndex[i], tgtWeights[i])
                tgtIndexWeights.append(subList)
                #cmds.removeMultiInstance(iTg + iTgGr + tWi)
            return tgtIndexWeights
        except:
            return None
    elif mode == 'getTargetWeights':
        # Ex: (index, value)
        tgtWeights = cmds.getAttr(iTg + iTgGr + tW)[0]
        tgtIndex = cmds.getAttr(iTg + iTgGr + tW, mi=True)
        tgtIndexWeights = []
        try:
            for i in xrange(len(tgtIndex)):
                tWi = '.targetWeights[%s]' %i
                subList = (tgtIndex[i], tgtWeights[i])
                tgtIndexWeights.append(subList)
                #cmds.removeMultiInstance(iTg + iTgGr + tWi)
            return tgtIndexWeights
        except:
            return None
    
    #===========================================================================
    # APPLY MODES
    #===========================================================================
    
    elif mode == 'applyPoint':
        cmds.setAttr(iTg + iTgGr + iTi + iPt, type='pointArray', *pointData)
    elif mode == 'applyIndex':
        cmds.setAttr(iTg + iTgGr + iTi + iCt, type='componentList', *componentData)
    elif mode == 'applyBaseWeights':
        stringList = cmds.listAttr(iTg + bsW, m=True)
        try:
            for i in xrange(len(stringList)):
                cmds.removeMultiInstance(blendShapeNode + '.' + stringList[i])
        except:
            pass
        try:
            for w in xrange(len(weightData)):
                bsWi = '.baseWeights[%s]' %weightData[w][0]
                cmds.setAttr(iTg + bsWi, weightData[w][1])
        except:
            pass
    elif mode == 'applyTargetWeights':
        stringList = cmds.listAttr(iTg + iTgGr + tW, m=True)
        try:
            for i in xrange(len(stringList)):
                cmds.removeMultiInstance(blendShapeNode + '.' + stringList[i])
        except:
            pass
#        for w in xrange(len(weightData)):
#            tWi = '.targetWeights[%s]' %weightData[w][0]
#            cmds.removeMultiInstance(iTg + iTgGr + tWi)
        try:
            for w in xrange(len(weightData)):
                tWi = '.targetWeights[%s]' %weightData[w][0]
                cmds.setAttr(iTg + iTgGr + tWi, weightData[w][1])
        except:
            pass
            
    
            

def unflattenList(stringList):
    #print 'def unflattenList'
    # Extract and unflatten numbers and string list, ex: vtx[97:108] // u'main.vtx[154:172]'
    compileExp = re.compile('\d+') 
    rangeVtxSublists = []
    
    # flatten string with number list like: vtx[97:108]
    for u in stringList:
        #print u
        rangeVtx = list(compileExp.findall(u.split('.')[-1]))
        rangeVtxSublists.append(rangeVtx) 
    
    #print rangeVtxSublists
    
    indexSort = []
    for u in rangeVtxSublists:
        # If sublist have more than 1 item, ex: vtx[97:108]
        if len(u) > 1:
            indxLs = range(int(u[0]), int(u[1])) + [int(u[1])]
            for i in indxLs:
                indexSort.append(int(i))
        else:
            indexSort.append(int(u[0]))
    
    return indexSort    

def selectVtxFromIndices(blendShapeNode, listIndice=None):
    #print 'def selectVtxFromIndices'
    selObj = getGeoNameFromNode(blendShapeNode)
    selVtxList = []
    for i in listIndice:
        selVtxList.append('%s.vtx[%s]' %(selObj, i))
    cmds.select(selVtxList)


def selectionUser(blendShapeNode=None, correctiveGroup=None, correctiveItem=None, vtxList=None):
    #print 'def userVtxSelection'
    
    unflattenList(stringList=vtxList)

   
def deltaTool(blendShapeNode, correctiveGroup, correctiveItem, mirrorPlane, mirrorSide,
              mode, pruneValue, factorValue, factorAdd, originalPointIndex, tolerance):    
    #print 'def deltaTool'
    # Funcion that correspond the Delta Option TAP from the UI. The options PRUNE, FACTOR, ZERO

    
    '''
    mirrorPlane:
    1 = 'XY'
    2 = 'YZ'
    3 = 'XZ'
    
    mirrorSide:
    1 = Pos
    2 = Neg
    3 = All
    4 = User    
    '''
    
    if mirrorPlane == 1:
        mirrorPlane = 'XY'
    elif mirrorPlane == 2:
        mirrorPlane = 'YZ'
    elif mirrorPlane == 3:
        mirrorPlane = 'XZ'
        
    if mirrorSide == 1:
        positive = True
        allDeltaIndx = None
        selectionUser = None
    elif mirrorSide == 2:
        positive = False
        allDeltaIndx = None
        selectionUser = None
    elif mirrorSide == 3:
        positive = None
        allDeltaIndx = True
        selectionUser = None
    elif mirrorSide == 4:
        positive = None
        allDeltaIndx = None
        selectionUser = True
    
    
    pointIndex = combinePointIndex(blendShapeNode, correctiveGroup, correctiveItem)
    # Gets all index from the data acquired of the corrective
    deltaIndx = []
    for u in pointIndex:
        deltaIndx.append(int(u[-1]))
        
    #if not pnc:
    #    print 'creating PNC data...'
    #    pnc = posNegCenterIndex(blendShapeNode, mirrorPlane, tolerance)
        
        #print pnc
    #print 'pnc: ', pnc
    
    pnc = posNegCenterIndex(blendShapeNode, mirrorPlane, tolerance)
    posIndx = pnc[0]
    negIndx = pnc[1]
    zeroIndx = pnc[2]     
    
    # Analyzing Selection Format                
    if selectionUser:
        #print 'selectionUser is the priority'
        sideIndx = []
        try:
            userSel = unflattenList(cmds.ls(sl=True))
            for i in userSel:
                if i in deltaIndx:
                    sideIndx.append(i)
        except:
            om.displayInfo('There is no vertices selected by the user')
        
    elif allDeltaIndx:
        # Act in all delta points
        sideIndx = posIndx + negIndx + zeroIndx
    else:
        # Else, check if the posToNeg is to continue the sideIndx as pos or neg index
        if positive:
            sideIndx = posIndx + zeroIndx
        else:
            sideIndx = negIndx + zeroIndx
    
    indexResult = []
    if mode == 'prune':
        pointIndexList = []
        for pi in xrange(len(pointIndex)):
            if pointIndex[pi][3] in sideIndx:
                if not isPruned(pointIndex[pi], pruneValue):
                    pointIndexList.append(pointIndex[pi])
                    indexResult.append(pointIndex[pi][3])
            else:
                pointIndexList.append(pointIndex[pi])
                indexResult.append(pointIndex[pi][3])        

    elif mode == 'factor':
        pointIndexList = []
        for pi in xrange(len(pointIndex)):
            if pointIndex[pi][3] in sideIndx:
                pointIndexList.append(factorPoint(pointIndex[pi], 
                                                  originalPointIndex[pi], 
                                                  factorAdd, factorValue))
                indexResult.append(pointIndex[pi][3])
            else:
                pointIndexList.append(pointIndex[pi])
                indexResult.append(pointIndex[pi][3])
    
    elif mode == 'zero':
        pointIndexList = []
        for pi in xrange(len(pointIndex)):
            if pointIndex[pi][3] in sideIndx:
                pZero = (0.0, 0.0, 0.0, pointIndex[pi][3])
                pointIndexList.append(pZero)
                indexResult.append(pointIndex[pi][3])
            else:
                pointIndexList.append(pointIndex[pi])
                indexResult.append(pointIndex[pi][3])
                
    elif mode == 'reset':
        pointIndexList = []
        for pi in xrange(len(pointIndex)):
            if pointIndex[pi][3] in sideIndx:
                pReset = (originalPointIndex[pi][0],originalPointIndex[pi][1],
                          originalPointIndex[pi][2], pointIndex[pi][3])
                pointIndexList.append(pReset)
                indexResult.append(pointIndex[pi][3])
            else:
                pointIndexList.append(pointIndex[pi])
                indexResult.append(pointIndex[pi][3])
    '''
    elif mode == 'check':
        selectVtxFromIndices(blendShapeNode, deltaIndx)
    '''
    deltaData = indexPointToDeltaData(pointIndexList)
    # Apply data to the array values
    getApplyPI(blendShapeNode, correctiveGroup, correctiveItem, mode='applyPoint', 
               pointData=deltaData[0])
    getApplyPI(blendShapeNode, correctiveGroup, correctiveItem, mode='applyIndex', 
               componentData=deltaData[1])                   
    
    cmds.refresh()
    if mirrorSide != 4:
        try:
            selectVtxFromIndices(blendShapeNode, indexResult)
        except:
            'There is no Delta to be showed'
            pass
    
    #selectVtxFromIndices(blendShapeNode, listIndice=negIndx)
    #print 'List before Pruning: ', pointIndex
    #print 'List After Pruning: ', pointIndexList
    return pointIndex

def isPruned(point, pruneValue):
    #print pruneValue
    #Return True if point delta is bellow pruneValue
    point = (point[0], point[1], point[2])
    for i in range(3):
        if abs(point[i]) > pruneValue:
            return False
    return True

def factorPoint(point, originalPoint, factorAdd, factorValue):
    #print 'def factorDelta'
    # Factor Formula
    
    factoredPoint = []
    for i in range(3):
        if factorAdd:
            factoredPoint.append(point[i] + (originalPoint[i] * factorValue))
        else:
            factoredPoint.append(point[i] - (originalPoint[i] * factorValue)) 
    factoredPoint.append(point[-1])
    return factoredPoint

def mirrorTargetWeights(blendShapeNode, correctiveGroup, mirrorPlane='ZY', 
                        posToNeg=True, flipModel=False, tolerance=0.00001, 
                        mirrorList=None, 
                        getMode='getBaseWeights', 
                        applyMode='applyBaseWeights'):
    
    '''
    print 'blendShapeNode---> ',blendShapeNode
    print 'correctiveGroup---> ',correctiveGroup
    print 'mirrorPlane---> ',mirrorPlane
    print 'posToNeg---> ',posToNeg
    print 'flipModel---> ',flipModel
    print 'tolerance---> ',tolerance
    print 'mirrorList---> ',mirrorList
    '''
    
    
    tgtIndexWeights =  getApplyPI(blendShapeNode, correctiveGroup, mode=getMode)
    print '###### ', str(blendShapeNode) + ' ' +  str(correctiveGroup) + ' ' + str(getMode)
    if not tgtIndexWeights:
        om.MGlobal.displayError('There is no Weight')
 
    else:
        if not mirrorList:
            mirrorList = createMirrorList(blendShapeNode, mirrorPlane, tolerance)
            #print mirrorList
        
        
        positiveIndx = []
        for i in mirrorList:
            if i[0] != i[1]:
                positiveIndx.append(i[0])
        
        #Selecting...
        #selectVtxFromIndices(blendShapeNode, positiveIndx)
                
        wIndex = []
        for wi in xrange(len(tgtIndexWeights)):
            wIndex.append(list(tgtIndexWeights[wi])[0])
        
        posIndx = [] 
        negIndx = []
        zeroIndx = []   
        for x in xrange(len(wIndex)):
            if wIndex[x] in positiveIndx:
                posIndx.append(wIndex[x])
            else:
                for mi in mirrorList:
                    if mi[0] != mi[1]:
                        if wIndex[x] == mi[1]:
                            negIndx.append(wIndex[x])
                            break
                    else:
                        zeroIndx.append(wIndex[x])
                        break
        
        if flipModel:
            # Flip everything no matter the option of PosToNeg checkBox
            sideIndx = posIndx + negIndx + zeroIndx
        else:
            # Else, check if the posToNeg is to continue the sideIndx as pos or neg index
            if posToNeg:
                sideIndx = posIndx + zeroIndx
            else:
                sideIndx = negIndx + zeroIndx
        
        
        weightIndexMirroed = []
        if not flipModel:
            # MIRROR MODE
            for pi in xrange(len(wIndex)):
                #print wIndex[pi]
                
                if wIndex[pi] in sideIndx:
                    checkedIndx = wIndex[pi]
                    # Check in the mirror List
                    for mi in mirrorList:
                        if posToNeg:
                            if mi[0] == checkedIndx:
                                if mi[1] != mi[0]:
                                    subList = (mi[1], tgtIndexWeights[pi][1])
                                    subList2 = (mi[0], tgtIndexWeights[pi][1])
                                    weightIndexMirroed.append(subList)
                                    weightIndexMirroed.append(subList2)
                                    break
                                else:
                                    subList = (checkedIndx, tgtIndexWeights[pi][1])
                                    weightIndexMirroed.append(subList)
                                    break
                                
                        else:
                            if mi[1] == checkedIndx:
                                if mi[1] != mi[0]:
                                    subList = (mi[0], tgtIndexWeights[pi][1])
                                    subList2 = (mi[1], tgtIndexWeights[pi][1])
                                    weightIndexMirroed.append(subList)
                                    weightIndexMirroed.append(subList2)
                                    break
                                else:
                                    subList = (checkedIndx, tgtIndexWeights[pi][1])
                                    weightIndexMirroed.append(subList)
                                    break
            
        else:
            # FLIP MODE
            #print 'FLIP MODE'
            for pi in xrange(len(wIndex)):
                if wIndex[pi] in sideIndx:
                    checkedIndx = wIndex[pi]
                    for mi in mirrorList:
                        if mi[0] == checkedIndx:
                            subList = (mi[1], tgtIndexWeights[pi][1])
                            weightIndexMirroed.append(subList)
                            break
                        elif mi[1] == checkedIndx:
                            subList = (mi[0], tgtIndexWeights[pi][1])
                            weightIndexMirroed.append(subList)
                            break
        
        
                
        '''
        print 'tgtIndexWeights: ', tgtIndexWeights
        print 'weightIndexMirroed: ', weightIndexMirroed
        print 'sideIndx: ', sideIndx
        print 'pos', posIndx
        print 'neg', negIndx
        print 'zero', zeroIndx
        '''
        
        print len(weightIndexMirroed)
        # Applying weightData mirroed back to the target:               
        getApplyPI(blendShapeNode, correctiveGroup, mode=applyMode, weightData=weightIndexMirroed)
        cmds.refresh()

def mirrorCorrectiveData(blendShapeNode, correctiveGroup, correctiveItem, 
                         mirrorPlane, posToNeg, flipModel, tolerance, mirrorList):
    
    #t = time.time()

    componentData = getApplyPI(blendShapeNode, correctiveGroup, correctiveItem, mode='getIndex')
    
    if not componentData:
        print '# Item: %s - Group: %s does not have Delta to be processed' %(correctiveItem, correctiveGroup)
    else:
        nAxis = mirrorPlaneReturn(mirrorPlane, mode='nAxis')
        zAxis = mirrorPlaneReturn(mirrorPlane, mode='zAxis') 
        
        # combine point and index into sublists (X, Y, Z, vtxNumber), ex: (-0.2749, 0.22717, 0.0, 92)
        pointIndex = combinePointIndex(blendShapeNode, correctiveGroup, correctiveItem)
        
        # Create mirror subLists [[23, 45], [25, 47]...]
        if not mirrorList:
            mirrorList = createMirrorList(blendShapeNode, mirrorPlane, tolerance)
        
        positiveIndx = []
        for i in mirrorList:
            if i[0] != i[1]:
                positiveIndx.append(i[0])
            
        #Selecting...
        #selectVtxFromIndices(blendShapeNode, positiveIndx)
        
        # Gets all index from the data acquired of the corrective
        deltaIndx = []
        for u in pointIndex:
            deltaIndx.append(int(u[-1]))
    
        # Separating what is positive, negative or middle based on position of the
        # index of the sublist and if they are the same result the middle. 
        # Left > Post // Right > Neg
        # Ex: [[15, 13], [3, 1], [10, 10],...]  the number 15, 3 are Positive while 
        # 13, 1 are Negative and the 10 is the middle 
        posIndx = [] 
        negIndx = []
        zeroIndx = []   
        for x in xrange(len(deltaIndx)):
            if deltaIndx[x] in positiveIndx:
                posIndx.append(deltaIndx[x])
            else:
                for mi in mirrorList:
                    if mi[0] != mi[1]:
                        if deltaIndx[x] == mi[1]:
                            negIndx.append(deltaIndx[x])
                            break
                    else:
                        zeroIndx.append(deltaIndx[x])
                        break
        
        
                    
        #print '}}positive}}}', posIndx
        #print '}}negative}}}', negIndx
        #print '}}zero}}}}}}}', zeroIndx
        
        if flipModel:
            # Flip everything no matter the option of PosToNeg checkBox
            sideIndx = posIndx + negIndx + zeroIndx
        else:
            # Else, check if the posToNeg is to continue the sideIndx as pos or neg index
            if posToNeg:
                sideIndx = posIndx + zeroIndx
            else:
                sideIndx = negIndx + zeroIndx
        
        pointIndexMirroed = []
        # loop at the length of the pointIndex (See annotation above)
        if not flipModel:
            # MIRROR MODE
            for pi in xrange(len(pointIndex)):
                if pointIndex[pi][3] in sideIndx:
                    checkedIndx = pointIndex[pi][3]
                    # Check in the mirror List
                    for mi in mirrorList:
                        if posToNeg:
                            if mi[0] == checkedIndx:
                                if mi[1] != mi[0]:
                                    pointIndexMirroed.append(mirrorPointIndex(pointIndex[pi], mi[1], nAxis))
                                    pointIndexMirroed.append(mirrorPointIndex(pointIndex[pi], mi[0], nAxis=None))
                                    break
                                else:
                                    pointIndexMirroed.append(mirrorPointIndex(pointIndex[pi], pointIndex[pi][3], zAxis))
                                    break
                                
                        else:
                            if mi[1] == checkedIndx:
                                if mi[1] != mi[0]:
                                    pointIndexMirroed.append(mirrorPointIndex(pointIndex[pi], mi[0], nAxis))
                                    pointIndexMirroed.append(mirrorPointIndex(pointIndex[pi], mi[1], nAxis=None))
                                    break
                                else:
                                    pointIndexMirroed.append(mirrorPointIndex(pointIndex[pi], pointIndex[pi][3], zAxis))
                                    break
            
        else:
            # FLIP MODE
            for pi in xrange(len(pointIndex)):
                if pointIndex[pi][3] in sideIndx:
                    checkedIndx = pointIndex[pi][3]
                    for mi in mirrorList:
                        if mi[0] == checkedIndx:
                            pointIndexMirroed.append(mirrorPointIndex(pointIndex[pi], mi[1], nAxis))
                            break
                        elif mi[1] == checkedIndx:
                            #print mi[1]
                            pointIndexMirroed.append(mirrorPointIndex(pointIndex[pi], mi[0], nAxis))
                            break
  
        # Ordering and preparing list to be applied after
        deltaData = indexPointToDeltaData(pointIndexList=pointIndexMirroed)
        
        # Apply data to the array values
        getApplyPI(blendShapeNode, correctiveGroup, correctiveItem, mode='applyPoint', pointData=deltaData[0])
        getApplyPI(blendShapeNode, correctiveGroup, correctiveItem, mode='applyIndex', componentData=deltaData[1])

def indexPointToDeltaData(pointIndexList=None):
    # return one list with 2 sublist corresponding to point and component list 
    # ready to be applied to the blendShapeNode.
    # pointIndexList ex: [(-9.2, 7.4, -9.5, 201), (-26.0, 21.0, -26.7, 202), (-91.3, 73.5, -93.6, 203), ...
    #print 'def indexPointToDeltaData'
    
    pointData = []
    componentData = []
    lambFunc = lambda c: c[-1]
    pointIndexList.sort(key=lambFunc)
        
    for dm in pointIndexList:
        pointData.append((dm[0], dm[1], dm[2], 1.0))
        # Pattern for the component Array
        componentData.append('vtx[%s]' %dm[3])
    
    pointData.insert(0, len(pointData))
    componentData.insert(0, len(componentData))
    
    return [pointData, componentData]
    

def mirrorPointIndex(point, indx, nAxis):
    if nAxis:
        mPIndex = ((point[0] * nAxis[0], 
                    point[1] * nAxis[1], 
                    point[2] * nAxis[2], 
                    indx))
    else:
        mPIndex = ((point[0], point[1], point[2], indx))
    return mPIndex
    