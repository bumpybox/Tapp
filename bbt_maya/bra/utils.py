import maya.cmds as cmds
import maya.mel as mel
import os
from shutil import move
import sys

def distance( objA, objB ):
    from math import sqrt,pow
    
    At=cmds.xform(objA,ws=True,q=True,t=True)
    Ax=At[0]
    Ay=At[1]
    Az=At[2]
    
    Bt=cmds.xform(objB,ws=True,q=True,t=True)
    Bx=Bt[0]
    By=Bt[1]
    Bz=Bt[2]
 
    return sqrt(  pow(Ax-Bx,2) + pow(Ay-By,2) + pow(Az-Bz,2)  )

def proxyParent():
    #defining joints
    joints=list()
    for node in cmds.ls(type='network'):
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='joint' and (cmds.getAttr('%s.system' % node))=='skin':
            jnt=cmds.listConnections('%s.message' % node,type='transform')
            
            joints.append(jnt)
    
    collGRP=cmds.group(em=True,name='proxy_grp')
    
    #looping through proxy objects and parenting to joints
    for node in cmds.ls(type='network'):
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='proxy':
            proxy=cmds.listConnections('%s.message' % node,type='transform')
            
            proxyGRP=cmds.group(em=True,name=(str(proxy[0])+'_grp'))
            cmds.delete(cmds.parentConstraint(proxy,proxyGRP))
            
            dist=list()
            
            #joints loop
            for m in range(0,len(joints)):
                dist.append(distance(proxyGRP,joints[m]))
            
            jnt=joints[dist.index(min(dist))]
            
            cmds.delete(cmds.orientConstraint(jnt,proxyGRP))
            
            cmds.parent(proxy,proxyGRP)
            
            cmds.parentConstraint(jnt,proxyGRP,maintainOffset=True)
            cmds.scaleConstraint(jnt,proxyGRP)
            
            cmds.parent(proxyGRP,collGRP)

def sphereDist():
    #create nodes
    sph=cmds.polySphere(ch=True,name='spherePreview_geo')
    
    edgeGroup=cmds.group(empty=True,name='spherePreview_group')
    
    dist=cmds.createNode('distanceBetween')
    
    #setup group
    cmds.move(0,0,1,edgeGroup)
    
    #setup sphere
    cmds.connectAttr('%s.worldMatrix' % sph[0],'%s.inMatrix1' % dist)
    
    cmds.connectAttr('%s.worldMatrix' % edgeGroup,'%s.inMatrix2' % dist)
    
    cmds.connectAttr('%s.distance' % dist,'%s.radius' % sph[1])
    
    #create metaData
    meta=cmds.shadingNode('network',asUtility=True,name='meta_spherePreview')
    cmds.addAttr(meta,longName='type',dataType='string')
    cmds.setAttr('%s.type' % meta,'spherePreview',type='string')
    cmds.addAttr(meta,longName='createJoints',dataType='string')
    cmds.addAttr(meta,longName='sphere',attributeType='message')
    cmds.addAttr(meta,longName='group',attributeType='message')
    
    cmds.addAttr(sph[0],longName='metaParent',attributeType='message')
    cmds.addAttr(edgeGroup,longName='metaParent',attributeType='message')
    cmds.addAttr(dist,longName='metaParent',attributeType='message')
    
    cmds.connectAttr('%s.message' % meta,'%s.metaParent' % sph[0])
    cmds.connectAttr('%s.message' % meta,'%s.metaParent' % edgeGroup)
    cmds.connectAttr('%s.message' % meta,'%s.metaParent' % dist)
    cmds.connectAttr('%s.message' % sph[0],'%s.sphere' % meta)
    cmds.connectAttr('%s.message' % edgeGroup,'%s.group' % meta)
    
    #return
    return (sph[0],edgeGroup,meta)

