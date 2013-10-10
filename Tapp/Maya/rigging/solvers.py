import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.rigging.utils as mru
import Tapp.Maya.MG_Tools.python.rigging.script.MG_softIk as mmpsi
import Tapp.Maya.utils.ZvParentMaster as muz
import Tapp.Maya.rigging.meta as meta

def system(point,parent=None):
    if parent:
        metaNode=parent.addPoint(name=point.name)
    else:
        metaNode=meta.MetaPoint(name=point.name)
    
    metaNode.rename('meta_'+point.name)
    
    point.meta=metaNode
    
    metaNode.solverData=point.solverData
    metaNode.controlData=point.controlData
    
    if point.children:
        for child in point.children:
            system(child,parent=metaNode)

def replaceParent(point):
    
    if point.parentData:
        
        print 'name:'
        print point.name
        
        parent=meta.r9Meta.getMetaNodes(mTypes=['MetaPoint'],
                                        mAttrs=['mNodeID=%s' % point.parentData.name])[0]
        
        point.meta.parentData=parent.mNode
    
    if point.children:
        for child in point.children:
            replaceParent(child)

def parent(point):
    
    #if a static parent is specified
    if point.parentData:
        
        #setup ik static parenting
        if 'IK' in point.control:
            cmds.select(point.control['IK'],point.parentData.socket['blend'])
            muz.attach()
        
        #front of chain
        if not point.parent:
            for plug in point.plug:
                cmds.select(point.plug[plug],point.parentData.socket['blend'])
                muz.attach()
    
    #continuing to children
    if point.children:
        for child in point.children:
            parent(child)

def blend(points,namespace=''):
    
    #create extra control
    control=mru.Pin(namespace+'cnt')
    
    #building blends
    rootgrp=cmds.group(empty=True,name=namespace+'grp')
    
    def _build(node):
        
        prefix=namespace+node.name.split('|')[-1]+'_'
        
        #create socket
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(None, socket,translation=node.translation,rotation=node.rotation)
        
        cmds.parent(socket,rootgrp)
        
        node.meta.addSocket(socket)
        
        for s in node.socket:
            
            con=cmds.parentConstraint(node.socket[s],socket)[0]
            
            #ensuring extra control has the attribute
            if not cmds.objExists(control+'.'+s):
                
                cmds.addAttr(control,ln=s,at='float',min=0,max=1,k=True)
            
            #only connecting extra controller if there are more than one system present
            if len(node.socket)>1:
                
                #connecting extra to target weights - using string search, which probably needs improvement ---
                targets=cmds.parentConstraint(con,q=True,weightAliasList=True)
                
                for target in targets:
                    
                    if node.socket[s] in target:
                        
                        cmds.connectAttr(control+'.'+s,con+'.'+target)
            
            #parenting up the points
            if node.parent:
                
                #making sure the points has ended
                if s not in node.parent.socket:
                    
                    cmds.select(node.plug[s],node.parent.socket['blend'])
                    muz.attach()
        
        node.socket['blend']=socket
        
        if node.children:
            for child in node.children:
                _build(child)
    
    _build(points[0])
    
    #setup extra control
    mru.Snap(None,control,translation=points[0].translation,rotation=points[0].rotation)
    
    cmds.parent(control,points[0].socket['blend'])
    
    attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
    mru.ChannelboxClean(control, attrs)
    
    points[0].meta.addControl(control,'extra')
    
    def switch(node):
            
        for system in node.control:
            
            mNode=meta.r9Meta.MetaClass(node.control[system])
            mNode=mNode.getParentMetaNode()
            
            sockets=[]
            for s in node.socket:
                if s!=system and s!='blend':
                    
                    sockets.append(node.socket[s])
            
            mNode.connectChildren(sockets,'switch')

        if node.children:
            for child in node.children:
                switch(child)
    
    switch(points[0])
    
    if len(points)==1:
        cmds.delete(control)

