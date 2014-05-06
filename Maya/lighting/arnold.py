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

    allSets = cmds.ls(set=1)
    aiMasksSets = []

    for s in allSets:
        if s[0:6] == 'aiMask':
            aiMasksSets.append(s)

    if aiMasksSets == []:
        return cmds.warning('No aiMask sets!')

    core.createOptions()

    aiColors = [
    cmds.shadingNode('aiUserDataColor', asShader=1),
    cmds.shadingNode('aiUserDataColor', asShader=1),
    cmds.shadingNode('aiUserDataColor', asShader=1)
    ]

    cmds.setAttr(aiColors[0] + '.defaultValue', 1, 0, 0, typ='double3')
    cmds.setAttr(aiColors[1] + '.defaultValue', 0, 1, 0, typ='double3')
    cmds.setAttr(aiColors[2] + '.defaultValue', 0, 0, 1, typ='double3')

    for aiSet in xrange(0, len(aiMasksSets), 3):

        tSwitch = cmds.shadingNode('tripleShadingSwitch', au=1)
        cmds.setAttr(tSwitch + '.default', 0, 0, 0, typ='double3')

        aiUshader = cmds.shadingNode('aiUtility', asShader=1)
        cmds.setAttr(aiUshader + '.shadeMode', 2)
        cmds.connectAttr(tSwitch + '.output', aiUshader + '.color', f=1)

        for n, i in enumerate(aiMasksSets[aiSet:aiSet + 3]):
            aiColor = aiColors[n % len(aiColors)]

            for obj in cmds.listRelatives(cmds.sets(i, q=1), pa=1):
                inpt = cmds.getAttr(tSwitch + '.input', s=1)
                if cmds.nodeType(obj) == 'mesh':
                    cmds.connectAttr(obj + '.instObjGroups[0]',
                                     tSwitch + '.input[' + str(inpt) + '].inShape', f=1)
                    cmds.connectAttr(aiColor + '.outColor',
                                     tSwitch + '.input[' + str(inpt) + '].inTriple', f=1)

        # AOV'S

        aovListSize = cmds.getAttr('defaultArnoldRenderOptions.aovList', s=1)

        customAOV = cmds.createNode('aiAOV',
                                    n='aiAOV_rgbMask' + str(aiSet // 3 + 1),
                                    skipSelect=True)
        cmds.setAttr(customAOV + '.name', 'rgbMask' + str(aiSet // 3 + 1),
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
