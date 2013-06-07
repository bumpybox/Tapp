import maya.cmds as cmds

from Tapp.Maya.Red9.core.Red9_Meta import *

class MetaRig(MetaClass):
    '''
    Initial test for a MetaRig labelling system
    '''
    def __init__(self,*args,**kws):
        super(MetaRig, self).__init__(*args,**kws)
        self.lockState=True
    
    def addMetaSubSystem(self, systemType, side,  attr=None, nodeName=None): 
        '''
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
        
        subSystem=MetaRigSubSystem(nodeName)
        self.connectChild(subSystem, 'systems',cleanCurrent=False)
        #subSystem=self.addChildMetaNode('MetaRigSubSystem', attr='systems', nodeName=nodeName) 
        
        #set the attrs on the newly created subSystem MetaNode
        subSystem.systemType=systemType
        subSystem.mirrorSide=side
        return subSystem

'''
class MetaRigSubSystem(MetaRig):

    def __init__(self,*args,**kws):
        super(MetaRigSubSystem, self).__init__(*args,**kws) 
        self.lockState=True
    
    def addPlug(self, node, boundData=None):
        
        if isinstance(node,list):
            raise StandardError('node must be a single Maya Object')
        
        self.connectChild(node,'plug')  
        if boundData:
            if issubclass(type(boundData),dict): 
                for key, value in boundData.iteritems():
                    log.debug('Adding boundData to node : %s:%s' %(key,value))
                    MetaClass(node).addAttr(key, value=value)
                    '''

class MetaSocket(MetaRig):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(MetaSocket, self).__init__(*args,**kws) 
        self.lockState=True

class MetaPlug(MetaRig):
    '''
    Example Export base class inheriting from MetaClass
    '''
    def __init__(self,*args,**kws):
        super(MetaPlug, self).__init__(*args,**kws) 
        self.lockState=True
    
        
#========================================================================
# This HAS to be at the END of this module so that the RED9_META_REGISTRY
# picks up all inherited subclasses when Red9.core is imported
#========================================================================   
registerMClassInheritanceMapping()
registerMClassNodeMapping()