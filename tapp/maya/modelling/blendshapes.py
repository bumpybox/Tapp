import maya.cmds as cmds
import maya.mel as mel


def mirrorBlendshape(targets=[],original=''):

    #getting nodes
    sel = cmds.ls(selection=True)
    if len(sel) == 1:
        cmds.warning('Select all blendshapes first, then the original mesh last!')
        return
    if not targets:
        targets = sel[0:-1]
    if not original:
        original = sel[-1]

    #mirroring blendshape
    mirror = cmds.duplicate(original)[0]
    bldShp = cmds.blendShape(targets, mirror)[0]
    try:
        cmds.setAttr(mirror + '.sx', lock=False)
    except:
        pass
    cmds.setAttr(mirror + '.sx', -1)

    mirrorTrg = cmds.duplicate(original)[0]
    cmds.select(mirrorTrg, mirror)
    mel.eval('CreateWrap;')

    mirrorTrgs = []
    for trg in targets:
        cmds.setAttr('%s.%s' % (bldShp, trg), 1)
        temp = cmds.duplicate(mirrorTrg)[0]
        temp = cmds.rename(temp, trg + '_mirror')
        mirrorTrgs.append(temp)
        cmds.setAttr('%s.%s' % (bldShp, trg), 0)

    cmds.delete(mirror)
    cmds.delete(mirrorTrg)

    return mirrorTrgs


def symmetry():

    #getting nodes
    sel = cmds.ls(selection=True)
    if len(sel) == 1:
        cmds.warning('Select the edited mesh first, then the original mesh last!')
        return
    if len(sel) > 2:
        cmds.warning('Select the edited mesh first, then the original mesh last!')
        return

    edit = sel[0]
    original = sel[1]

    #creating symmetry mesh
    mirror = mirrorBlendshape([edit], original)[0]
    copy = cmds.duplicate(original)[0]
    bldShp = cmds.blendShape(edit, mirror, copy)[0]
    cmds.setAttr('%s.%s' % (bldShp, edit), 1)
    cmds.setAttr('%s.%s' % (bldShp, mirror), 1)
    symmetry = cmds.duplicate(copy)[0]
    symmetry = cmds.rename(symmetry, edit + '_symmetry')

    cmds.delete(copy, mirror)

    return symmetry
