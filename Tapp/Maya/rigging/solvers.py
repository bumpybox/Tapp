import pymel.core as pc
import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.rigging.utils as mru
import Tapp.Maya.MG_Tools.python.rigging.script.MG_softIk as mmpsi

def ik(chain,namespace=''):
    
    #build rig---       
    #create root grp
    rootgrp=cmds.group(empty=True,name=namespace+'grp')
    
    #create plug object
    plug=cmds.spaceLocator(name=namespace+'plug')[0]
    
    if not hasattr(chain[0],'plug'):
        chain[0].plug={}
    
    chain[0].plug['ik']=plug
    
    #setup plug
    phgrp=cmds.group(empty=True,n=(plug+'_PH'))
    sngrp=cmds.group(empty=True,n=(plug+'_SN'))
    
    cmds.parent(sngrp,phgrp)
    cmds.parent(plug,sngrp)
    
    mru.Snap(None,phgrp,
             translation=chain[0].translation,
             rotation=chain[0].rotation)
    cmds.parent(phgrp,rootgrp)
    
    chain[0].meta.addPlug(plug,plugType='system')
    
    #finding upvector
    crs=mru.CrossProduct(chain[0].translation,
                         chain[1].translation,
                         chain[2].translation)
    
    #creating joints and sockets
    jnts=[]
    for node in chain:
        count=chain.index(node)
        
        prefix=namespace+node.name.split('|')[-1]+'_'
        
        #creating joint
        cmds.select(cl=True)
        jnt=cmds.joint(n=prefix+'jnt01')
        
        #setup joint
        mru.Snap(None,jnt, translation=node.translation, rotation=node.rotation)
        
        grp=cmds.group(empty=True)
        cmds.xform(grp,ws=True,translation=node.translation)
        
        if chain[count]!=chain[-1]:
            temp=cmds.group(empty=True)
            mru.Snap(None,temp,translation=chain[count+1].translation)
            
            cmds.delete(cmds.aimConstraint(temp,grp,worldUpType='vector',
                                           worldUpVector=crs))
        
            cmds.delete(temp)
        
        rot=cmds.xform(grp,query=True,rotation=True)
        cmds.rotate(rot[0],rot[1],rot[2],jnt,
                    worldSpace=True,pcp=True)
        
        cmds.makeIdentity(jnt,apply=True,t=1,r=1,s=1,n=0)
        
        cmds.delete(grp)
        
        if chain[count]!=chain[0]:
            cmds.parent(jnt,jnts[-1])
        
        if len(jnts)==0:
            cmds.parent(jnt,rootgrp)
        
        jnts.append(jnt)
        
        #create sockets
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(None,socket, translation=node.translation, rotation=node.rotation)
        cmds.parent(socket,jnt)
        
        if not hasattr(node,'socket'):
            node.socket={}
        node.socket['ik']=socket
    
    #plug parent
    cmds.parent(jnts[0],plug)
    
    #create ik
    startStretch=cmds.group(empty=True,n=namespace+'startStretch')
    endStretch=cmds.group(empty=True,n=namespace+'endStretch')
    
    mru.Snap(jnts[0],startStretch)
    mru.Snap(jnts[-1],endStretch)
    
    ikResult=mmpsi.MG_softIk(jnts,startMatrix=startStretch,endMatrix=endStretch,root=rootgrp)
    
    ikResult['ikHandle']=cmds.rename(ikResult['ikHandle'],namespace+'ikHandle')
    
    cmds.parent(startStretch,plug)
    
    #setup ik
    cmds.addAttr(plug,ln='ik_stretch',at='float',min=0,max=1,k=True)
    
    cmds.connectAttr(plug+'.ik_stretch',ikResult['softIk']+'.stretch')
    
    #build controls---
    
    for node in chain:
        
        count=chain.index(node)
        
        prefix=namespace+node.name+'_'
        
        #building root control, polevector and end control
        if 'IK_control' in node.controlData:
            
            #create control plug
            cntplug=cmds.spaceLocator(name=prefix+'plug')[0]
            
            chain[0].plug['ik_control']=cntplug
            
            #setup control plug
            mru.Snap(None,cntplug,
                     translation=node.translation,
                     rotation=node.rotation)
            
            phgrp=cmds.group(empty=True,n=(cntplug+'_PH'))
            sngrp=cmds.group(empty=True,n=(cntplug+'_SN'))
            
            mru.Snap(cntplug,phgrp)
            mru.Snap(cntplug,sngrp)
            
            cmds.parent(phgrp,plug)
            cmds.parent(sngrp,phgrp)
            cmds.parent(cntplug,sngrp)
            
            #creating control
            cnt=mru.Sphere(prefix+'cnt',size=node.scale[0])
            
            #setup control
            mru.Snap(None,cnt, translation=node.translation, rotation=node.rotation)
            
            if not hasattr(node,'control'):
                node.control={}
            node.control['ik']=cnt
            
            phgrp=cmds.group(empty=True,n=(cnt+'_PH'))
            sngrp=cmds.group(empty=True,n=(cnt+'_SN'))
            
            mru.Snap(cnt,phgrp)
            mru.Snap(cnt,sngrp)
            
            cmds.parent(phgrp,cntplug)
            cmds.parent(sngrp,phgrp)
            cmds.parent(cnt,sngrp)
            
            #adding cntplug and cnt to meta system
            node.meta.addPlug(cntplug,plugType='control')
            
            node.meta.addControl(cnt,controlSystem='ik')
            
            #root control
            if node==chain[0]:
                
                cmds.parent(jnts[0],cnt)
                cmds.parent(startStretch,cnt)
                
                cmds.parent(node.socket['ik'],cnt)
            
            #polevector control
            if node.children and node!=chain[0]:
                
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
            
            #end control
            if not node.children:
            
                cmds.pointConstraint(cnt,endStretch)
                
                cmds.orientConstraint(cnt,node.socket['ik'])

