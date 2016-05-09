import os
import traceback

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
        # export alembic
        if not path:
            fileFilter = "Alembic Files (*.abc)"
            path = pm.fileDialog2(fileFilter=fileFilter, dialogStyle=1,
                                  fileMode=3)

        if path:
            currentFile = cmds.file(q=True, sn=True)
            path = path[0].replace('\\', '/')

            # collecting export objects
            cmd = ''
            for obj in pm.ls(selection=True, long=True):
                cmd = ' -root ' + obj

                # get time range
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


def Connect(src, dst):

    pm.undoInfo(openChunk=True)

    alembics = src
    if not isinstance(src, list):
        alembics = pm.ls(src, dagObjects=True, type='transform')

    targets = dst
    if not isinstance(dst, list):
        targets = pm.ls(dst, dagObjects=True, type='transform')

    attrs = ['translate', 'rotate', 'scale', 'visibility']
    for node in targets:
        for abc in alembics:
            if node.longName().split(':')[-1] == abc.longName().split(':')[-1]:
                for attr in attrs:
                    pm.connectAttr('%s.%s' % (abc, attr),
                                   '%s.%s' % (node, attr),
                                   force=True)

                # securing primary shape is connected
                pm.connectAttr('%s.worldMesh[0]' % abc.getShape(),
                               '%s.inMesh' % node.getShape(),
                               force=True)

    pm.undoInfo(closeChunk=True)


def SetupAlembic(alembicFile, shaderFile):

    # reference alembic file
    filename = os.path.basename(alembicFile)
    newNodes = cmds.file(alembicFile, reference=True, namespace=filename,
                         groupReference=True, groupName='NewReference',
                         returnNewNodes=True)

    alembicRoot = None
    for node in newNodes:
        if node == '|NewReference':
            alembicRoot = pm.PyNode(node)
            cmds.rename('%s:grp' % filename)

    # reference shader file
    filename = os.path.basename(shaderFile)
    newNodes = cmds.file(shaderFile, reference=True, namespace=filename,
                         groupReference=True, groupName='NewReference',
                         returnNewNodes=True)

    shaderRoot = None
    for node in newNodes:
        if node == '|NewReference':
            shaderRoot = pm.PyNode(node)
            cmds.rename('%s:grp' % filename)

    # connecting shader to alembic
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
