import operator

import maya.cmds as cmds

def Filter(objects,filterData):
    ''' Filters objects based on a dictionary.
        objects is a list of nodes.
        filterData is a dictionary,
            eg {'system':'fk','index':'1'}
        Returns a list of valid nodes.
    '''
    
    objs=[]
    
    for obj in objects:
        data=GetData(obj)
        
        shared_item = set(data.items()) & set(filterData.items())
        if len(shared_item)==len(filterData):
            objs.append(obj)
    
    return objs

def Sort(objects,attr):
    ''' Sorts objects based on a value attribute.
        objects is a list of objects.
        attr is the attribute to sort by.
        Returns a list. 
    '''
    
    objs={}
    
    for obj in objects:
        data=GetData(obj)
        
        if attr in data:
            objs[obj]=float(data[attr])
    
    sortedList=sorted(objs.iteritems(),
                      key=operator.itemgetter(1))
    
    sortedObjs=[]
    
    for item in sortedList:
        sortedObjs.append(item[0])
    
    #return
    return sortedObjs

def ModifyData(node,data):
    ''' Modify data on existing nodes.
        data is a dictionary.
        node is a transform or meta node.
    '''
    
    if cmds.nodeType(node)=='transform':
        
        #getting meta node
        mNode=GetMetaNode(node)
        
        __modifyData__(mNode, data)
    
    if cmds.nodeType(node)=='network':
        
        __modifyData__(node, data)

def __modifyData__(mNode,data):
    ''' Support function for ModifyData. '''
    
    mData=GetData(mNode)
    
    for attr in data:
        
        #checking existance of attribute
        if attr in mData.keys():
            
            if attr=='metaParent' or attr=='switch':
                cmds.connectAttr(data[attr]+'.message',
                                 mNode+'.'+attr,
                                 force=True)
            else:
                cmds.setAttr(mNode+'.'+attr,str(data[attr]),
                             type='string')
        elif attr=='metaParent' or attr=='switch':
            cmds.addAttr(mNode,longName=attr,
                         attributeType='message')
            cmds.connectAttr(data[attr]+'.message',
                             mNode+'.'+attr,
                             force=True)
        else:
            cmds.addAttr(mNode,longName=attr,
                         dataType='string')
            cmds.setAttr('%s.%s' % (mNode,attr),data[attr],
                         type='string')

def SetData(name,nodeType,component,metaParent,data):
    ''' Create a network node with the requested data 
        data should be passed in as a dictionary
    '''
    
    #create network node
    node=cmds.shadingNode( 'network',asUtility=True, n=name)
    
    #add base data
    cmds.addAttr(node,longName='type',dataType='string')
    if nodeType!=None:
        cmds.setAttr('%s.type' % node,nodeType,type='string')
    
    if component!=None:
        cmds.addAttr(node,longName='component',
                     dataType='string')
        
        cmds.setAttr('%s.component' % node,component,
                     type='string')
    
    cmds.addAttr(node,longName='metaParent',
                 attributeType='message')
    if metaParent!=None:           
        cmds.connectAttr('%s.message' % metaParent,
                         '%s.metaParent' % node)
    
    #add extra data
    if data!=None:
        for attr in data:
            if attr=='switch':
                cmds.addAttr(node,longName=attr,
                             attributeType='message')
                cmds.connectAttr('%s.message' % data[attr],
                                 '%s.switch' % node)
            else:
                cmds.addAttr(node,longName=attr,
                             dataType='string')
                cmds.setAttr('%s.%s' % (node,attr),data[attr],
                             type='string')
    
    return node

def SetTransform(node,metaParent):
    ''' Create an metaParent attribute on the passed transform,
        and connect to the passed meta node.'''
    
    attrList=cmds.attributeInfo(node,
                                all=True)
    
    if 'metaParent' not in attrList:
        cmds.addAttr(node,longName='metaParent',
                     attributeType='message')
        cmds.connectAttr('%s.message' % metaParent,
                         '%s.metaParent' % node)
    else:
        cmds.connectAttr('%s.message' % metaParent,
                         '%s.metaParent' % node,force=True)

def GetTransform(node):
    ''' Returns the transform node attached to a meta node. '''
    
    return cmds.listConnections('%s.message' % node,
                                type='transform')[0]

def GetMetaNode(node):
    ''' Returns the meta mode attached to a transform node. '''
    
    return cmds.listConnections('%s.metaParent' % node,
                                type='network')[0]

