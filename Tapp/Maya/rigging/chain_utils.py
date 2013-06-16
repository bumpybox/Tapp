import logging
import inspect

import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.rigging.utils as mru
reload(mru)
import MG_Tools.python.rigging.script.MG_softIk as mpsi
reload(mpsi)
import Tapp.Maya.rigging.meta as meta
reload(meta)

def buildChain(obj):
    
    def chainFromSystem(obj,parent=None):
        
        node=meta.chain(obj)
        
        node.name=obj.data['name']
        
        data=obj.data
        del(data['name'])
        node.data=data
        
        #transforms
        node.translation=cmds.xform(obj.node,q=True,ws=True,translation=True)
        node.rotation=cmds.xform(obj.node,q=True,ws=True,rotation=True)
        node.scale=cmds.xform(obj.node,q=True,relative=True,scale=True)
        
        
        #parent and children
        node.parent=parent
        
        if obj.hasAttr('guideChildren'):
            for child in obj.guideChildren:
                node.addChild(chainFromSystem(child,parent=node))
            
            return node
        else:
            return node
    
    def chainFromGuide(obj,parent=None):
        
        node=meta.chain(obj)
        
        #getting name
        node.name=obj.split('|')[-1]
        
        #getting attr data
        data={}
        for attr in cmds.listAttr(obj,userDefined=True):
            data[attr]=cmds.getAttr(obj+'.'+attr)
        node.data=data
        
        #transforms
        node.translation=cmds.xform(obj,q=True,ws=True,translation=True)
        node.rotation=cmds.xform(obj,q=True,ws=True,rotation=True)
        node.scale=cmds.xform(obj,q=True,relative=True,scale=True)
        
        #parent and children
        node.parent=parent
        
        children=cmds.listRelatives(obj,children=True,fullPath=True,type='transform')
        
        if children:
            for child in children:
                node.addChild(chainFromGuide(child,parent=node))
            
            return node
        else:
            return node
    
    check=meta.r9Meta.MetaClass(obj)
    
    #build from guide---
    if check.__class__.__name__=='MetaClass':
        
        chain=chainFromGuide(obj)
        chain.addRoot(obj,'master')
        
        return chain
        
    #build from system---
    if check.__class__.__name__=='TappSystem':
        
        obj=meta.r9Meta.MetaClass(obj)
        
        for socket in obj.getChildMetaNodes(mAttrs='mClass=TappSocket'):
            if not socket.hasAttr('guideParent'):
                
                chain=chainFromSystem(socket)
                chain.addRoot(obj.root,'master')
                chain.addSystem(obj)
                
                return chain

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
    ikStart=cmds.group(empty=True,n='startStretch')
    ikEnd=cmds.group(empty=True,n='endStretch')
    
    mru.Snap(jnts[0],ikStart)
    mru.Snap(jnts[-1],ikEnd)
    
    ikResult=mpsi.MG_softIk(jnts,startMatrix=ikStart,endMatrix=ikEnd,root=rootgrp)
    
    ikResult['ikHandle']=cmds.rename(ikResult['ikHandle'],'ikHandle')
    
    cmds.parent(ikStart,root)
    
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
            
            if node.children:
                
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
            else:
                
                cmds.pointConstraint(cnt,ikEnd)
                cmds.parent(node.socket['ik'],cnt)
                
                cmds.parent(phgrp,rootgrp)

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
        
        cmds.parent(rootgrp,node.root['master'])
        
        cmds.parent(jnt,rootgrp)
    
    if node.children:
        for child in node.children:
            joints_build(child)

