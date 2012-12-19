import maya.cmds as cmds

class meta():
    ''' Class for all functions associated with the meta data '''
    
    def createSkin(self,name):
        ''' Creates a skin meta node'''
        
        return self.setData(name,'skin',None,None,None)
    
    def createProxy(self,name):
        ''' Creates a skin meta node'''
        
        return self.setData(name,'proxy',None,None,None)
    
    def createControl(self,name,component,metaParent,data):
        ''' Creates a control meta node 
            data needs to be dictionary
        '''
        
        return self.setData(name,'control',component,metaParent,data)
    
    def createRoot(self,name,version,component):
        ''' Creates a root meta node '''
        
        data={'version':version}
        
        return self.setData(name, 'root', component, None,data)
    
    def createModule(self,name,component,metaParent,index,side):
        ''' Creates a module meta node '''
        
        data={'index':index,'side':side}
        
        return self.setData(name,'module',component,metaParent,data)
    
    def setData(self,name,type,component,metaParent,*args):
        ''' Create a network node with the requested data 
            args should be passed in as a dictionary
        '''
        
        #create network node
        node=cmds.shadingNode( 'network',asUtility=True, n=name)
        
        #add base data
        cmds.addAttr(node,longName='type',dataType='string')
        if type==None:
            cmds.warning('Not setting type on %s can be BAD!' % node)
        else:
            cmds.setAttr('%s.type' % node,type,type='string')
        
        cmds.addAttr(node,longName='component',dataType='string')
        if component==None:
            cmds.warning('Not setting component on %s can be BAD!' % node)
        else:
            cmds.setAttr('%s.component' % node,component,type='string')
        
        cmds.addAttr(node,longName='metaParent',attributeType='message')
        if metaParent==None:
            cmds.warning('No metaParent specified for %s.' % node)
        else:
            cmds.connectAttr('%s.message' % metaParent,'%s.metaParent' % node)
        
        #add extra data
        if args[0]!=None:
            for arg in args[0]:
                cmds.addAttr(node,longName=arg,dataType='string')
                cmds.setAttr('%s.%s' % (node,arg),args[0][arg],type='string')
        
        return node
    
    def getData(self,node):
        ''' Returns the meta data as a dictionary for the requested node '''
        
        #making sure we get a network node
        if cmds.nodeType(node)!='network':
            metaNode=cmds.listConnections('%s.metaParent' % node)[0]
        else:
            metaNode=node
        
        #setting data variables
        attrList=[]
        attrList=cmds.attributeInfo(metaNode,all=True)
        data={}
        data['name']=metaNode
        
        #looping through custom attributes
        for count in range(7,len(attrList)):
            
            attr=attrList[count]
            
            if cmds.getAttr('%s.%s' % (metaNode,attr),type=True)!='message':
                data[attr]=cmds.getAttr('%s.%s' % (metaNode,attr))
            
            if cmds.getAttr('%s.%s' % (metaNode,attr),type=True)=='message':
                
                #query whether message attribute is connected
                if cmds.listConnections('%s.%s' % (metaNode,attr))==None:
                    data[attr]=None
                else:
                    metaParent=cmds.listConnections('%s.%s' % (metaNode,attr))[0]
                    
                    data[attr]=metaParent
        
        return data
    
    def upStream(self,node,type):
        ''' Returns the parent node with the requested type. '''
        
        upStreamNode=None
        data=self.getData(node)
        
        if data['type']!=type:
            upStreamNode=self.upStream(cmds.listConnections('%s.metaParent' % node)[0],type)
        
        if data['type']==type:
            upStreamNode=node
        
        return upStreamNode
    
    def downStream(self,node,type,all=False):
        ''' Returns all nodes down the hierarchy with the requested type. 
        
            If all=True, nodes further down the hierarchy is returned as well.
        '''
        
        childNodes=cmds.listConnections('%s.message' % node,type='network')
        
        validNodes=[]
        
        if childNodes!=None:
            for n in childNodes:
                data=self.getData(n)
                
                if data['type']==type:
                    validNodes.append(n)
                
                #if user wants the whole hierarchy
                if all==True:
                    if (self.downStream(n,type,all=all))!=None:
                        for m in (self.downStream(n,type,all=all)):
                            validNodes.append(m)
            
            return validNodes
    
    def getHierarchies(self):
        hierarchies={}
        hierarchies['None']=[]
        
        for node in cmds.ls(type='network'):
            data=self.getData(node)
            
            if data['metaParent']==None:
                hierarchies['None'].append(node)
            
            if cmds.listConnections('%s.message' % node,type='network')>0:
                hierarchies[node]=[]
                
                for child in cmds.listConnections('%s.message' % node,type='network'):
                    hierarchies[node].append(child)
        
        return hierarchies