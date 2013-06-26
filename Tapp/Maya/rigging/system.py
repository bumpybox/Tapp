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
                checklist.append(cls.__name__)
            
            if not self.methods in checklist:
                log.error('build: methods input string invalid!')
                return
            else:
                self.methods=[self.methods]

        
        for cls in subclasses:
            temp=cls(self.chain,log)
            
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
        
        #build system
        mrs.buildSystem(self.chain)
        
        #build methods
        for build in self.builds:
            
            build.build()

system('|clavicle').build()

'''
switching
need to have a method for adding controls/sockets to systems
    so I can add fk clavicle to ik system
better way of getting from system back to guide
hook up controls visibility to blend control
build spline
place guides like clusters tool
    if multiple verts, use one of them to align the guide towards
'''

'''         
            #parenting roots
            self.rootParent(self.chain)
        
        #switching
        self.switch(self.chain)
    
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