import maya.cmds as cmds

cmds.loadPlugin('mtoa.mll',quiet=True)

def addSubdivision():
    
    nodeList = cmds.ls(selection = True, dag=True, lf=True, type = 'mesh') # find shape nodes of current selection
    for node in nodeList:
        
        cmds.setAttr(node+'.aiSubdivType',1)
        cmds.setAttr(node+'.aiSubdivIterations',2)