def IK(points,namespace=''):
    
    #build rig---       
    #create root grp
    rootgrp=cmds.group(empty=True,name=namespace+'grp')
    
    #create plug object
    plug=cmds.spaceLocator(name=namespace+'plug')[0]
    
    if not hasattr(points[0],'plug'):
        points[0].plug={}
    
    points[0].plug['IK']=plug
    
    #setup plug
    phgrp=cmds.group(empty=True,n=(plug+'_PH'))
    sngrp=cmds.group(empty=True,n=(plug+'_SN'))
    
    cmds.parent(sngrp,phgrp)
    cmds.parent(plug,sngrp)
    
    mru.Snap(None,phgrp,
             translation=points[0].translation,
             rotation=points[0].rotation)
    cmds.parent(phgrp,rootgrp)
    
    points[0].meta.addPlug(plug,plugType='system')
    
    #finding upvector
    crs=mru.CrossProduct(points[0].translation,
                         points[1].translation,
                         points[2].translation)
    
    #creating joints and sockets
    jnts=[]
    for node in points:
        count=points.index(node)
        
        prefix=namespace+node.name.split('|')[-1]+'_'
        
        #creating joint
        cmds.select(cl=True)
        jnt=cmds.joint(n=prefix+'jnt01')
        
        #setup joint
        mru.Snap(None,jnt, translation=node.translation, rotation=node.rotation)
        
        grp=cmds.group(empty=True)
        cmds.xform(grp,ws=True,translation=node.translation)
        
        if points[count]!=points[-1]:
            temp=cmds.group(empty=True)
            mru.Snap(None,temp,translation=points[count+1].translation)
            
            cmds.delete(cmds.aimConstraint(temp,grp,worldUpType='vector',
                                           worldUpVector=crs))
        
            cmds.delete(temp)
        
        rot=cmds.xform(grp,query=True,rotation=True)
        cmds.rotate(rot[0],rot[1],rot[2],jnt,
                    worldSpace=True,pcp=True)
        
        cmds.makeIdentity(jnt,apply=True,t=1,r=1,s=1,n=0)
        
        cmds.delete(grp)
        
        if points[count]!=points[0]:
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
        node.socket['IK']=socket
    
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
    
    for node in points:
        
        count=points.index(node)
        
        prefix=namespace+node.name+'_'
        
        #building root control, polevector and end control
        if 'IK' in node.controlData:
            
            #create control plug
            cntplug=cmds.spaceLocator(name=prefix+'plug')[0]
            
            points[0].plug['IK_control']=cntplug
            
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
            cnt=mru.icon(iconType=node.controlData['IK'],name=prefix+'cnt',size=node.scale[0])
            
            #setup control
            mru.Snap(None,cnt, translation=node.translation, rotation=node.rotation)
            
            if not hasattr(node,'control'):
                node.control={}
            node.control['IK']=cnt
            
            phgrp=cmds.group(empty=True,n=(cnt+'_PH'))
            sngrp=cmds.group(empty=True,n=(cnt+'_SN'))
            
            mru.Snap(cnt,phgrp)
            mru.Snap(cnt,sngrp)
            
            cmds.parent(phgrp,cntplug)
            cmds.parent(sngrp,phgrp)
            cmds.parent(cnt,sngrp)
            
            #adding cntplug and cnt to meta system
            node.meta.addPlug(cntplug,plugType='control')
            
            node.meta.addControl(cnt,controlSystem='IK',icon=node.controlData['IK'])
            
            #root control
            if node==points[0]:
                
                cmds.parent(jnts[0],cnt)
                cmds.parent(startStretch,cnt)
                
                cmds.parent(node.socket['IK'],cnt)
            
            #polevector control
            if node.children and node!=points[0]:
                
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
                
                cmds.orientConstraint(cnt,node.socket['IK'])

def FK(points,namespace=''):
    
    #build rig---
    #create root grp
    rootgrp=cmds.group(empty=True,n=namespace+'grp')
    
    #create plug object
    plug=cmds.spaceLocator(n=namespace+'plug')[0]
    
    if not hasattr(points[0],'plug'):
        points[0].plug={}
    
    points[0].plug['FK']=plug
    
    #setup plug
    phgrp=cmds.group(empty=True,n=(plug+'_PH'))
    sngrp=cmds.group(empty=True,n=(plug+'_SN'))
    
    cmds.parent(sngrp,phgrp)
    cmds.parent(plug,sngrp)
    
    mru.Snap(None, phgrp, translation=points[0].translation,
             rotation=points[0].rotation)
    
    cmds.parent(phgrp,rootgrp)
    
    points[0].meta.addPlug(plug,plugType='system')
    
    for node in points:
        
        prefix=namespace+node.name.split('|')[-1]+'_'
        
        #create sockets
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(None,socket, translation=node.translation, rotation=node.rotation)
        
        if not hasattr(node,'socket'):
            node.socket={}
        node.socket['FK']=socket
        
        if node.parent:
            cmds.parent(socket,node.parent.socket['FK'])
        else:
            cmds.parent(socket,plug)
    
    #build controls---
    for node in points:
        
        prefix=namespace+node.name.split('|')[-1]+'_'
        
        #create control
        if 'FK' in node.controlData:
            cnt=mru.icon(iconType=node.controlData['FK'],name=prefix+'cnt',size=node.scale[0])
            
            #setup control
            mru.Snap(None,cnt, translation=node.translation, rotation=node.rotation)
            
            if not hasattr(node,'control'):
                node.control={}
            node.control['FK']=cnt
            
            cmds.parent(node.socket['FK'],cnt)
            
            phgrp=cmds.group(empty=True,n=(cnt+'_PH'))
            sngrp=cmds.group(empty=True,n=(cnt+'_SN'))
            
            mru.Snap(cnt,phgrp)
            mru.Snap(cnt,sngrp)
            
            cmds.parent(cnt,sngrp)
            cmds.parent(sngrp,phgrp)
            
            if node.parent:
                cmds.parent(phgrp,node.parent.socket['FK'])
            else:
                cmds.parent(phgrp,plug)
            
            if node.meta:
                node.meta.addControl(cnt,controlSystem='FK',icon=node.controlData['FK'])