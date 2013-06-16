import Red9.core.Red9_Meta as r9Meta

class chain():
    
    def __init__(self,obj):
        self.source=obj
        
        self.name=''
        self.socket={}
        self.control={}
        self.data=None
        self.children=[]
        self.parent=None
        self.translation=[]
        self.rotation=[]
        self.scale=[]
        self.system=None
        self.root=None
        self.guide=None
    
    def addSystem(self,system):
        self.system=system
        
        if self.children:
            for child in self.children:
                child.addSystem(system)
    
    def addRoot(self,root):
        self.root=root
        
        if self.children:
            for child in self.children:
                child.addRoot(root)
    
    def addChild(self,child):
        self.children.append(child)
    
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
        
class TappRig(r9Meta.MetaRig):
    '''
    Initial test for a MetaRig labelling system
    '''
    def __init__(self,*args,**kws):
        super(TappRig, self).__init__(*args,**kws)
        self.lockState=True

    def addMetaSubSystem(self, systemType, side, nodeName=None): 
        '''
        Overload of default addMetaSubSystem method
        
        Basic design of a MetaRig is that you have sub-systems hanging off an mRig
        node, managing all controllers and data for a particular system, such as an
        Arm system. 
        
        @param systemType: Attribute used in the message link. Note this is what you use
                     to transerve the Dag tree so use something sensible! 
        @param mirrorSide: Side to designate the system. This is an enum: Centre,Left,Right
        @param nodeName: Name of the MetaClass network node created
        '''
        import Red9.core.Red9_AnimationUtils as r9Anim
        r9Anim.MirrorHierarchy()._validateMirrorEnum(side) #??? do we just let the enum __setattr__ handle this?
        
        subSystem=TappSystem(name='meta_%s_%s' % (side.lower()[0],systemType.lower()))
        self.connectChildren([subSystem],'systems', srcAttr='metaParent')
        
        #set the attrs on the newly created subSystem MetaNode
        subSystem.systemType=systemType
        subSystem.mirrorSide=side
        return subSystem

class TappSystem(TappRig):
    
    def __init__(self,*args,**kws):
        super(TappSystem, self).__init__(*args,**kws)
        self.lockState=True
    
    def __bindData__(self):
        self.addAttr('mirrorSide',enumName='Centre:Left:Right',attrType='enum')
        self.addAttr('root',attrType='messageSimple')
    
    def addPlug(self, node, boundData=None):
              
        if isinstance(node,list):
            raise StandardError('node must be a single Maya Object')
        
        metaNode=TappPlug(name='meta_%s' % node)
        self.connectChildren(metaNode, 'plugs', srcAttr='metaParent')
        metaNode.connectChild(node, 'node', srcAttr='metaParent')
        if boundData:
            if issubclass(type(boundData),dict): 
                for key, value in boundData.iteritems():
                    r9Meta.log.debug('Adding boundData to node : %s:%s' %(key,value))
                    r9Meta.MetaClass(metaNode).addAttr(key, value=value)
        
        return metaNode
    
    def addSocket(self, node, boundData=None):
              
        if isinstance(node,list):
            raise StandardError('node must be a single Maya Object')
        
        metaNode=TappSocket(name='meta_%s' % node)
        self.connectChildren(metaNode, 'sockets', srcAttr='metaParent')
        metaNode.connectChild(node, 'node', srcAttr='metaParent')
        if boundData:
            if issubclass(type(boundData),dict): 
                for key, value in boundData.iteritems():
                    r9Meta.log.debug('Adding boundData to node : %s:%s' %(key,value))
                    metaNode.addAttr(key, value=value)
        
        return metaNode
    
    def addControl(self, node,system, boundData=None):
              
        if isinstance(node,list):
            raise StandardError('node must be a single Maya Object')
        
        metaNode=TappControl(name='meta_%s' % node)
        metaNode.system=system
        
        self.connectChildren(metaNode, 'controls', srcAttr='metaParent')
        metaNode.connectChild(node, 'node', srcAttr='metaParent')
        if boundData:
            if issubclass(type(boundData),dict): 
                for key, value in boundData.iteritems():
                    r9Meta.log.debug('Adding boundData to node : %s:%s' %(key,value))
                    r9Meta.MetaClass(metaNode).addAttr(key, value=value)
        
        return metaNode

class TappSocket(r9Meta.MetaRig):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(TappSocket, self).__init__(*args,**kws) 
        self.lockState=True
    
    def __bindData__(self):
        '''
        Overload call to wipe MetaRig bind data
        '''
        pass

class TappControl(r9Meta.MetaRig):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(TappControl, self).__init__(*args,**kws) 
        self.lockState=True
    
    def __bindData__(self):
        '''
        Overload call to wipe MetaRig bind data
        '''
        self.addAttr('system','')

class TappPlug(r9Meta.MetaRig):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(TappPlug, self).__init__(*args,**kws) 
        self.lockState=True
    
    def __bindData__(self):
        '''
        Overload call to wipe MetaRig bind data
        '''
        pass
        
#========================================================================
# This HAS to be at the END of this module so that the RED9_META_REGISTRY
# picks up all inherited subclasses when Red9.core is imported
#========================================================================   
r9Meta.registerMClassInheritanceMapping()
r9Meta.registerMClassNodeMapping()