def spherePreview():
    selCount=len(cmds.ls(sl=True))
    
    #zero selected
    if selCount==0:
        #create locator
        loc=cmds.spaceLocator(name='spherePreview_loc')[0]
        
        #create sphere
        nodes=sphereDist()
        
        #setup sphere
        cmds.pointConstraint(loc,nodes[1])
        
        #setup loc        
        cmds.move(0,0,1,loc)
        
        #attach metaData
        cmds.addAttr(loc,longName='metaParent',attributeType='message')
        
        cmds.connectAttr('%s.message' % nodes[2],'%s.metaParent' % loc)
        
        cmds.setAttr('%s.createJoints' % nodes[2],'true',type='string')
    
    #one item selected
    if selCount==1:
        #getting selection
        sel=cmds.ls(sl=True)[0]
        
        #create locator
        loc=cmds.spaceLocator(name='spherePreview_loc')[0]
        
        #create sphere
        nodes=sphereDist()
        
        #setup sphere
        cmds.pointConstraint(loc,nodes[1])
        
        cmds.delete(cmds.pointConstraint(sel,nodes[0]))
        
        #setup loc
        cmds.delete(cmds.pointConstraint(sel,loc))
        
        cmds.move(0,0,1,loc,relative=True)

        #attach metaData
        cmds.addAttr(loc,longName='metaParent',attributeType='message')
        
        cmds.connectAttr('%s.message' % nodes[2],'%s.metaParent' % loc)
        
        cmds.setAttr('%s.createJoints' % nodes[2],'true',type='string')

    #one item selected
    if selCount==2:
        #getting selection
        sel1=cmds.ls(sl=True)[0]
        
        sel2=cmds.ls(sl=True)[1]
        
        #create sphere
        nodes=sphereDist()
        
        #setup sphere
        cmds.pointConstraint(sel1,nodes[0])
        
        cmds.pointConstraint(sel2,nodes[1])
        
        #setup metaData
        cmds.setAttr('%s.createJoints' % nodes[2],'false',type='string')

def spherePreviewDelete():
    for node in (cmds.ls(type='network')):
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='spherePreview':
            if (cmds.getAttr('%s.createJoints' % node))=='true':
                #create joints
                cmds.select(cl=True)
                jnt1=cmds.joint()
                
                cmds.select(cl=True)
                jnt2=cmds.joint()
                
                #setup joints
                sph=cmds.listConnections('%s.sphere' % node,type='transform')
                cmds.delete(cmds.pointConstraint(sph,jnt1))
                
                grp=cmds.listConnections('%s.group' % node,type='transform')
                cmds.delete(cmds.pointConstraint(grp,jnt2))
                
                cmds.delete(cmds.aimConstraint(grp,jnt1))
                cmds.makeIdentity(jnt1,apply=True)
                
                cmds.delete(cmds.orientConstraint(jnt1,jnt2))
                cmds.makeIdentity(jnt2,apply=True)
                
                cmds.parent(jnt2,jnt1)
            
            for child in cmds.listConnections('%s.message' % node,type='transform'):
                cmds.delete(child)

''' NOT WORKING
def importWeightMapButton():
    fileNames=weightMapPath()
    
    if fileNames!=None:
        for f in fileNames:
            #correcting filename
            f=f.replace('\\','/')
            s
            #importing skin maps
            importWeightMap(f)

def weightMapPath():
    #getting file path and name
    basicFilter = "Weightmap (*.weightmap)"
    fileNames=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,fileMode=4,caption='Open Weightmaps')
    
    return fileNames

def importWeightMap(fileName):
    #reading weightmap
    f=open(fileName,'r')
    
    #getting data from file
    fData=f.read()
    
    fLines=fData.split('\n')
    
    del fLines[0]
    del fLines[0]
    
    newLines=list()
    for line in fLines:
        newLines.append(line.split('\r'))
    
    data=list()
    for line in newLines:
        data.append(line[0].split('\t'))
    
    del data[len(data)-1]
    
    geo=data[0][0]
    
    joints=list()
    for i in data:
        joints.append(i[1])
    
    #applying skin to geo
    cmds.select(geo)
    mel.eval('DeleteHistory;')
    cmds.skinCluster( joints, geo,)
    
    #importing weightmap
    cmds.select(geo)
    mel.eval('braImportSkin("'+fileName+'","weightmap");')

def exportWeightMapButton():
    #getting file path and name
    basicFilter = "Weightmap (*.weightmap)"
    fileName=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1, fileMode=0)
    
    #exporting skin maps
    if fileName!=None:
        mel.eval('exportSkinWeightMap("'+fileName[0]+'","weightmap");')
'''