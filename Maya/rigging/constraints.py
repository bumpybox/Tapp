import maya.cmds as cmds
import json


def GetData(nodeFilter='joint'):
    sel = cmds.ls(selection=True, type=nodeFilter)
    dataExport = []
    transforms = ['tx', 'ty', 'tz',
                  'rx', 'ry', 'rz',
                  'sx', 'sy', 'sz']
    for node in sel:
        data = {}
        data['name'] = node
        constraints = []
        for attr in transforms:
            conn = cmds.listConnections('%s.%s' % (node, attr))
            if conn:
                conn = conn[0]
                connType = cmds.nodeType(conn)
                if 'Constraint' in connType:
                    constraints.append(conn)
                    data[conn] = {}
                    data[conn]['type'] = connType

        for con in set(constraints):
            targets = cmds.listConnections(con + '.target')
            data[con]['targets'] = list(set(targets) - set([con]))
        dataExport.append(data)

    return dataExport


def ExportData():
    data = GetData()
    multipleFilters = "JSON Files (*.json)"
    f = cmds.fileDialog2(fileMode=0, fileFilter=multipleFilters)
    if f:
        f = open(f[0], 'w')
        json.dump(data, f)
        f.close()


def ImportData(f=None):
    multipleFilters = "JSON Files (*.json)"
    if not f:
        f = cmds.fileDialog2(fileMode=1, fileFilter=multipleFilters)
    if f:
        if isinstance(f, list):
            f = f[0]
        f = open(f, 'r')
        data = json.load(f)
        SetData(data)
    else:
        return None


def SetData(data):

    cmds.undoInfo(openChunk=True)

    for node in data:
        for key in node:
            if not key == 'name':
                targets = node[key]['targets']
                if node[key]['type'] == 'parentConstraint':
                    cmds.parentConstraint(targets, node['name'],
                                          maintainOffset=True)
                if node[key]['type'] == 'orientConstraint':
                    cmds.orientConstraint(targets, node['name'],
                                          maintainOffset=True)
                if node[key]['type'] == 'pointConstraint':
                    cmds.pointConstraint(targets, node['name'],
                                         maintainOffset=True)
                if node[key]['type'] == 'scaleConstraint':
                    cmds.scaleConstraint(targets, node['name'],
                                         maintainOffset=True)

    cmds.undoInfo(closeChunk=True)


def Delete():

    cmds.undoInfo(openChunk=True)

    sel = cmds.ls(selection=True, dagObjects=True)
    for node in sel:
        if 'Constraint' in cmds.nodeType(node):
            cmds.delete(node)

    cmds.undoInfo(closeChunk=True)
