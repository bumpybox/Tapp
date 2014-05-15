import os

import maya.cmds as cmds
import maya.mel as mel


def loadAlembic():

    cmds.loadPlugin('AbcExport.mll', quiet=True)
    cmds.loadPlugin('AbcImport.mll', quiet=True)


def Export():

    loadAlembic()

    sel = cmds.ls(selection=True)

    path = []
    if sel:
        #export alembic
        fileFilter = "Alembic Files (*.abc)"
        path = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=1,
                                fileMode=3)

        if path:
            currentFile = cmds.file(q=True, sn=True)
            path = path[0].replace('\\', '/')

            #collecting export objects
            cmd = ''
            for obj in cmds.ls(selection=True, long=True):
                cmd = ' -root ' + obj

                #get time range
                start = cmds.playbackOptions(q=True, animationStartTime=True)
                end = cmds.playbackOptions(q=True, animationEndTime=True)

                melCmd = 'AbcExport -j \"-frameRange %s %s' % (start, end)
                melCmd += ' -writeVisibility -uvWrite -worldSpace %s -file' % cmd
                fileName = obj.split(':')[0].replace('|', '') + '.'
                fileName += os.path.basename('.'.join(currentFile.split('.')[1:-1]))
                fileName += '.abc'
                melCmd += ' \\\"%s\\\"\";' % (path + '/' + fileName)
                mel.eval(melCmd)
        else:
            cmds.warning('No path chosen!')

    else:
        cmds.warning('No nodes selected!')


def Import():

    loadAlembic()

    fileFilter = "Alembic Files (*.abc)"
    files = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=1,
                            fileMode=4)

    if files:
        for f in files:
            filename = os.path.basename(f)
            newNodes = cmds.file(f, reference=True, namespace=filename,
                                 groupReference=True, groupName='NewReference',
                                 returnNewNodes=True)

            for node in newNodes:
                if node == '|NewReference':
                    cmds.rename('%s:grp' % filename)


def getConnectedAttr(node, connectShapes=True):
    data = {}

    if connectShapes:
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True)
        if shapes:
            for shp in shapes:
                data = getConnectedAttr(shp)

    exceptions = ['message', 'instObjGroups']
    for attr in cmds.listAttr(node, connectable=False):
        if attr not in exceptions:
            try:
                if cmds.listConnections('%s.%s' % (node, attr),
                                        connections=True):
                    data[attr] = cmds.listConnections('%s.%s' % (node, attr),
                                                      plugs=True)[0]
            except:
                pass

    return data


def Connect(connectShapes=True):

    cmds.undoInfo(openChunk=True)

    sel = cmds.ls(selection=True)
    alembic = sel[0]
    target = sel[1]

    alembics = cmds.ls(alembic, dagObjects=True, long=True)
    targets = cmds.ls(target, dagObjects=True, long=True)
    for node in targets:
        for abc in alembics:
            if node.split(':')[-1] == abc.split('|')[-1]:
                data = getConnectedAttr(abc, connectShapes)
                if data:
                    for attr in data:
                        cmds.connectAttr(data[attr], '%s.%s' % (node, attr),
                                         force=True)

    cmds.undoInfo(closeChunk=True)


def Blendshape():

    cmds.undoInfo(openChunk=True)

    sel = cmds.ls(selection=True)
    alembic = sel[0]
    target = sel[1]

    alembics = cmds.ls(alembic, dagObjects=True, long=True)
    targets = cmds.ls(target, dagObjects=True, long=True)
    for node in targets:
        for abc in alembics:
            if node.split(':')[-1] == abc.split('|')[-1]:
                blendshape = cmds.blendShape(abc, node)[0]
                cmds.setAttr('%s.%s' % (blendshape, abc.split('|')[-1]), 1)

    cmds.undoInfo(closeChunk=True)


def CopyAttrs():

    cmds.undoInfo(openChunk=True)

    sel = cmds.ls(selection=True)
    alembic = sel[0]
    target = sel[1]

    alembics = cmds.ls(alembic, dagObjects=True, transforms=True, long=True)
    targets = cmds.ls(target, dagObjects=True, transforms=True, long=True)
    for node in targets:
        for abc in alembics:
            if node.split(':')[-1] == abc.split('|')[-1]:
                t = cmds.xform(abc, q=True, ws=True, translation=True)
                r = cmds.xform(abc, q=True, ws=True, rotation=True)
                s = cmds.xform(abc, q=True, ws=True, scale=True)

                cmds.xform(node, ws=True, translation=t)
                cmds.xform(node, ws=True, rotation=r)
                cmds.xform(node, ws=True, scale=s)

    cmds.undoInfo(closeChunk=True)