def fk(chain,namespace=''):
    
    #build rig---
    #create root grp
    rootgrp=cmds.group(empty=True,n=namespace+'grp')
    
    #failsafe
    if not hasattr(chain[0],'plug'):
        chain[0].plug={}
    
    #create plug object
    plug=cmds.spaceLocator(n=namespace+'plug')[0]
    
    #setup plug
    phgrp=cmds.group(empty=True,n=(plug+'_PH'))
    sngrp=cmds.group(empty=True,n=(plug+'_SN'))
    
    cmds.parent(sngrp,phgrp)
    cmds.parent(plug,sngrp)
    
    mru.Snap(None, phgrp, translation=chain[0].translation,
             rotation=chain[0].rotation)
    
    cmds.parent(phgrp,rootgrp)
    
    chain[0].meta.addPlug(plug,plugType='system')
    
    for node in chain:
        
        prefix=namespace+node.name.split('|')[-1]+'_'
        
        #create sockets
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(None,socket, translation=node.translation, rotation=node.rotation)
        
        if not hasattr(node,'socket'):
            node.socket={}
        node.socket['fk']=socket
        
        if node.parent:
            cmds.parent(socket,node.parent.socket['fk'])
        else:
            cmds.parent(socket,plug)
    
    #build controls---
    for node in chain:
        
        prefix=namespace+node.name.split('|')[-1]+'_'
        
        #create control
        if 'FK_control' in node.controlData:
            cnt=mru.Box(prefix+'cnt',size=node.scale[0])
            
            #setup control
            mru.Snap(None,cnt, translation=node.translation, rotation=node.rotation)
            
            if not hasattr(node,'control'):
                node.control={}
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
                cmds.parent(phgrp,plug)
            
            if node.meta:
                node.meta.addControl(cnt,controlSystem='fk')