import maya.cmds as cmds
import maya.mel as mel
import os
from shutil import move
import sys
from xml.dom.minidom import Document,parse,parseString

def distance( objA, objB ):
    from math import sqrt,pow
    
    At=cmds.xform(objA,ws=True,q=True,t=True)
    Ax=At[0]
    Ay=At[1]
    Az=At[2]
    
    Bt=cmds.xform(objB,ws=True,q=True,t=True)
    Bx=Bt[0]
    By=Bt[1]
    Bz=Bt[2]
 
    return sqrt(  pow(Ax-Bx,2) + pow(Ay-By,2) + pow(Az-Bz,2)  )

def exportControlShapes():
    #getting file path and name
    basicFilter = "Controls (*.controls)"
    fileName=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,caption='Open Controls File')
    
    #network loop
    exportNodes=list()
    modulesCopy=list()
    for node in cmds.ls(type='network'):
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='control':
            #copying module
            module=cmds.listConnections('%s.metaParent' % node)
            
            moduleCopy=cmds.duplicate(module,parentOnly=True)
            
            modulesCopy.append(moduleCopy)
            
            #getting metaNode
            childNodes=cmds.listConnections('%s.message' % node)
            
            #copying control
            for childNode in childNodes:
                if cmds.nodeType(childNode)=='transform':
                    #copy control node
                    cntCopy=cmds.duplicate(childNode,returnRootsOnly=True,renameChildren=True)
                    
                    #parent control to world
                    temp=cmds.listRelatives(childNode,parent=True)
                    if temp!=None:
                        cmds.parent(cntCopy,world=True)
                    
                    #deleting all non shapes children
                    temp=cmds.listRelatives(cntCopy,children=True)
                    for child in temp:
                        if cmds.nodeType(child)!='nurbsCurve':
                            cmds.delete(child)
                    
                    #copy and connect metaParent
                    metaParentCopy=cmds.duplicate(node,parentOnly=True)
                    
                    cmds.connectAttr('%s.message' % metaParentCopy[0],'%s.metaParent' % cntCopy[0],force=True)
                    
                    #connect metaParent to module
                    cmds.connectAttr('%s.message' % moduleCopy[0],'%s.metaParent' % metaParentCopy[0],force=True)
                    
                    #add control node to export list
                    exportNodes.append(cntCopy)
    
    #exporting nodes
    cmds.select(clear=True)
    for node in exportNodes:
        cmds.select(node,add=True)
    
    if fileName!=None:
        newFileName=cmds.file(fileName[0],exportSelected=True,type='mayaAscii')
        move(newFileName,(os.path.splitext(newFileName)[0]))
    
    #delete copied nodes
    for node in exportNodes:
        cmds.delete(node)
    
    for node in modulesCopy:
        cmds.delete(node)

