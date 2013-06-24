import operator

import Tapp.Maya.rigging.builds as mrb
reload(mrb)
import Tapp.Maya.rigging.system_utils as mrs
reload(mrs)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler=logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(funcName)s - LINE: %(lineno)d - %(message)s'))
log.addHandler(handler)

class system(object):
    
    def __init__(self,obj,methods=['default']):
        
        self.chain=mrs.buildChain(obj)
        self.methods=methods
        self.builds=self.getBuilds()
        
    def __repr__(self):
        
        result=''
        
        for build in self.builds:
                
            result+=build.__str__()
        
        return result
    
    def getBuilds(self):
        
        result=[]
        
        subclasses=mrb.base.__subclasses__()
        
        #if methods is a string
        if isinstance(self.methods,str):
            
            checklist=[]
            for cls in subclasses:
                checklist.append(cls.__class__.__name__)
                
            if not self.methods in checklist:
                log.error('build: methods input string invalid!')
                return
            else:
                self.methods=[self.methods]

        
        for cls in subclasses:
            temp=cls(self.chain)
            
            for method in self.methods:
                
                if method=='default':
                    if temp.executeDefault:
                        
                        result.append(temp)
                else:
                    if method==str(temp.__class__.__name__):
                        
                        result.append(temp)
        
        #sort builds by executeOrder attribute
        result = sorted(result, key=operator.attrgetter('executeOrder'))
        
        return result
    
    def build(self,deleteSource=True):
        
        #delete source
        if deleteSource:
            
            mrs.deleteSource(self.chain)
        
        #build methods
        for build in self.builds:
            
            build.build()

system('|clavicle').build()

'''
plugs!
build spline
possibly need to not have one attr for activating systems, and go to each socket and activate the system if its present
hook up controls visibility to blend control
better inheritance model
place guides like clusters tool
    if multiple verts, use one of them to align the guide towards
'''

'''
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
        '''