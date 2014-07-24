import maya.cmds as cmds

cmds.loadPlugin('mtoa.mll', quiet=True)

import mtoa.core as core


def Subdivision(iterations=2):

    #find shape nodes of current selection
    nodeList = cmds.ls(selection=True, dag=True, lf=True, type='mesh')

    for node in nodeList:

        cmds.setAttr(node + '.aiSubdivType', 1)
        cmds.setAttr(node + '.aiSubdivIterations', iterations)


def MaskBuild():

    sel = cmds.ls(selection=True)

    aiMaskSets = []
    for node in sel:
        if cmds.nodeType(node) == 'objectSet':
            aiMaskSets.append(node)

    if not aiMaskSets:
        cmds.warning('No sets selected!')
        return

    core.createOptions()

    aiColor = cmds.shadingNode('aiUserDataColor', asShader=1)

    cmds.setAttr(aiColor + '.defaultValue', 1, 1, 1, typ='double3')

    for aiSet in xrange(0, len(aiMaskSets), 3):

        tSwitch = cmds.shadingNode('tripleShadingSwitch', au=1)
        cmds.setAttr(tSwitch + '.default', 0, 0, 0, typ='double3')

        aiUshader = cmds.shadingNode('aiUtility', asShader=1)
        cmds.setAttr(aiUshader + '.shadeMode', 2)
        cmds.connectAttr(tSwitch + '.output', aiUshader + '.color', f=1)

        for obj in cmds.listRelatives(cmds.sets(aiSet, q=1), pa=1):
            inpt = cmds.getAttr(tSwitch + '.input', s=1)
            if cmds.nodeType(obj) == 'mesh':
                cmds.connectAttr(obj + '.instObjGroups[0]',
                                 tSwitch + '.input[' + str(inpt) + '].inShape', f=1)
                cmds.connectAttr(aiColor + '.outColor',
                                 tSwitch + '.input[' + str(inpt) + '].inTriple', f=1)

        #AOV
        aovListSize = cmds.getAttr('defaultArnoldRenderOptions.aovList', s=1)

        customAOV = cmds.createNode('aiAOV',
                                    n='aiAOV_rgbMask',
                                    skipSelect=True)
        cmds.setAttr(customAOV + '.name', aiSet,
                     type='string')
        cmds.connectAttr(customAOV + '.message',
                         'defaultArnoldRenderOptions.aovList[' + str(aovListSize) + ']',
                         f=1)

        cmds.connectAttr('defaultArnoldDriver.message',
                         customAOV + '.outputs[0].driver', f=1)
        cmds.connectAttr('defaultArnoldFilter.message',
                         customAOV + '.outputs[0].filter', f=1)

        # connect to default shader
        cmds.connectAttr(aiUshader + '.outColor',
                         customAOV + '.defaultValue', f=1)


MaskBuild()

def MaskFlush():

    aovs = cmds.ls(type='aiAOV')
    nodes = []
    for aov in aovs:
        if 'rgbMask' in aov:
            nodes.append(aov)
            ut = cmds.listConnections(aov, type='aiUtility')
            if ut:
                nodes.extend(ut)
                ts = cmds.listConnections(ut, type='tripleShadingSwitch')
                if ts:
                    nodes.extend(ts)
                    audc = cmds.listConnections(ts, type='aiUserDataColor')
                    if audc:
                        nodes.extend(audc)

    if nodes:
        cmds.delete(nodes)


def Mask():

    sel = cmds.ls(selection=True)

    if sel:
        cmds.sets(name='aiMask1')

        MaskFlush()
        MaskBuild()
    else:
        cmds.warning('No nodes selected!')
