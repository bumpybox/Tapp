import os

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


def loadAlembic():

    pm.loadPlugin('AbcExport.mll', quiet=True)
    pm.loadPlugin('AbcImport.mll', quiet=True)


def Export(path=None):

    loadAlembic()

    sel = pm.ls(selection=True)

    if sel:
        #export alembic
        if not path:
            fileFilter = "Alembic Files (*.abc)"
            path = pm.fileDialog2(fileFilter=fileFilter, dialogStyle=1,
                                    fileMode=3)

        if path:
            currentFile = cmds.file(q=True, sn=True)
            path = path[0].replace('\\', '/')

            #collecting export objects
            cmd = ''
            for obj in pm.ls(selection=True, long=True):
                cmd = ' -root ' + obj

                #get time range
                start = pm.playbackOptions(q=True, animationStartTime=True)
                end = pm.playbackOptions(q=True, animationEndTime=True)

                melCmd = 'AbcExport -j \"-frameRange %s %s' % (start, end)
                melCmd += ' -writeVisibility -uvWrite -worldSpace %s -file' % cmd
                fileName = obj.split(':')[0].replace('|', '') + '.'
                fileName += os.path.basename('.'.join(currentFile.split('.')[1:-1]))
                fileName += '.abc'
                melCmd += ' \\\"%s\\\"\";' % (path + '/' + fileName)
                mel.eval(melCmd)
        else:
            pm.warning('No path chosen!')

    else:
        pm.warning('No nodes selected!')


def Import():

    loadAlembic()

    fileFilter = "Alembic Files (*.abc)"
    files = pm.fileDialog2(fileFilter=fileFilter, dialogStyle=1,
                            fileMode=4)

    if files:
        for f in files:
            filename = os.path.basename(f)
            newNodes = cmds.file(f, reference=True, namespace=filename,
                                 groupReference=True, groupName='NewReference',
                                 returnNewNodes=True)

            for node in newNodes:
                if node == '|NewReference':
                    pm.rename('%s:grp' % filename)


def getConnectedAttr(node, connectShapes=True):
    data = {}

    if connectShapes:
        shapes = pm.listRelatives(node, shapes=True, fullPath=True)
        if shapes:
            for shp in shapes:
                data = getConnectedAttr(shp)

    exceptions = ['message', 'instObjGroups']
    for attr in pm.listAttr(node, connectable=False):
        if attr not in exceptions:
            try:
                if pm.listConnections('%s.%s' % (node, attr),
                                        connections=True):
                    data[attr] = pm.listConnections('%s.%s' % (node, attr),
                                                      plugs=True)[0]
            except:
                pass

    return data


def Blendshape(source, target):

    blendshape = pm.blendShape(source, target)[0]
    pm.setAttr('%s.%s' % (blendshape, source.split(':')[-1]), 1)


def CopyTransform(source, target):

    t = pm.xform(source, q=True, ws=True, translation=True)
    r = pm.xform(source, q=True, ws=True, rotation=True)
    s = pm.xform(source, q=True, ws=True, scale=True)

    pm.xform(target, ws=True, translation=t)
    pm.xform(target, ws=True, rotation=r)
    pm.xform(target, ws=True, scale=s)


def Connect(alembicRoot, targetRoot, connectShapes=True):

    pm.undoInfo(openChunk=True)

    alembics = pm.ls(alembicRoot, dagObjects=True, long=True)
    targets = pm.ls(targetRoot, dagObjects=True, long=True)
    for node in targets:
        for abc in alembics:
            if node.split(':')[-1] == abc.split(':')[-1]:

                #get connection attributes
                data = getConnectedAttr(abc, connectShapes)

                #connects any animated node
                if data:
                    for attr in data:
                        try:
                            pm.connectAttr(data[attr],
                                             '%s.%s' % (node, attr),
                                             force=True)
                            CopyTransform(abc, node)
                        except:
                            pass
                #connects any static node
                else:
                    try:
                        #copy transform and blendshape to ensure placement
                        CopyTransform(abc, node)
                        Blendshape(abc, node)

                    except:
                        pass

                #adding user defined attrs to all shapes
                if node.nodeType() == 'mesh':
                    shapes = node.getParent().getShapes()
                    for shp in shapes:
                        for attr in node.listAttr(userDefined=True):
                            attrType = pm.getAttr(attr, type=True)
                            try:
                                shp.addAttr(attr.split('.')[-1],
                                               attributeType=attrType,
                                               defaultValue=attr.get())
                            except:
                                pass

    pm.undoInfo(closeChunk=True)

def SetupAlembic(alembicFile, shaderFile):
    
    #reference alembic file
    filename = os.path.basename(alembicFile)
    newNodes = cmds.file(alembicFile, reference=True, namespace=filename,
                         groupReference=True, groupName='NewReference',
                         returnNewNodes=True)

    alembicRoot = None
    for node in newNodes:
        if node == '|NewReference':
            alembicRoot = pm.PyNode(node)
            cmds.rename('%s:grp' % filename)

    #reference shader file
    filename = os.path.basename(shaderFile)
    newNodes = cmds.file(shaderFile, reference=True, namespace=filename,
                         groupReference=True, groupName='NewReference',
                         returnNewNodes=True)

    shaderRoot = None
    for node in newNodes:
        if node == '|NewReference':
            shaderRoot = pm.PyNode(node)
            cmds.rename('%s:grp' % filename)
    
    #connecting shader to alembic
    Connect(alembicRoot, shaderRoot)
    alembicRoot.v.set(0)

def SetupAlembicInput():
    
    loadAlembic()

    fileFilter = 'Alembic Files (*.abc)'
    title = 'Select Alembic caches'
    files = pm.fileDialog2(fileFilter=fileFilter, dialogStyle=1,
                            fileMode=4, caption=title)

    data = {}
    if files:
        for f in files:
            fileFilter = 'Maya Files (*.ma *.mb)'
            title = 'Select shader file for %s' % os.path.basename(f)
            maFile = pm.fileDialog2(fileFilter=fileFilter, dialogStyle=1,
                                    fileMode=1, caption=title)
            
            if maFile:
                data[f] = maFile[0]

    for k in data:
        SetupAlembic(k, data[k])
