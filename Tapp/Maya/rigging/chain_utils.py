import maya.cmds as cmds

import Tapp.Maya.rigging.utils as mru
reload(mru)
import Tapp.Maya.rigging.meta as meta
reload(meta)
import Tapp.Maya.rigging.builds as mrb
reload(mrb)
import MG_Tools.python.rigging.script.MG_softIk as mpsi
reload(mpsi)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler=logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(funcName)s - LINE: %(lineno)d - %(message)s'))
log.addHandler(handler)

def buildChain(obj):
    
    def chainFromSystem(obj,parent=None):
        
        node=chain(obj)
        
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
        
        node=chain(obj)
        
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
        
        log.debug('building a chain node from guide')
        
        chain=chainFromGuide(obj)
        chain.addRoot(obj,'master')
        
        return chain
        
    #build from system---
    if check.__class__.__name__=='MetaSystem':
        
        log.debug('building a chain node from system')
        
        obj=meta.r9Meta.MetaClass(obj)
        
        for socket in obj.getChildMetaNodes(mAttrs='mClass=TappSocket'):
            if not socket.hasAttr('guideParent'):
                
                chain=chainFromSystem(socket)
                chain.addRoot(obj.root,'master')
                chain.addSystem(obj)
                
                return chain

class chain(object):
    '''
    Generic data handler. This is the basis from which everything is build.
    '''
    
    def __init__(self,node):
        
        if node:
            self.source=node
        
        #tree data
        self.children=[]
        self.parent=None
        
        #transforms data
        self.translation=[]
        self.rotation=[]
        self.scale=[]
        
        self.name=''
        self.socket={}
        self.control={}
        self.data=None
        self.system=None
        self.root={}
        self.guide=None
        self.joint={}
    
    def addSystem(self,system):
        self.system=system
        
        if self.children:
            for child in self.children:
                child.addSystem(system)
    
    def addRoot(self,root,rootType):
        self.root[rootType]=root
        
        if self.children:
            for child in self.children:
                child.addRoot(root,rootType)
    
    def addChild(self,node):
        '''
        Will add the passed in node to the children list.
        '''
        self.children.append(node)
    
    def downstream(self,searchAttr):
        
        result=[]
        
        if self.children:
            for child in self.children:
                if child.data and len(set(child.data) & set(searchAttr))>0:
                    result=[child]
                else:
                    childData=child.downstream(searchAttr)
                    if childData:
                        result.extend(childData)
        else:
            return None,self
        
        return result
    
    def tween(self,endNode):
        
        result=[self]
        
        if self==endNode:
            return result
        
        if self.children:
            for child in self.children:
                result.extend(child.tween(endNode))
        
        return result
    
    def breakdown(self,startAttr,endAttr,result=[]):
        
        if len(set(self.data) & set(startAttr))>0:
            startNode=self
        else:
            startData=self.downstream(startAttr)
            if len(startData)>1:
                return result
            else:
                startNode=startData[0]
        
        endData=startNode.downstream(endAttr)
        if len(endData)>1:
            endNode=endData[1]
            
            result.append(startNode.tween(endNode))
            return result
        else:
            endNode=endData[0]
        
        result.append(startNode.tween(endNode))
        
        if endNode.children:
            return endNode.breakdown(startAttr,endAttr,result=result)
        
        return result

class system():
    
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
    
    def build(self,methods=['fk','ik','spline'],blend=True,deleteSource=True):
        
        #if methods is a string
        if isinstance(methods,str):
            checkList=['fk','ik','joints','spline','guide']
            if not methods in checkList:
                self.log.error('build: methods input string invalid!')
                return
            else:
                methods=[methods]
        
        #checking input type
        if not isinstance(methods,list):
            self.log.error('build: methods is a not a list!')
            return
        
        #delete source
        if deleteSource:
            
            if self.chain.root:
                
                log.debug('deleting the source: %s' % self.chain.root['master'])
                
                cmds.delete(self.chain.root['master'])
                self.chain.root['master']=None
            
            if self.chain.system:
                for control in self.chain.system.getChildren(cAttrs='controls'):
                    meta.r9Meta.MetaClass(control).delete()
                    
                for socket in self.chain.system.getChildren(cAttrs='sockets'):
                    meta.r9Meta.MetaClass(socket).delete()
                
                log.debug('deleting the system: %s' % self.chain.system)
                
                self.chain.system.delete()
                self.chain.system=None
        
        #adding root and system
        if ['guide','joints'] not in methods:
            #rig asset
            #asset=cmds.container(n='rig',type='dagContainer')
            asset=cmds.group(empty=True,n='rig')
            attrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
            mru.ChannelboxClean(asset, attrs)
            
            self.chain.addRoot(asset,'master')
            
            #meta rig
            system=meta.MetaSystem()
            
            system.root=asset
            
            self.chain.addSystem(system)
        
        #build methods
        for method in methods:
            if method=='fk':
                for c in self.fk_chains:
                    mrb.fk_build(c)
            
            if method=='ik':
                for c in self.ik_chains:
                    mrb.ik_build(c)
            
            if method=='joints':
                mrb.joints_build(self.chain)
            
            if method=='guide':
                mrb.guide_build(self.chain)
        
        #blending
        if blend and ['guide','joints'] not in methods:
            
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
system()

#rebuild system
#chain=buildChain('TappSystem')
#solver(chain).build(method='all',blend=True)

'''
plugs!
build spline
possibly need to not have one attr for activating systems, and go to each socket and activate the system if its present
hook up controls visibility to blend control
better inheritance model
place guides like clusters tool
    if multiple verts, use one of them to align the guide towards
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