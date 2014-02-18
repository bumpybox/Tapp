import Tapp.Maya.Red9.core.Red9_Meta as r9Meta

class MetaRoot(r9Meta.MetaRig):
    '''
    Initial test for a MetaRig labelling system
    '''
    def __init__(self,*args,**kws):
        super(MetaRoot, self).__init__(*args,**kws)
        self.lockState=False 
    
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
        import Tapp.Maya.Red9.core.Red9_AnimationUtils as r9Anim
        r9Anim.MirrorHierarchy()._validateMirrorEnum(side) #??? do we just let the enum __setattr__ handle this?
        
        subSystem=MetaSystem(name='meta_%s_%s' % (side.lower()[0],systemType.lower()))
        self.connectChildren([subSystem],'systems', srcAttr='metaParent')
        
        #set the attrs on the newly created subSystem MetaNode
        subSystem.systemType=systemType
        subSystem.mirrorSide=side
        return subSystem

class MetaSystem(MetaRoot):
    
    def __init__(self,*args,**kws):
        super(MetaSystem, self).__init__(*args,**kws)
        self.lockState=False
    
    def __bindData__(self):
        pass
    
    def getPoints(self):
        
        nodes=self.getChildren(walk=False, cAttrs=['points'])
        
        result=[]
        for node in nodes:
            result.append(r9Meta.MetaClass(node))
        
        return result
    
    def getControls(self):
        
        nodes=self.getChildren(walk=False, cAttrs=['controls'])
        
        result=[]
        for node in nodes:
            result.append(r9Meta.MetaClass(node))
        
        return result
    
    def getChildControls(self):
        
        points=self.getChildren(walk=True, cAttrs=['points'])
        
        result=[]
        for point in points:
            for control in r9Meta.MetaClass(point).getControls():
                result.append(control)
        
        return result
    
    def getSocket(self):
        
        socket=self.getChildren(walk=False, cAttrs=['socket'])[0]
        
        return r9Meta.MetaClass(socket)

    def getPlug(self):
        
        plug=self.getChildren(walk=False, cAttrs=['plug'])[0]
        
        return r9Meta.MetaClass(plug)
    
    def addPoint(self,name=None, boundData=None):
        
        if name:
            metaNode=MetaPoint(name=name)
            
            metaNode.name=name
        else:
            metaNode=MetaPoint()
        
        self.connectChildren(metaNode, 'points', srcAttr='metaParent')
        
        if boundData:
            if issubclass(type(boundData),dict): 
                for key, value in boundData.iteritems():
                    r9Meta.log.debug('Adding boundData to node : %s:%s' %(key,value))
                    r9Meta.MetaClass(metaNode).addAttr(key, value=value)
        
        return metaNode
    
    def addPlug(self, node,plugType=None, boundData=None):
              
        if isinstance(node,list):
            raise StandardError('node must be a single Maya Object')
        
        metaNode=MetaPlug(name='meta_%s' % node)
        
        if plugType:
            metaNode.type=plugType
        
        self.connectChildren(metaNode, 'plug', srcAttr='metaParent')
        metaNode.connectChild(node, 'node', srcAttr='metaParent')
        if boundData:
            if issubclass(type(boundData),dict): 
                for key, value in boundData.iteritems():
                    r9Meta.log.debug('Adding boundData to node : %s:%s' %(key,value))
                    r9Meta.MetaClass(metaNode).addAttr(key, value=value)
        
        return metaNode
    
    def addSocket(self, node,socketSystem=None, boundData=None):
              
        if isinstance(node,list):
            raise StandardError('node must be a single Maya Object')
        
        metaNode=MetaSocket(name='meta_%s' % node)
        
        if socketSystem:
            metaNode.system=socketSystem
        
        self.connectChildren(metaNode, 'socket', srcAttr='metaParent')
        metaNode.connectChild(node, 'node', srcAttr='metaParent')
        if boundData:
            if issubclass(type(boundData),dict): 
                for key, value in boundData.iteritems():
                    r9Meta.log.debug('Adding boundData to node : %s:%s' %(key,value))
                    metaNode.addAttr(key, value=value)
        
        return metaNode
    
    def addControl(self, node,controlSystem=None,icon=None, boundData=None):
              
        if isinstance(node,list):
            raise StandardError('node must be a single Maya Object')
        
        metaNode=MetaControl(name='meta_%s' % node)
        
        if controlSystem:
            metaNode.system=controlSystem
        
        if icon:
            metaNode.icon=icon
        
        self.connectChildren(metaNode, 'controls', srcAttr='metaParent')
        metaNode.connectChild(node, 'node', srcAttr='metaParent')
        if boundData:
            if issubclass(type(boundData),dict): 
                for key, value in boundData.iteritems():
                    r9Meta.log.debug('Adding boundData to node : %s:%s' %(key,value))
                    r9Meta.MetaClass(metaNode).addAttr(key, value=value)
        
        return metaNode

class MetaPoint(MetaSystem):
    
    def __init__(self,*args,**kws):
        super(MetaPoint, self).__init__(*args,**kws)
        self.lockState=False
    
    def __bindData__(self):
        self.addAttr('solverData',{})
        self.addAttr('controlData',{})
        self.addAttr('parentData','',attrType='messageSimple')
        self.addAttr('longname', '')
        self.addAttr('size',1.0)

class MetaTransform(r9Meta.MetaRig):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(MetaTransform, self).__init__(*args,**kws) 
        self.lockState=False
    
    def __bindData__(self):
        '''
        Overload call to wipe MetaRig bind data
        '''
        pass
    
    def getNode(self):
        '''
        Returns node attached to meta node.
        '''
        
        return self.getChildren(cAttrs=['node'])[0]

class MetaSocket(MetaTransform):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(MetaSocket, self).__init__(*args,**kws) 
        self.lockState=False
    
    def __bindData__(self):
        '''
        Overload call to wipe MetaRig bind data
        '''
        pass

class MetaControl(MetaTransform):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(MetaControl, self).__init__(*args,**kws) 
        self.lockState=False
    
    def __bindData__(self):
        '''
        Overload call to wipe MetaRig bind data
        '''
        self.addAttr('system','')

class MetaPlug(MetaTransform):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(MetaPlug, self).__init__(*args,**kws) 
        self.lockState=False
    
    def __bindData__(self):
        '''
        Overload call to wipe MetaRig bind data
        '''
        self.addAttr('type','')
        
#========================================================================
# This HAS to be at the END of this module so that the RED9_META_REGISTRY
# picks up all inherited subclasses when Red9.core is imported
#========================================================================   
r9Meta.registerMClassInheritanceMapping()