class solver():
    
    def __init__(self,chain):
        
        self.log= logging.getLogger( "%s.%s" % ( self.__module__, self.__class__.__name__))
        
        self.chain=chain
        self.fk_chains=[]
        self.ik_chains=[]
        self.spline_chains=[]
        
        #finding chains (WORKAROUND! the results from breakdown seems to accumulate by each call)
        startAttr=['FK_solver_start','FK_control']
        endAttr=['FK_solver_end']
        self.fk_chains=self.chain.breakdown(startAttr,endAttr,result=[])
        
        startAttr=['IK_solver_start','IK_control']
        endAttr=['IK_solver_end']
        self.ik_chains=self.chain.breakdown(startAttr,endAttr,result=[])
        
        startAttr=['Spline_solver_start','Spline_control']
        endAttr=['Spline_solver_end']
        self.spline_chains=self.chain.breakdown(startAttr,endAttr,result=[])
    
    def __repr__(self):
        
        result=''
        
        for c in self.fk_chains:
            result+='fk chain from:\n'
            for node in c:
                result+=node.name+'\n'
        
        for c in self.ik_chains:
            result+='ik chain from:\n'
            for node in c:
                result+=node.name+'\n'
        
        for c in self.spline_chains:
            result+='spline chain from:\n'
            for node in c:
                result+=node.name+'\n'
        
        return result
    
    def blend(self,node,control):
        
        prefix=node.name.split('|')[-1]+'_bld_'
        
        #create socket
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(None, socket,translation=node.translation,rotation=node.rotation)
        
        data=node.data
        data['name']=node.name
        metaNode=node.system.addSocket(socket,boundData={'data':data})
        if node.parent:
            metaParent=meta.r9Meta.MetaClass(node.parent.socket['blend'])
            metaParent=metaParent.getParentMetaNode()
            
            metaParent.connectChildren([metaNode],'guideChildren', srcAttr='guideParent')
        
        cmd='cmds.parentConstraint('
        for s in node.socket:
            cmd+='\''+node.socket[s]+'\','
        cmd+='\''+socket+'\')'
        con=eval(cmd)[0]
        
        for s in node.socket:
            attr=control+'.'+s
            if not cmds.objExists(attr):
                cmds.addAttr(control,ln=s,at='float',keyable=True,
                             min=0,max=1)
        
            for count in range(0,len(node.socket)):
                target=cmds.listConnections(con+'.target[%s].targetParentMatrix' % count)
                if target[0]==node.socket[s]:
                    cmds.connectAttr(control+'.'+s,con+'.'+
                                     node.socket[s]+'W%s' % count,force=True)
        
        node.socket['blend']=socket
        
        cmds.parent(socket,node.root['master'])
        
        if node.children:
            for child in node.children:
                self.blend(child,control)
    
    def switch(self,node):
        
        if len(node.control)>1:
            for control in node.control:
                
                mNode=meta.r9Meta.MetaClass(node.control[control])
                mNode=mNode.getParentMetaNode()
                
                otherControls=[]
                for c in node.control:
                    if c!=control:
                        
                        otherControl=meta.r9Meta.MetaClass(node.control[c])
                        otherControl=otherControl.getParentMetaNode()
                        otherControls.append(otherControl)
                
                mNode.connectChildren(otherControls,'switch')
        
        if node.children:
            for child in node.children:
                self.switch(child)
    
    def rootParent(self,node):
        
        for key in node.root:
            if key!='master':
                if node.parent:
                    cmds.parentConstraint(node.parent.socket['blend'],node.root[key],maintainOffset=True)
        
        if node.children:
            for child in node.children:
                self.rootParent(child)
    
    def build(self,methods=['fk','ik','joints','spline'],blend=False,deleteSource=True):
        
        #checking input type
        if not isinstance(methods,list):
            self.log.error('build: methods is a not a list!')
            return
        
        #delete source
        if deleteSource:
            
            if self.chain.root:
                cmds.delete(self.chain.root['master'])
            
            if self.chain.system:
                for control in self.chain.system.getChildren(cAttrs='controls'):
                    meta.r9Meta.MetaClass(control).delete()
                    
                for socket in self.chain.system.getChildren(cAttrs='sockets'):
                    meta.r9Meta.MetaClass(socket).delete()
                
                self.chain.system.delete()
        
        #adding root and system
        if len(methods)>1:
            #rig asset
            #asset=cmds.container(n='rig',type='dagContainer')
            asset=cmds.group(empty=True,n='rig')
            attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
            mru.ChannelboxClean(asset, attrs)
            
            self.chain.addRoot(asset,'master')
            
            #meta rig
            system=meta.TappSystem()
            
            system.root=asset
            
            self.chain.addSystem(system)
        
        #build methods
        for method in methods:
            if method=='fk':
                for c in self.fk_chains:
                    fk_build(c)
            
            if method=='ik':
                for c in self.ik_chains:
                    ik_build(c)
            
            if method=='joints':
                joints_build(self.chain)
            
            if method=='guide':
                guide_build(self.chain)
        
        #blending
        if blend and len(methods)>1:
            
            #create extra control
            cnt=mru.Pin('extra_cnt')
            
            #create blend sockets
            self.blend(self.chain,cnt)
            
            #setup extra control
            mru.Snap(None,cnt,translation=self.chain.translation,rotation=self.chain.rotation)
            
            cmds.parent(cnt,self.chain.socket['blend'])
            cmds.rotate(0,90,0,cnt,r=True,os=True)
            
            if cmds.objExists(asset+'.ik_stretch'):
                cmds.addAttr(cnt,ln='ik_stretch',at='float',k=True,
                             min=0,max=1)
                
                cmds.connectAttr(cnt+'.ik_stretch',asset+'.ik_stretch')
            
            system.addControl(cnt,'extra')
            
            #parenting roots
            self.rootParent(self.chain)
        
        #switching
        self.switch(self.chain)

