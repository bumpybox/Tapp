import maya.cmds as cmds


def latticeAdd():

    #undo enable
    cmds.undoInfo(openChunk=True)

    #getting nodes
    sel = cmds.ls(selection=True)
    lat = sel[-1]
    objs = sel[0:-1]

    if cmds.nodeType(cmds.listRelatives(lat, shapes=True)[0]) != 'lattice':
        cmds.warning('Last selected is NOT a lattice!')
        return

    #adding to lattice
    for obj in objs:
        try:
            cmds.lattice(lat, e=True, geometry=obj)
        except:
            pass

    cmds.undoInfo(closeChunk=True)


def latticeRemove():

    #undo enable
    cmds.undoInfo(openChunk=True)

    #getting nodes
    sel = cmds.ls(selection=True)
    if not sel:
        cmds.warning('No nodes selected!')
        return

    lat = sel[-1]
    objs = sel[0:-1]

    if cmds.nodeType(cmds.listRelatives(lat, shapes=True)[0]) != 'lattice':
        cmds.warning('Last selected is NOT a lattice!')
        return

    #removing from lattice
    for obj in objs:
        try:
            cmds.lattice(lat, e=True, remove=True, geometry=obj)

            #disconnecting shapes
            shapes = cmds.listRelatives(obj, shapes=True)
            for shp in shapes:
                source = cmds.listConnections(shp + '.inMesh', source=True)
                if cmds.nodeType(source) == 'ffd':
                    attr = cmds.listConnections(shp + '.inMesh', plugs=True)[0]
                    cmds.disconnectAttr(attr, shp + '.inMesh')
        except:
            pass

    cmds.undoInfo(closeChunk=True)