def GetData(node,stripNamespace=True):
    ''' Returns the meta data as a dictionary for
        the requested node. 
    '''
    
    #making sure we get a network node
    if cmds.nodeType(node)!='network':
        metaNode=cmds.listConnections(node+'.metaParent')[0]
    else:
        metaNode=node
    
    #setting data variables
    attrList=cmds.attributeInfo(metaNode,all=True)
    data={}
    
    if stripNamespace:
        name=str(metaNode).split(':')[-1]
        data['name']=name
    else:
        data['name']=str(metaNode)
    
    #looping through custom attributes
    for count in range(7,len(attrList)):
        
        attr=attrList[count]
        
        if cmds.getAttr('%s.%s' % (metaNode,attr),
                        type=True)=='enum':               
            data[str(attr)]=str(cmds.getAttr(metaNode+'.'+attr,
                                    asString=True))
        
        if cmds.getAttr('%s.%s' % (metaNode,attr),
                        type=True)!='enum' and\
                         cmds.getAttr(metaNode+'.'+attr,
                                      type=True)!='message':
            data[str(attr)]=str(cmds.getAttr(metaNode+'.'+attr))
        
        if cmds.getAttr(metaNode+'.'+attr,
                        type=True)=='message':
            
            #query whether message attribute is connected
            if cmds.listConnections(metaNode+'.'+attr)==None:
                data[str(attr)]=None
            else:
                metaParent=cmds.listConnections(metaNode+
                                                '.'+attr)[0]
                
                if stripNamespace:
                    name=str(metaParent).split(':')[-1]
                    data[str(attr)]=name
                else:
                    data[str(attr)]=str(metaParent)
    
    return data

def UpStream(node,nodeType):
    ''' Returns the parent node with the requested nodeType. '''
    
    upStreamNode=None
    data=GetData(node)
    
    if data['type']!=nodeType:
        if cmds.listConnections(node+'.metaParent')!=None:
            upStreamNode=UpStream(cmds.listConnections\
                                       (node+'.metaParent')[0],
                                       nodeType)
    
    if data['type']==nodeType:
        upStreamNode=node
    
    return upStreamNode

def DownStream(node,nodeType,allNodes=False):
    ''' Returns allNodes nodes down the hierarchy with 
        the requested nodeType. 
    
        If allNodes=True, nodes further down the hierarchy 
        is returned as well.
    '''
    
    childNodes=cmds.listConnections('%s.message' % node,
                                    type='network')
    
    validNodes=[]
    
    if childNodes!=None:
        for n in childNodes:
            data=GetData(n)
            
            if data['type']==nodeType:
                validNodes.append(n)
            
            #if user wants the whole hierarchy
            if allNodes==True:
                if (DownStream(n,nodeType,
                                    allNodes=allNodes))!=None:
                    for m in (DownStream(n,nodeType,
                                              allNodes=\
                                              allNodes)):
                        validNodes.append(m)
        
        return validNodes

def Compare(dictA,dicts):
    ''' Compares one dict to multiple dicts.
        dicts have should be of following construct:
            {#NODE#:{#NODE DATA#}}
        
        returns the dict that shares the most values,
        with dictA.
    '''
    
    validNodes={}
    
    for key in dicts:
        
        validNodes[key]=__compare__(dictA,dicts[key])
    
    closestNode=max(validNodes, key=validNodes.get)
    
    return [closestNode,validNodes[closestNode]]

def __compare__(dictA,dictB):
    ''' Compares dictA with dictB.
    
        returns a percentage of values shared.
    '''
    
    sharedKeys=[]
    
    for keyA in dictA:
        for keyB in dictB:
            if keyA==keyB:
                sharedKeys.append(keyA)
    
    sharedData=0.0
    
    for key in sharedKeys:
        if dictA[key]==dictB[key]:
            sharedData+=1.0
    
    sharePercent=sharedData/len(dictA)*100
    
    return sharePercent

def GetControlData(node,stripNamespace=True):
    ''' Returns control data.
    '''
    
    #return variable
    data={}
    
    if (cmds.attributeQuery('metaParent',n=node,ex=True))==True:
        
        #getting control data
        data=GetData(node,stripNamespace=stripNamespace)
        
        if data['type']=='control':
        
            #adding module data
            module=UpStream(node, 'module')
            mData=GetData(module)
            data['module_side']=mData['side']
            data['module']=mData['component']
            data['module_index']=mData['index']
            data['module_subcomponent']=mData['subcomponent']
            
            #adding root data
            root=UpStream(node, 'root')
            rData=GetData(root)
            data['root_asset']=rData['asset']
            
            #getting transform data
            if stripNamespace:
                data['transform']=str(node).split(':')[-1]
            else:
                data['transform']=str(node)
        else:
            
            return None
    else:
        cmds.warning(node+' is not part of the meta system!')
        
        return None
    
    #return
    return data