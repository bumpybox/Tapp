import maya.cmds as cmds

class Meta():
    ''' Class for all nodes functions associated with the meta data '''
    
    def setData(self,name,nodeType,component,metaParent,*args):
        ''' Create a network node with the requested data 
            args should be passed in as a dictionary
        '''
        
        #create network node
        node=cmds.shadingNode( 'network',asUtility=True, n=name)
        
        #add base data
        cmds.addAttr(node,longName='type',dataType='string')
        if nodeType==None:
            cmds.warning('Not setting nodeType on %s can be BAD!' % node)
        else:
            cmds.setAttr('%s.type' % node,nodeType,type='string')
        
        if component==None:
            cmds.warning('Not setting component on %s can be BAD!' % node)
        else:
            cmds.addAttr(node,longName='component',dataType='string')
            
            cmds.setAttr('%s.component' % node,component,type='string')
        
        cmds.addAttr(node,longName='metaParent',attributeType='message')
        if metaParent==None:
            cmds.warning('No metaParent specified for %s.' % node)
        else:           
            cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
        
        #add extra data
        if args[0]!=None:
            for arg in args[0]:
                if arg=='switch':
                    cmds.addAttr(node,longName=arg,attributeType='message')
                    cmds.connectAttr('%s.message' % args[0][arg],'%s.switch' % node)
                else:
                    cmds.addAttr(node,longName=arg,dataType='string')
                    cmds.setAttr('%s.%s' % (node,arg),args[0][arg],type='string')
        
        return node
    
    def setTransform(self,node,metaParent):
        ''' Create an metaParent attribute on the passed transform,
        and connect to the passed meta node.'''
        
        cmds.addAttr(node,longName='metaParent',attributeType='message')
        cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
    
    def getTransform(self,node):
        ''' Returns the transform node attached to a meta node. '''
        
        return cmds.listConnections('%s.message' % node,type='transform')[0]

    def getData(self,node):
        ''' Returns the meta data as a dictionary for the requested node '''
        
        #making sure we get a network node
        if cmds.nodeType(node)!='network':
            metaNode=cmds.listConnections('%s.metaParent' % node)[0]
        else:
            metaNode=node
        
        #setting data variables
        attrList=cmds.attributeInfo(metaNode,all=True)
        data={}
        data['name']=metaNode
        
        #looping through custom attributes
        for count in range(7,len(attrList)):
            
            attr=attrList[count]
            
            if cmds.getAttr('%s.%s' % (metaNode,attr),type=True)=='enum':               
                data[attr]=cmds.getAttr('%s.%s' % (metaNode,attr),asString=True)
            
            if cmds.getAttr('%s.%s' % (metaNode,attr),type=True)!='enum' and cmds.getAttr('%s.%s' % (metaNode,attr),type=True)!='message':
                data[attr]=cmds.getAttr('%s.%s' % (metaNode,attr))
            
            if cmds.getAttr('%s.%s' % (metaNode,attr),type=True)=='message':
                
                #query whether message attribute is connected
                if cmds.listConnections('%s.%s' % (metaNode,attr))==None:
                    data[attr]=None
                else:
                    metaParent=cmds.listConnections('%s.%s' % (metaNode,attr))[0]
                    
                    data[attr]=metaParent
        
        return data
    
    def upStream(self,node,nodeType):
        ''' Returns the parent node with the requested nodeType. '''
        
        upStreamNode=None
        data=self.getData(node)
        
        if data['type']!=nodeType:
            upStreamNode=self.upStream(cmds.listConnections('%s.metaParent' % node)[0],nodeType)
        
        if data['type']==nodeType:
            upStreamNode=node
        
        return upStreamNode
    
    def downStream(self,node,nodeType,allNodes=False):
        ''' Returns allNodes nodes down the hierarchy with the requested nodeType. 
        
            If allNodes=True, nodes further down the hierarchy is returned as well.
        '''
        
        childNodes=cmds.listConnections('%s.message' % node,type='network')
        
        validNodes=[]
        
        if childNodes!=None:
            for n in childNodes:
                data=self.getData(n)
                
                if data['type']==nodeType:
                    validNodes.append(n)
                
                #if user wants the whole hierarchy
                if allNodes==True:
                    if (self.downStream(n,nodeType,allNodes=allNodes))!=None:
                        for m in (self.downStream(n,nodeType,allNodes=allNodes)):
                            validNodes.append(m)
            
            return validNodes
    
    def getHierarchies(self):
        hierarchies={}
        hierarchies['None']=[]
        
        for node in cmds.ls(nodeType='network'):
            data=self.getData(node)
            
            if data['metaParent']==None:
                hierarchies['None'].append(node)
            
            if cmds.listConnections('%s.message' % node,nodeType='network')>0:
                hierarchies[node]=[]
                
                for child in cmds.listConnections('%s.message' % node,nodeType='network'):
                    hierarchies[node].append(child)
        
        return hierarchies