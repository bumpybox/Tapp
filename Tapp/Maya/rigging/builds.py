import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.rigging.utils as mru
reload(mru)
import Tapp.Maya.MG_Tools.python.rigging.script.MG_softIk as mpsi
reload(mpsi)
import Tapp.Maya.rigging.meta as meta
reload(meta)
import Tapp.Maya.rigging.system_utils as mrs
reload(mrs)
import Tapp.Maya.utils.ZvParentMaster as muz

class base(object):
    
    def __init__(self,chain,log):
        
        self.log=log
        self.chain=chain
        self.executeDefault=False
        self.executeOrder=1
        self.dependencies=[]

class system(base):
    
    def __init__(self,chain,log):
        super(system,self).__init__(chain,log)
        
        self.executeDefault=True
        self.executeOrder=0
        
        self.chain=chain
        
    def build(self):
        
        self.log.debug('building system')
        
        #meta rig
        self.system=meta.MetaSystem()
        
        self.chain.addSystem(self.system)
        
        #create points
        self.createPoints(self.chain)
    
    def createPoints(self,node):
        
        #creating and assigning meta point
        node.point=self.system.addPoint(name=node.name)
        
        #storing guide data on meta point
        data=mrs.pointToDict(node)
        node.point.addAttr('guideData',data)
        
        #recurse into children
        if node.children:
            
            for child in node.children:
                
                self.createPoints(child)

class ik(base):
    
    def __init__(self,chain,log):
        super(ik,self).__init__(chain,log)
        
        self.executeDefault=True
        self.chain=chain
        
        self.chains=self.setChains()
        
        for node in self.chains[0]:
            
            print node.name
        
        self.dependencies=[system]
    
    def __str__(self):
        
        result=''
        
        for c in self.chains:
            result+='ik chain from:\n'
            for node in c:
                result+=node.name+'\n'
        
        return result
    
    def setChains(self):
        
        startAttr=['IK_solver_start','IK_control']
        endAttr=['IK_solver_end']
        
        return self.chain.breakdown(startAttr,endAttr,result=[])
    
    def build(self):
        
        self.log.debug('building ik rig')
        
        for chain in self.chains:
            
            self.__build(chain)
    
    def __build(self,chain):
    
        #build rig---       
        #create root grp
        rootgrp=cmds.group(empty=True,name='ik_grp')
        
        #fail safe
        if chain[0].plug['master']:
            cmds.parent(rootgrp,chain[0].plug['master'])
        
        #create plug object
        plug=cmds.spaceLocator(name='ik_plug')[0]
        
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
        
        self.chains[0][0].point.addPlug(plug,plugType='system')
        
        #finding upvector
        crs=mru.CrossProduct(chain[0].translation,
                             chain[1].translation,
                             chain[2].translation)
        
        #creating joints and sockets
        jnts=[]
        for node in chain:
            count=chain.index(node)
            
            prefix=node.name.split('|')[-1]+'_ik_'
            
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
            node.socket['ik']=socket
        
        #plug parent
        cmds.parent(jnts[0],plug)
        
        #create ik
        startStretch=cmds.group(empty=True,n='startStretch')
        endStretch=cmds.group(empty=True,n='endStretch')
        
        mru.Snap(jnts[0],startStretch)
        mru.Snap(jnts[-1],endStretch)
        
        ikResult=mpsi.MG_softIk(jnts,startMatrix=startStretch,endMatrix=endStretch,root=rootgrp)
        
        ikResult['ikHandle']=cmds.rename(ikResult['ikHandle'],'ikHandle')
        
        cmds.parent(startStretch,plug)
        
        #setup ik
        cmds.addAttr(plug,ln='ik_stretch',at='float',min=0,max=1,k=True)
        
        cmds.connectAttr(plug+'.ik_stretch',ikResult['softIk']+'.stretch')
        
        #build controls---
        self.log.debug('building ik controls')
        
        for node in chain:
            
            count=chain.index(node)
            
            prefix=node.name+'_ik_'
            
            #building root control, polevector and end control
            if 'IK_control' in node.data:
                
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
                node.control['ik']=cnt
                
                phgrp=cmds.group(empty=True,n=(cnt+'_PH'))
                sngrp=cmds.group(empty=True,n=(cnt+'_SN'))
                
                mru.Snap(cnt,phgrp)
                mru.Snap(cnt,sngrp)
                
                cmds.parent(phgrp,cntplug)
                cmds.parent(sngrp,phgrp)
                cmds.parent(cnt,sngrp)
                
                #adding cntplug and cnt to meta system
                node.point.addPlug(cntplug,plugType='control')
                
                node.point.addControl(cnt,controlSystem='ik')
                
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