#build system
chain=buildChain('|clavicle')
solver(chain).build()

#rebuild system
#chain=buildChain('TappSystem')
#solver(chain).build(method='all',blend=True)

'''
build joints
build spline
possibly need to not have one attr for activting systems, and go to each socket and active the system if its present
need to find/build a better logging system, 
hook up controls visibility to blend control
'''

def switch(objs,switchSystem):
    
    if objs:
        systems=[]
        for obj in objs:
            metaNode=meta.r9Meta.MetaClass(obj).getParentMetaNode()
            if metaNode:
                systems.append(metaNode.getParentMetaNode().mNode)
        
        systems=set(systems)
        for system in systems:
            system=meta.r9Meta.MetaClass(system)
            
            controls=system.getChildren(cAttrs='controls')
            
            #transforming controls to switch system
            currentSystem=None
            for control in controls:
                
                control=meta.r9Meta.MetaClass(control)
                
                if control.system=='extra':
                    for attr in cmds.listAttr(control.node,userDefined=True):
                        
                        if attr=='fk':
                            if cmds.getAttr(control.node[0]+'.fk'):
                                currentSystem='fk'
                        
                        if attr=='ik':
                            if cmds.getAttr(control.node[0]+'.ik'):
                                currentSystem='ik'
            
            if currentSystem:
                
                for control in controls:
                    
                    control=meta.r9Meta.MetaClass(control)
                    
                    if control.system!=currentSystem:
                        if control.hasAttr('switch'):
                            for switch in control.switch:
                                if switch.system==currentSystem:
                                    mru.Snap(switch.node[0], control.node[0])
            else:
                cmds.warning('No current system is active! Setting %s as active system.' % switchSystem)
            
            #blending to switch system
            for control in controls:
                
                control=meta.r9Meta.MetaClass(control)
                
                if control.system=='extra':
                    if switchSystem in cmds.listAttr(control.node,userDefined=True):
                        
                        cmds.setAttr(control.node[0]+'.'+switchSystem,1)
                    else:
                        cmds.warning('System "%s" was not found!' % switchSystem)
    else:
        cmds.warning('No objects found to switch!')

#switch(cmds.ls(selection=True),'fk')