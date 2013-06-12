import Red9.core.Red9_Meta as r9Meta

class TappRig(r9Meta.MetaRig):
    '''
    Initial test for a MetaRig labelling system
    '''
    def __init__(self,*args,**kws):
        super(TappRig, self).__init__(*args,**kws)
        self.lockState=True

    def addMetaSubSystem(self, systemType, side, nodeName=None): 
        '''
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
        self.addAttr('systemType', attrType='string')
        self.addAttr('mirrorSide',enumName='Centre:Left:Right',attrType='enum')  
    
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
    
    def addControl(self, node, boundData=None):
              
        if isinstance(node,list):
            raise StandardError('node must be a single Maya Object')
        
        metaNode=TappControl(name='meta_%s' % node)
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
        pass

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