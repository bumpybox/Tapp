from compiler.ast import flatten

import maya.cmds as cmds
import maya.mel as mel

def loadAlembic():
    
    cmds.loadPlugin('AbcExport.mll',quiet=True)
    cmds.loadPlugin('AbcImport.mll',quiet=True)

def exportAlembic():
    
    loadAlembic()
    
    #export alembic
    fileFilter = "Alembic Files (*.abc)"
    f=cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=1,fileMode=0)
    
    if f:
        #collecting export objects
        cmd=''
        for obj in cmds.ls(selection=True):
            cmd+=' -root '+obj
        
        #get time range
        start=cmds.playbackOptions(q=True,animationStartTime=True)
        end=cmds.playbackOptions(q=True,animationEndTime=True)
        
        alembic=mel.eval('AbcExport -j \"-frameRange %s %s -stripNamespaces -uvWrite -worldSpace %s -file %s";' % (start,end,cmd,f[0]))
        
        return alembic

def importAlembic():
    
    loadAlembic()
    
    #import alembic
    fileFilter = "Alembic Files (*.abc)"
    f=cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=1,fileMode=1)
    
    if f:
        alembic=mel.eval('AbcImport -mode import -fitTimeRange -setToStartFrame "%s";' % f[0])
    
    return alembic

def swapAlembic(alembic):
    #undo start
    cmds.undoInfo(openChunk=True)
    
    #getting connected attributes and nodes
    attrDict={}
    nodeList=[]
    for con in cmds.listConnections(alembic,skipConversionNodes=True,source=False,
                                    shapes=True,plugs=True):
        attr=con.split('.')[-1]
        node=con.split('.')[0]
        
        nodeList.append(node)
        
        attrDict.setdefault(node, []).append(attr)
    
    nodeList=list(set(nodeList))
    
    #getting scene nodes without the alembic nodes
    sceneNodes=[]
    sceneNodes.append(cmds.ls(transforms=True))
    sceneNodes.append(cmds.ls(shapes=True))
    sceneNodes=flatten(sceneNodes)
    sceneNodes=list(set(sceneNodes)-set(nodeList))
    
    #pairing scene nodes with alembic nodes
    pairingDict={}
    for node in nodeList:
        
        nameCompare=node
        
        if cmds.nodeType(node)=='mesh':
            if node.endswith('Deformed'):
                nameCompare=node.replace('Deformed','')
        
        for sceneNode in sceneNodes:
            
            if nameCompare==sceneNode.split(':')[-1]:
                pairingDict[node]=sceneNode
    
    #connecting scene nodes with alembic nodes, and deleting alembic nodes
    for node in pairingDict:
        target=pairingDict[node]
        
        for attr in attrDict[node]:
            sourceAttr=cmds.listConnections(node+'.'+attr,plugs=True)[0]
            
            cmds.connectAttr(sourceAttr,target+'.'+attr,force=True)
        
        #cmds.delete(node)
    
    #undo end
    cmds.undoInfo(closeChunk=True)