class fk(base):
    
    def __init__(self,chain,log):
        super(fk,self).__init__(chain,log)
        
        self.executeDefault=True
        self.chain=chain
        
        self.chains=self.setChains()
        
        self.dependencies=[system]
            
    def __str__(self):
        
        result=''
        
        self.setChains()
        
        for c in self.chains:
            result+='fk chain from:\n'
            for node in c:
                result+=node.name+'\n'
        
        return result
    
    def setChains(self):
        
        startAttr=['FK_solver_start','FK_control']
        endAttr=['FK_solver_end']
        
        return self.chain.breakdown(startAttr,endAttr,result=[])
    
    def build(self):
        
        self.log.debug('building fk rig')
        
        for chain in self.chains:
            
            self.__build(chain)
    
    def __build(self,chain):
    
        #build rig---
        #create root grp
        rootgrp=cmds.group(empty=True,name='fk_grp')
        
        if chain[0].plug['master']:
            cmds.parent(rootgrp,chain.plug['master'])
        
        #create plug object
        plug=cmds.spaceLocator(name='fk_plug')[0]
        
        #setup plug
        phgrp=cmds.group(empty=True,n=(plug+'_PH'))
        sngrp=cmds.group(empty=True,n=(plug+'_SN'))
        
        cmds.parent(sngrp,phgrp)
        cmds.parent(plug,sngrp)
        
        mru.Snap(None,phgrp,
                 translation=chain[0].translation,
                 rotation=chain[0].rotation)
        cmds.parent(phgrp,rootgrp)
        
        self.chain.point.addPlug(plug,plugType='system')
        
        for node in chain:
            
            prefix=node.name.split('|')[-1]+'_fk_'
            
            #create sockets
            socket=cmds.spaceLocator(name=prefix+'socket')[0]
            
            #setup socket
            mru.Snap(None,socket, translation=node.translation, rotation=node.rotation)
            node.socket['fk']=socket
            
            if node.parent:
                cmds.parent(socket,node.parent.socket['fk'])
            else:
                cmds.parent(socket,plug)
        
        #build controls---
        self.log.debug('building fk controls')
        
        for node in chain:
            
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
                    cmds.parent(phgrp,plug)
                
                if node.point:
                    node.point.addControl(cnt,controlSystem='fk')

class blend(base):
    
    def __init__(self,chain,log):
        super(blend,self).__init__(chain,log)
        
        self.executeDefault=True
        self.executeOrder=99
        self.chain=chain
    
    def build(self):
        
        self.log.debug('building blend')
        
        print self.chain.breakdown('extraControl','extraControl',result=[])
        
        #create extra control
        cnt=mru.Pin('extra_cnt')
        
        self.control=cnt
        
        #building blends
        self.rootgrp=cmds.group(empty=True,name='blend_grp')
        
        self._build(self.chain)
        
        #setup extra control
        mru.Snap(None,cnt,translation=self.chain.translation,rotation=self.chain.rotation)
        
        cmds.parent(cnt,self.chain.socket['blend'])
        cmds.rotate(0,90,0,cnt,r=True,os=True)
        
        attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']
        mru.ChannelboxClean(cnt, attrs)
        
        self.chain.point.addControl(cnt,'extra')
        
        self.switch(self.chain)
    
    def switch(self,node):
        
        self.log.debug('setup switching')
            
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
                self.switch(child)
    
    def _build(self,node):
        
        prefix=node.name.split('|')[-1]+'_bld_'
        
        #create socket
        socket=cmds.spaceLocator(name=prefix+'socket')[0]
        
        #setup socket
        mru.Snap(None, socket,translation=node.translation,rotation=node.rotation)
        
        cmds.parent(socket,self.rootgrp)
        
        node.point.addSocket(socket)
        
        for s in node.socket:
            
            con=cmds.parentConstraint(node.socket[s],socket)[0]
            
            #ensuring extra control has the attribute
            if not cmds.objExists(self.control+'.'+s):
                
                cmds.addAttr(self.control,ln=s,at='float',min=0,max=1,k=True)
            
            #only connecting extra controller if there are more than one system present
            if len(node.socket)>1:
                
                #connecting extra to target weights - using string search, which probably needs improvement ---
                targets=cmds.parentConstraint(con,q=True,weightAliasList=True)
                
                for target in targets:
                    
                    if ('_'+s+'_') in target:
                        
                        cmds.connectAttr(self.control+'.'+s,con+'.'+target)
            
            #parenting up the chain
            if node.parent:
                
                #making sure the chain has ended
                if s not in node.parent.socket:
                    
                    cmds.select(node.plug[s],node.parent.socket['blend'])
                    muz.attach()
        
        node.socket['blend']=socket
        
        if node.children:
            for child in node.children:
                self._build(child)


class guide(base):
    
    def __init__(self,chain,log):
        super(guide,self).__init__(chain,log)
    
    def __str__(self):
        
        return 'guide build!'
    
    def build(self):
        
        self.log.debug('building guide controls')
        
        #if system exists, deletes it
        if self.chain.system:
            self.chain.system.delete()
        
        self.__build(self.chain)
    
    def __build(self,chain):
        #build controls---
        cnt=mru.implicitSphere(chain.name)
            
        chain.guide=cnt
        
        mru.Snap(None, cnt, translation=chain.translation, rotation=chain.rotation)
        
        #adding data
        for data in chain.data:
            
            mNode=meta.r9Meta.MetaClass(cnt)
            mNode.addAttr(data,chain.data[data])
        
        #parenting
        if chain.parent:
            chain.guide=cmds.parent(cnt,chain.parent.guide)
        
        #traversing down the node tree
        if chain.children:
            for child in chain.children:
                self.__build(child)

class joints(base):

    def __init__(self,chain,log):
        super(joints,self).__init__(chain,log)
    
    def __str__(self):
        
        return 'joints build!'
    
    def build(self):
        
        self.log.debug('building joints rig')
        
        self.__build(self.chain)
    
    def __build(self,chain):
    
        #build rig---
        #creating joint
        cmds.select(cl=True)
        jnt=cmds.joint(n=chain.name)
        
        chain.joint=jnt
        
        #setup joint
        mru.Snap(None,jnt, translation=chain.translation, rotation=chain.rotation)
        
        #parent and children
        if chain.parent:
            chain.joint=cmds.parent(jnt,chain.parent.joint)
        else:
            #create root grp
            rootgrp=cmds.group(empty=True,name='joints_grp')
            
            if chain.plug['master']:
                cmds.parent(rootgrp,chain.plug['master'])
            
            cmds.parent(jnt,rootgrp)
        
        if chain.children:
            for child in chain.children:
                self.__build(child)