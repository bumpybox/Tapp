import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.rigging.utils as mru
reload(mru)
import MG_Tools.python.rigging.script.MG_softIk as mpsi
reload(mpsi)
import Tapp.Maya.rigging.meta as meta
reload(meta)

def buildChain(obj,parent=None):
    
    node=meta.chain(obj)
    
    #getting name
    node.name=obj.split('|')[-1]
    
    #getting attr data
    data={}
    for attr in cmds.listAttr(node.name,userDefined=True):
        data[attr]=cmds.getAttr(node.name+'.'+attr)
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
            node.addChild(buildChain(child,parent=node))
        
        return node
    else:
        return node

def fk_build(chainList):
    
    #build rig---
    root=cmds.group(empty=True,name='fk_grp')
    
    cmds.parent(root,chainList[0].root)
    
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
            
            node.system.addControl(cnt)

def ik_build(chainList):
    
    #build rig---
    root=cmds.group(empty=True,name='ik_grp')
    
    cmds.parent(root,chainList[0].root)
    
    #finding upvector
    posA=cmds.xform(chainList[0].name,q=True,ws=True,translation=True)
    posB=cmds.xform(chainList[1].name,q=True,ws=True,translation=True)
    posC=cmds.xform(chainList[2].name,q=True,ws=True,translation=True)
    crs=mru.CrossProduct(posA,posB,posC)
    
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
        
        #need to do this, but without using the string name---
        if chainList[count]!=chainList[-1]:
            cmds.aimConstraint(chainList[count+1].name,grp,worldUpType='vector',
                               worldUpVector=crs)
        
        rot=cmds.xform(grp,query=True,rotation=True)
        cmds.rotate(rot[0],rot[1],rot[2],jnt,
                    worldSpace=True,pcp=True)
        
        cmds.makeIdentity(jnt,apply=True,t=1,r=1,s=1,n=0)
        
        cmds.delete(grp)
        
        if chainList[count]!=chainList[0]:
            cmds.parent(jnt,jnts[-1])
        
        if len(jnts)==0:
            cmds.parent(jnt,root)
        
        jnts.append(jnt)
        
        #create sockets
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(None,socket, translation=node.translation, rotation=node.rotation)
        cmds.parent(socket,jnt)
        node.socket['ik']=socket
    
    #create ik
    ikStart=cmds.group(empty=True)
    ikEnd=cmds.group(empty=True)
    
    mru.Snap(jnts[0],ikStart)
    mru.Snap(jnts[-1],ikEnd)
    
    ikResult=mpsi.MG_softIk(jnts,startMatrix=ikStart,endMatrix=ikEnd,root=root)
    
    #setup ik
    cmds.addAttr(node.root,ln='ik_stretch',at='float',min=0,max=1)
    
    cmds.connectAttr(node.root+'.ik_stretch',ikResult['softIk']+'.stretch')
    
    #build controls---
    for node in chainList:
        
        count=chainList.index(node)
        
        prefix=node.name.split('|')[-1]+'_ik_'
        
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
            
            node.system.addControl(cnt)
            
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
                
                cmds.parent(polevectorSHP,root)
                cmds.parent(phgrp,root)
            else:
                
                cmds.pointConstraint(cnt,ikEnd)
                cmds.parent(node.socket['ik'],cnt)
                
                cmds.parent(phgrp,root)

class solver():
    
    def __init__(self,chain):
        
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
    
    def blend(self,node,control,system):
        
        prefix=node.name.split('|')[-1]+'_bld_'
        
        #create socket
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(node.name, socket)
        
        metaNode=system.addSocket(socket,boundData={'data':node.data})
        if node.parent:
            metaParent=meta.r9Meta.MetaClass(node.parent.socket['blend'])
            metaParent=metaParent.getParentMetaNode()
            #metaNode.addAttr('guideParent',metaParent,attrType='messageSimple')
            
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
        
        if node.children:
            for child in node.children:
                self.blend(child,control,system)
    
    def build(self,method=['fk','ik','spline','joint','all'],blend=[True,False]):
        
        if method:
            #rig asset
            asset=cmds.container(n='rig',type='dagContainer')
            attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
            mru.ChannelboxClean(asset, attrs)
            
            self.chain.addRoot(asset)
            
            #meta rig
            system=meta.TappSystem()
            self.chain.addSystem(system)
        
        if method=='fk':
            for c in self.fk_chains:
                fk_build(c)
        
        if method=='ik':
            for c in self.ik_chains:
                ik_build(c)
        
        if method=='all':
            for c in self.fk_chains:
                fk_build(c)
            
            for c in self.ik_chains:
                ik_build(c)
        
        if blend:
            
            #create extra control
            cnt=mru.Pin('extra_cnt')
            
            #create blend sockets
            self.blend(self.chain,cnt,system)
            
            #setup extra control
            mru.Snap(self.chain.name,cnt)
            
            cmds.parent(cnt,self.chain.socket['blend'])
            cmds.rotate(0,90,0,cnt,r=True,os=True)
            
            if cmds.objExists(asset+'.ik_stretch'):
                cmds.addAttr(cnt,ln='ik_stretch',at='float',k=True,
                             min=0,max=1)
                
                cmds.connectAttr(cnt+'.ik_stretch',asset+'.ik_stretch')
        
        cmds.delete(self.chain.name)

chain=buildChain('|clavicle')
solver(chain).build('ik',blend=False)

'''
troubleshoot blend
build guide directly from solver class

ability to choose control icon for control tags
'''

'''
mRig=meta.MetaRig(name='meta_root')
mRig.CTRL_Prefix='cnt'
spine=mRig.addMetaSubSystem('spine', 'Centre')
arm=spine.addMetaSubSystem('arm', 'Left')
#print mRig.getChildren(cAttrs='systems')
spine.addPlug('locator1')
arm.addControl('locator2')
spine.addSocket('locator3')
'''