def importControlShapes():
    #getting file path and name
    basicFilter = "Controls (*.controls)"
    fileName=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,fileMode=1)
    
    #existing control nodes
    moduleNodes=list()
    
    for node in cmds.ls(type='network'):
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='module':
            moduleNodes.append(node)
                    
    #importing nodes
    importNodes=cmds.file(fileName,i=True,returnNewNodes=True)
    
    #importNodes loop
    for node in importNodes:
        
        #getting module
        if cmds.nodeType(node)=='network' and (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='module':
            module=node
            
            #getting shape node
            for subNode in cmds.listConnections('%s.message' % module):
                if cmds.nodeType(subNode)=='network':
                    metaNode=subNode
                    
                    for child in cmds.listConnections('%s.message' % metaNode):
                        if cmds.nodeType(child)=='transform':
                            controlNode=child
                            
                            shapeNode=cmds.listRelatives(controlNode,shapes=True)
            
            print metaNode
            
            #finding corresponding control node
            for i in moduleNodes:
                if (cmds.getAttr('%s.component' % i))==(cmds.getAttr('%s.component' % module)) and (cmds.getAttr('%s.index' % i))==(cmds.getAttr('%s.index' % module)) and (cmds.getAttr('%s.side' % i))==(cmds.getAttr('%s.side' % module)):
                    
                    origModule=i
                    metaNodeList=list()
                    origMetaNode=None
                    
                    for o in cmds.listConnections('%s.message' % origModule,type='network'):
                        if (cmds.getAttr('%s.type' % o))=='control' and (cmds.getAttr('%s.component' % o))==(cmds.getAttr('%s.component' % metaNode)):
                            metaNodeList.append(o)
                    
                    print 'candidates:'
                    print metaNodeList
                    
                    if len(metaNodeList)>1:
                        for o in metaNodeList:
                            if (cmds.attributeQuery('system',n=o,ex=True))==True and (cmds.getAttr('%s.system' % o))==(cmds.getAttr('%s.system' % metaNode)) and (cmds.getAttr('%s.index' % o))==(cmds.getAttr('%s.index' % metaNode)):
                                origMetaNode=o
                    else:
                        origMetaNode=metaNodeList[0]
                    
                    print 'candidate:'
                    print origMetaNode
                    print '-------------'
                    if origMetaNode!=None:
                        #getting shape node
                        origControlNode=cmds.listConnections('%s.message' % origMetaNode,type='transform')[0]
                        
                        origShapeNode=cmds.listRelatives(origControlNode,shapes=True)[0]
                        
                        #delete original shape node
                        tempGroup=cmds.createNode( 'transform', ss=True )
                        
                        cmds.parent(origShapeNode,tempGroup,absolute=True,shape=True)
                        
                        cmds.delete(tempGroup)
                        
                        print shapeNode
                        print origControlNode
                        
                        #adding new shape node
                        cmds.parent(shapeNode,origControlNode,add=True,shape=True)
    
    #removing imported nodes
    transformNodes=list()
    moduleNodes=list()
    
    tempNetwork=cmds.shadingNode('network',asUtility=True)
    
    for node in importNodes:
        if cmds.nodeType(node)=='transform':
            transformNodes.append(node)
        if cmds.nodeType(node)=='network':
            cmds.connectAttr('%s.message' % tempNetwork,'%s.metaParent' % node,force=True)
    
    for node in transformNodes:
        cmds.delete(node)
    
    cmds.delete(tempNetwork)

def hideRig():
    for node in cmds.ls():
        if cmds.nodeType(node)=='nurbsCurve':
            p=cmds.listRelatives(node,p=True)[0]
            if (cmds.attributeQuery('metaParent',n=p,ex=True))==False:
                cmds.setAttr('%s.visibility' % node,False)
        if cmds.nodeType(node)=='locator':
            cmds.setAttr('%s.visibility' % node,False)
        if cmds.nodeType(node)=='ikHandle':
            cmds.setAttr('%s.visibility' % node,False)
        if cmds.nodeType(node)=='joint':
            cmds.setAttr('%s.drawStyle' % node,2)

def unhideRig():
    for node in cmds.ls():
        if cmds.nodeType(node)=='nurbsCurve':
            p=cmds.listRelatives(node,p=True)[0]
            if (cmds.attributeQuery('metaParent',n=p,ex=True))==False:
                cmds.setAttr('%s.visibility' % node,True)
        if cmds.nodeType(node)=='locator':
            cmds.setAttr('%s.visibility' % node,True)
        if cmds.nodeType(node)=='ikHandle':
            cmds.setAttr('%s.visibility' % node,True)
        if cmds.nodeType(node)=='joint':
            cmds.setAttr('%s.drawStyle' % node,0)

def unblackboxRig():
    for con in cmds.ls(type='container'):
        cmds.container(con,edit=True,removeContainer=True)

def blackboxRig():
    #create asset
    asset=cmds.container(name='rig')
    
    cmds.setAttr('%s.blackBox' % asset,1)
    
    #adding all dag nodes to asset
    for node in cmds.ls(dagObjects=True):
        if cmds.referenceQuery(node, isNodeReferenced=True )==0:
            if cmds.nodeType(node)=='ikHandle':
                cmds.container(asset,edit=True,addNode=node)
            if cmds.nodeType(node)=='joint':
                cmds.container(asset,edit=True,addNode=node)
            if cmds.nodeType(node)=='transform':
                if cmds.nodeType(cmds.listRelatives(node,shapes=True))!='camera':
                    cmds.container(asset,edit=True,addNode=node)
    
    #publishing control nodes
    for node in cmds.ls(type='network'):
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='control':
            cnt=cmds.listConnections(node,type='transform')[0]
            
            cmds.containerPublish(asset,publishNode=(cnt,''))
            cmds.containerPublish(asset,bindNode=(cnt,cnt))

def getHierarchy():
    modules=list()
    
    for meta in cmds.ls(type='network'):
        if (cmds.attributeQuery('type',n=meta,ex=True))==True and (cmds.getAttr('%s.type' % meta))=='root':
            modules.append(meta)
        if (cmds.attributeQuery('type',n=meta,ex=True))==True and (cmds.getAttr('%s.type' % meta))=='module':
            modules.append(meta)
    
    template=list()
    
    for module in modules:
        hierarchy=dict()
        
        hierarchy['parent']=module
        childList=list()
        
        for meta in cmds.listConnections('%s.message' % module,type='network'):
            if (cmds.getAttr('%s.type' % meta))=='module':
                childList.append(meta)
        
        hierarchy['child']=childList
        
        if len(childList)>0:
            template.append(hierarchy)
    
    return template

def exportHierarchy():
    #getting file path and name
    basicFilter = "Hierarchy (*.hierarchy)"
    fileName=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1)[0]
    
    #user cancel fail safe
    if fileName!=None:
        doc=Document()
        
        root_node=doc.createElement('hierarchy')
        doc.appendChild(root_node)
        
        for item in getHierarchy():
            #create parent element
            object_node=doc.createElement(item['parent'])
            root_node.appendChild(object_node)
            
            #create child elements
            for node in item['child']:
                child_node=doc.createElement(node)
                object_node.appendChild(child_node)
        
        xml_file=open(fileName,'w')
        xml_file.write(doc.toprettyxml())
        xml_file.close()

