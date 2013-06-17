import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.rigging.utils as mru
reload(mru)
import MG_Tools.python.rigging.script.MG_softIk as mpsi
reload(mpsi)
import Tapp.Maya.rigging.meta as meta
reload(meta)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler=logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(funcName)s - LINE: %(lineno)d - %(message)s'))
log.addHandler(handler)

def ik_build(chainList):
    
    #build rig---
    #create root grp
    rootgrp=cmds.group(empty=True,name='ik_grp')
    
    cmds.parent(rootgrp,chainList[0].root['master'])
    
    #create root object
    root=cmds.spaceLocator(name='ik_root')[0]
    
    mru.Snap(None,root,
             translation=chainList[0].translation,
             rotation=chainList[0].rotation)
    cmds.parent(root,rootgrp)
    
    chainList[0].root['ik']=root
    
    #finding upvector
    crs=mru.CrossProduct(chainList[0].translation,
                         chainList[1].translation,
                         chainList[2].translation)
    
    #creating joints and sockets
    jnts=[]
    for node in chainList:
        count=chainList.index(node)
        
        prefix=node.name.split('|')[-1]+'_ik_'
        
        #creating joint
        cmds.select(cl=True)
        jnt=cmds.joint(n=prefix+'jnt01')
        
        #setup joint
        mru.Snap(None,jnt, translation=node.translation, rotation=node.rotation)
        
        grp=cmds.group(empty=True)
        cmds.xform(grp,ws=True,translation=node.translation)
        
        if chainList[count]!=chainList[-1]:
            temp=cmds.group(empty=True)
            mru.Snap(None,temp,translation=chainList[count+1].translation)
            
            cmds.delete(cmds.aimConstraint(temp,grp,worldUpType='vector',
                                           worldUpVector=crs))
        
            cmds.delete(temp)
        
        rot=cmds.xform(grp,query=True,rotation=True)
        cmds.rotate(rot[0],rot[1],rot[2],jnt,
                    worldSpace=True,pcp=True)
        
        cmds.makeIdentity(jnt,apply=True,t=1,r=1,s=1,n=0)
        
        cmds.delete(grp)
        
        if chainList[count]!=chainList[0]:
            cmds.parent(jnt,jnts[-1])
        
        if len(jnts)==0:
            cmds.parent(jnt,rootgrp)
        
        jnts.append(jnt)
        
        #create sockets
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(None,socket, translation=node.translation, rotation=node.rotation)
        cmds.parent(socket,jnt)
        node.socket['ik']=socket
    
    #root parent
    cmds.parent(jnts[0],root)
    
    #create ik
    startStretch=cmds.group(empty=True,n='startStretch')
    endStretch=cmds.group(empty=True,n='endStretch')
    
    mru.Snap(jnts[0],startStretch)
    mru.Snap(jnts[-1],endStretch)
    
    ikResult=mpsi.MG_softIk(jnts,startMatrix=startStretch,endMatrix=endStretch,root=rootgrp)
    
    ikResult['ikHandle']=cmds.rename(ikResult['ikHandle'],'ikHandle')
    
    cmds.parent(startStretch,root)
    
    #setup ik
    cmds.addAttr(node.root['master'],ln='ik_stretch',at='float',min=0,max=1)
    
    cmds.connectAttr(node.root['master']+'.ik_stretch',ikResult['softIk']+'.stretch')
    
    #build controls---
    for node in chainList:
        
        count=chainList.index(node)
        
        prefix=node.name.split('|')[-1]+'_ik_'
        
        #building polevector and end control
        if 'IK_control' in node.data:
            cnt=mru.Sphere(prefix+'cnt',size=node.scale[0])
        
            #setup control
            mru.Snap(None,cnt, translation=node.translation, rotation=node.rotation)
            node.control['ik']=cnt
            
            phgrp=cmds.group(empty=True,n=(cnt+'_PH'))
            sngrp=cmds.group(empty=True,n=(cnt+'_SN'))
            
            mru.Snap(cnt,phgrp)
            mru.Snap(cnt,sngrp)
            
            cmds.parent(cnt,sngrp)
            cmds.parent(sngrp,phgrp)
            
            
            node.system.addControl(cnt,'ik')
            
            #root control
            if node==chainList[0]:
                
                cmds.parent(jnts[0],cnt)
                cmds.parent(startStretch,cnt)
                
                cmds.parent(node.socket['ik'],cnt)
                
                cmds.parent(phgrp,rootgrp)
            
            #polevector control
            if node.children and node!=chainList[0]:
                
                mru.Snap(jnts[count],phgrp)
                
                dist=0
                for jntCount in range(0,len(jnts)-1):
                    dist+=mru.Distance(jnts[jntCount], jnts[jntCount+1])
                
                cmds.move(-dist/len(jnts)/2,0,-dist/len(jnts),phgrp,r=True,os=True,wd=True)
                
                mru.Snap(None,phgrp, rotation=node.rotation)
                
                curve=cmds.curve(d=1,p=[(0,0,0),(0,0,0)])
                polevectorSHP=cmds.listRelatives(curve,s=True)[0]
                cmds.setAttr(polevectorSHP+'.overrideEnabled',1)
                cmds.setAttr(polevectorSHP+'.overrideDisplayType',2)
                
                cmds.select(curve+'.cv[0]',r=True)
                cluster=mel.eval('newCluster " -envelope 1";')
                
                mru.Snap(cnt,cluster[1])
                cmds.parent(cluster[1],cnt)
                
                cmds.rename(cluster[0],prefix+'polvector_cls')
                
                cmds.select(curve+'.cv[1]',r=True)
                cluster=mel.eval('newCluster " -envelope 1";')
                
                mru.Snap(jnts[count],cluster[1])
                cmds.parent(cluster[1],jnts[count])
                
                cmds.rename(cluster[0],prefix+'polvector_cls')
                polevectorSHP=cmds.rename(curve,prefix+'polevector_shp')
                
                cmds.poleVectorConstraint(cnt,ikResult['ikHandle'])
                
                cmds.parent(polevectorSHP,rootgrp)
                cmds.parent(phgrp,rootgrp)
            
            #end control
            if not node.children:
            
                cmds.pointConstraint(cnt,endStretch)
                cmds.parent(node.socket['ik'],cnt)
                
                cmds.parent(phgrp,rootgrp)

