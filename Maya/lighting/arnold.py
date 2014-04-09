import maya.cmds as cmds

cmds.loadPlugin('mtoa.mll', quiet=True)


def Subdivision(iterations=2):

    #find shape nodes of current selection
    nodeList = cmds.ls(selection=True, dag=True, lf=True, type='mesh')

    for node in nodeList:

        cmds.setAttr(node + '.aiSubdivType', 1)
        cmds.setAttr(node + '.aiSubdivIterations', iterations)