def importHierarchyButton():
    basicFilter = "Hierarchy (*.hierarchy)"
    fileName=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,fileMode=1)
    
    #user cancel fail safe
    if fileName!=None:
        importHierarchy(fileName)

def importHierarchy(fileName):
    #converting fileName to string
    fileName=fileName[0]
    
    #reading xml file
    f=open(fileName,'r')
    
    #getting data from file
    fData=f.read()
    
    #convert string to document
    doc=parseString(fData)
    root=doc.childNodes[0]
    
    #clearing current hierarchy
    for meta in cmds.ls(type='network'):
        if (cmds.attributeQuery('type',n=meta,ex=True))==True and (cmds.getAttr('%s.type' % meta))=='plug':
            plug=cmds.listConnections('%s.message' % meta,type='transform')[0]
            cmds.delete(plug,constraints=True)
        
        if (cmds.attributeQuery('type',n=meta,ex=True))==True and (cmds.getAttr('%s.type' % meta))=='module':
            metaParent=cmds.listConnections('%s.metaParent' % meta)[0]
            cmds.disconnectAttr('%s.message' % metaParent,'%s.metaParent' % meta)
        
    #building hierarchy from xml data
    for parentNode in root.childNodes:
        if parentNode.attributes!=None:
            #getting parent sockets
            sockets=list()
            
            for meta in cmds.listConnections('%s.message' % parentNode.tagName,type='network'):
                if (cmds.attributeQuery('type',n=meta,ex=True))==True and (cmds.getAttr('%s.type' % meta))=='socket':
                    socket=cmds.listConnections('%s.message' % meta,type='transform')[0]
                    sockets.append(socket)
            
            for childNode in parentNode.childNodes:
                if childNode.attributes!=None:
                    for meta in cmds.listConnections('%s.message' % childNode.tagName,type='network'):
                        if (cmds.attributeQuery('type',n=meta,ex=True))==True and (cmds.getAttr('%s.type' % meta))=='plug':
                            plug=cmds.listConnections('%s.message' % meta,type='transform')[0]
                            
                            if len(sockets)>1:
                                dist=[]
                                
                                #socket loop
                                for m in range(0,len(sockets)):
                                    dist.append(distance(plug,sockets[m]))
                                    
                                #getting socket and socket module
                                socket=sockets[dist.index(min(dist))]
                                
                                metaSocket=(cmds.listConnections('%s.metaParent' % socket))[0]
                                socketModule=(cmds.listConnections('%s.metaParent' % metaSocket))[0]
                                
                                #connecting plug and socket
                                cmds.parentConstraint(socket,plug,maintainOffset=True)
                                cmds.scaleConstraint(socket,plug)
                                
                                cmds.connectAttr('%s.message' % parentNode.tagName,'%s.metaParent' % childNode.tagName,force=True)
                            else:
                                #connecting plug and socket
                                cmds.parentConstraint(socket,plug,maintainOffset=True)
                                cmds.scaleConstraint(socket,plug)
                                
                                cmds.connectAttr('%s.message' % parentNode.tagName,'%s.metaParent' % childNode.tagName,force=True)