def fk_build(chainList):
    
    #build rig---
    #create root grp
    rootgrp=cmds.group(empty=True,name='fk_grp')
    
    cmds.parent(rootgrp,chainList[0].root['master'])
    
    #create root object
    root=cmds.spaceLocator(name='fk_root')[0]
    
    mru.Snap(None,root,
             translation=chainList[0].translation,
             rotation=chainList[0].rotation)
    cmds.parent(root,rootgrp)
    
    chainList[0].root['fk']=root
    
    for node in chainList:
        
        prefix=node.name.split('|')[-1]+'_fk_'
        
        #create sockets
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(None,socket, translation=node.translation, rotation=node.rotation)
        node.socket['fk']=socket
        
        if node.parent:
            cmds.parent(socket,node.parent.socket['fk'])
        else:
            cmds.parent(socket,root)
    
    #build controls---
    for node in chainList:
        
        prefix=node.name.split('|')[-1]+'_fk_'
        
        #create control
        if 'FK_control' in node.data:
            cnt=mru.Box(prefix+'cnt',size=node.scale[0])
            
            #setup control
            mru.Snap(None,cnt, translation=node.translation, rotation=node.rotation)
            node.control['fk']=cnt
            
            cmds.parent(node.socket['fk'],cnt)
            
            phgrp=cmds.group(empty=True,n=(cnt+'_PH'))
            sngrp=cmds.group(empty=True,n=(cnt+'_SN'))
            
            mru.Snap(cnt,phgrp)
            mru.Snap(cnt,sngrp)
            
            cmds.parent(cnt,sngrp)
            cmds.parent(sngrp,phgrp)
            
            if node.parent:
                cmds.parent(phgrp,node.parent.socket['fk'])
            else:
                cmds.parent(phgrp,root)
            
            node.system.addControl(cnt,'fk')

def guide_build(node):
    
    #build controls---
    cnt=mru.implicitSphere(node.name)
        
    node.guide=cnt
    
    mru.Snap(None, cnt, translation=node.translation, rotation=node.rotation)
    
    #adding data
    for data in node.data:
        
        mNode=meta.r9Meta.MetaClass(cnt)
        mNode.addAttr(data,node.data[data])
    
    #parenting
    if node.parent:
        cmds.parent(cnt,node.parent.guide)
    
    #traversing down the node tree
    if node.children:
        for child in node.children:
            guide_build(child)

def joints_build(node):
    
    #build rig---
    
    #creating joint
    cmds.select(cl=True)
    jnt=cmds.joint(n=node.name)
    
    node.joint['blend']=jnt
    
    #setup joint
    mru.Snap(None,jnt, translation=node.translation, rotation=node.rotation)
    
    #parent and children
    if node.parent:
        cmds.parent(jnt,node.parent.joint['blend'])
    else:
        #create root grp
        rootgrp=cmds.group(empty=True,name='joints_grp')
        
        if node.root['master']:
            cmds.parent(rootgrp,node.root['master'])
        
        cmds.parent(jnt,rootgrp)
    
    if node.children:
        for child in node.children:
            joints_build(child)