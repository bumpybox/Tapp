import maya.cmds as cmds
import maya.mel as mel
import os
from shutil import move
import sys
from xml.dom.minidom import Document,parse,parseString

braDir=os.path.dirname(__file__)

braVersion='1.0.1'

def createCharacter():
    #getting files
    basicFilter = "Template (*.template)"
    templateFile=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,fileMode=1,caption='Open Template File')
    
    if templateFile!=None:
        basicFilter = "Controls (*.controls)"
        controlsFile=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,fileMode=1,caption='Open Controls File')
        
        basicFilter = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
        proxyFile=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,fileMode=1,caption='Open Proxy File')
        
        basicFilter = "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)"
        geoFile=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,fileMode=1,caption='Open Geometry File')
        
        if geoFile!=None:
            basicFilter = "Weightmap (*.weightmap)"
            weightFiles=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,fileMode=4)
    
    #creating character
    if templateFile!=None:
        cmds.file(templateFile,i=True,defaultNamespace=True)
        createRig()
        hideRig()
        blackboxRig()
        
        #importing control shapes
        if controlsFile!=None:
            importControlShapes(controlsFile)
        
        #importing proxies
        if proxyFile!=None:
            temp=os.path.splitext(os.path.basename(proxyFile[0]))[0]
            proxyNodes=cmds.file(proxyFile,reference=True,returnNewNodes=True,namespace=temp)
            cmds.select(cl=True)
            cmds.select(proxyNodes)
            proxyParent()
        
        #importing geometry
        if geoFile!=None:
            temp=os.path.splitext(os.path.basename(geoFile[0]))[0]
            geoNodes=cmds.file(geoFile,reference=True,returnNewNodes=True,namespace=temp)
            cmds.select(cl=True)
            cmds.select(geoNodes)
            
            grp=cmds.group(name='geo')
            cmds.setAttr('%s.overrideEnabled' % grp,1)
            cmds.setAttr('%s.overrideDisplayType' % grp,2)
            
            if weightFiles!=None:
                for f in weightFiles:
                    #correcting filename
                    f=f.replace('\\','/')
                    
                    #importing skin maps
                    importWeightMap(f)
''' NOT WORKING
def importWeightMap(fileName):
    #reading weightmap
    f=open(fileName,'r')
    
    #getting data from file
    fData=f.read()
    
    fLines=fData.split('\n')
    
    del fLines[0]
    del fLines[0]
    
    newLines=list()
    for line in fLines:
        newLines.append(line.split('\r'))
        
    print newLines
    
    data=list()
    for line in newLines:
        data.append(line[0].split('\t'))
    
    del data[len(data)-1]
    
    geo=data[0][0]
    
    joints=list()
    for i in data:
        joints.append(i[1])
    
    #applying skin to geo
    cmds.select(geo)
    mel.eval('DeleteHistory;')
    cmds.skinCluster( joints, geo,)
    
    #importing weightmap
    cmds.select(geo)
    mel.eval('braImportSkin("'+fileName+'","weightmap");')
'''

def proxyParent():
    #defining joints
    joints=list()
    for node in cmds.ls(type='network'):
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='joint' and (cmds.getAttr('%s.system' % node))=='skin':
            jnt=cmds.listConnections('%s.message' % node,type='transform')
            
            joints.append(jnt)
    
    collGRP=cmds.group(em=True,name='proxy_grp')
    cmds.setAttr('%s.overrideEnabled' % collGRP,1)
    cmds.setAttr('%s.overrideDisplayType' % collGRP,2)
    
    #looping through proxy objects and parenting to joints
    for node in cmds.ls(type='network'):
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='mesh' and (cmds.attributeQuery('system',n=node,ex=True))==True and (cmds.getAttr('%s.system' % node))=='proxy':
            proxy=cmds.listConnections('%s.message' % node,type='transform')
            
            proxyGRP=cmds.group(em=True,name=(str(proxy[0])+'_grp'))
            cmds.delete(cmds.parentConstraint(proxy,proxyGRP))
            
            dist=list()
            
            #joints loop
            for m in range(0,len(joints)):
                dist.append(distance(proxyGRP,joints[m]))
            
            jnt=joints[dist.index(min(dist))]
            
            cmds.delete(cmds.orientConstraint(jnt,proxyGRP))
            
            cmds.parent(proxy,proxyGRP)
            
            cmds.parentConstraint(jnt,proxyGRP,maintainOffset=True)
            cmds.connectAttr('%s.scale' % jnt[0],'%s.scale' % proxyGRP,force=True)
            
            cmds.parent(proxyGRP,collGRP)

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

def importControlShapes(fileName):   
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

def deleteTemplate():
    if len(cmds.ls( selection=True ))>0:
        
        for sel in cmds.ls( selection=True ):
            metaNode=cmds.listConnections('%s.metaParent' % sel)
            module=cmds.listConnections('%s.metaParent' % metaNode[0])
            
            for node in cmds.listConnections('%s.message' % module[0]):
                if (cmds.attributeQuery('component',n=node,ex=True))==True and (cmds.getAttr('%s.component' % node))=='root':
                    for subNode in cmds.listConnections('%s.message' % node):
                        if (cmds.nodeType(subNode)=='transform'):
                            root=subNode
            
            cmds.delete(root)
    else:
        raise RuntimeError, 'Nothing is selected!'

def mirrorTemplate():
    if len(cmds.ls( selection=True ))>0:
        for sel in cmds.ls( selection=True ):
            metaNode=cmds.listConnections('%s.metaParent' % sel)
            module=cmds.listConnections('%s.metaParent' % metaNode[0])
            
            networkNodes=list()
            for node in cmds.listConnections('%s.message' % module[0]):
                if cmds.nodeType(node)=='network':
                    networkNodes.append(node)
            
            moduleType=cmds.getAttr('%s.component' % module[0])
            moduleType+='.template'
            
            directory=braDir+'/templates'
            print directory
            
            templates = []
            for root, dirs, files in os.walk(directory):
                for name in files:
                    path = os.path.join(root, name)
                    if name.endswith('.template'):
                        templates.append(name)
            
            importNodes=list()
            for item in templates:
                if item==moduleType:
                    importNodes=cmds.file((directory+'/'+item),i=True,returnNewNodes=True,defaultNamespace=True)
            
            for node in importNodes:
                if cmds.nodeType(node)=='network':
                    if (cmds.getAttr('%s.type' % node))=='control':
                        for item in networkNodes:
                            if (cmds.attributeQuery('component',n=item,ex=True))==True and (cmds.getAttr('%s.component' % item))==(cmds.getAttr('%s.component' % node)):
                                original=cmds.listConnections('%s.message' % item,type='transform')
                                target=cmds.listConnections('%s.message' % node,type='transform')
                                
                                print 'item:'
                                print item
                                print 'original:'
                                print original
                                print 'target:'
                                print target
                                
                                cmds.copyAttr(original[0],target[0],values=True)
                                
                                if cmds.getAttr('%s.rotateX' % original[0],lock=True)==False:
                                    originalRot=cmds.xform(original,q=True,ws=True,ro=True)
                                    cmds.xform(target[0],ws=True,ro=(0,(originalRot[1]*-1),(originalRot[2]*-1)))
                                    
                                    cmds.delete(cmds.orientConstraint(original,target,skip=('y','z')))
                                    
                                    cmds.rotate(0,180,0,target[0],os=True,r=True)
                                
                                if (cmds.getAttr('%s.tx' % target[0],lock=True))!=True:
                                    originalPos=cmds.xform(original,q=True,ws=True,translation=True)
                                    cmds.xform(target[0],ws=True,translation=((originalPos[0]*-1),originalPos[1],originalPos[2]))
                        
    else:
        raise RuntimeError, 'Nothing is selected!'

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

def connectPlugs():
    if len(cmds.ls( selection=True ))>1:
        #collecting plugs
        plugs=list()
        sockets=list()
        modules=list()
        
        #selection loop
        for sel in cmds.ls( selection=True ):
            #getting module
            metaNode=cmds.listConnections('%s.metaParent' % sel)
            module=cmds.listConnections('%s.metaParent' % metaNode[0])
            
            modules.append(module)
            
            #getting plug and socket
            for node in cmds.listConnections('%s.message' % module[0]):
                if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='plug':
                    #plug
                    plug=cmds.listConnections('%s.message' % node,type='transform')[0]
                    plugs.append(plug)
                    
                if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='socket':
                    #socket
                    socket=cmds.listConnections('%s.message' % node,type='transform')[0]
                    sockets.append(socket)
        
        #plug loop
        print plugs
        print sockets
        for i in range(0,len(plugs)-1):
            #removing previous constraints
            cmds.delete(plugs[i],constraints=True)
            
            dist=[]
            
            #socket loop
            for m in range(0,len(sockets)):
                dist.append(distance(plugs[i],sockets[m]))
                
            #getting socket and socket module
            socket=sockets[dist.index(min(dist))]
            
            metaSocket=(cmds.listConnections('%s.metaParent' % socket))[0]
            socketModule=(cmds.listConnections('%s.metaParent' % metaSocket))[0]
            
            #connecting plug and socket
            cmds.parentConstraint(socket,plugs[i],maintainOffset=True)
            cmds.scaleConstraint(socket,plugs[i])
            
            cmds.connectAttr('%s.message' % socketModule,'%s.metaParent' % modules[i][0],force=True)

def createRig():
    #creating root
    rootNode=0
    for m in (cmds.ls(type='network')):
            if (cmds.getAttr('%s.type' % m))=='root':
                rootNode=1
    if rootNode==0:
        root=cmds.shadingNode('network',asUtility=True,name='meta_root')
        cmds.addAttr(root,longName='type',dataType='string')
        cmds.setAttr('%s.type' % root,'root',type='string')
        cmds.addAttr(root,longName='version',dataType='string')
        cmds.setAttr('%s.version' % root,braVersion,type='string')
        cmds.addAttr(root,longName='metaParent',attributeType='message')
        
        metaWorld=cmds.shadingNode('network',asUtility=True,name='meta_world_cnt')
        cmds.addAttr(metaWorld,longName='type',dataType='string')
        cmds.setAttr('%s.type' % metaWorld,'control',type='string')
        cmds.addAttr(metaWorld,longName='component',dataType='string')
        cmds.setAttr('%s.component' % metaWorld,'world',type='string')
        cmds.addAttr(metaWorld,longName='metaParent',attributeType='message')
        
        metaWorldSocket=cmds.shadingNode('network',asUtility=True,name='meta_worldSocket')
        cmds.addAttr(metaWorldSocket,longName='type',dataType='string')
        cmds.setAttr('%s.type' % metaWorldSocket,'socket',type='string')
        cmds.addAttr(metaWorldSocket,longName='component',dataType='string')
        cmds.setAttr('%s.component' % metaWorldSocket,'world',type='string')
        cmds.addAttr(metaWorldSocket,longName='metaParent',attributeType='message')
        
        worldCNT=cmds.circle(radius=5,name='world_cnt',constructionHistory=False)
        cmds.addAttr(worldCNT,longName='metaParent',attributeType='message')
        cmds.rotate(90,0,0,'world_cnt.cv[0:7]',relative=True,pivot=(0,0,0),objectSpace=True)
        
        worldSocket=cmds.spaceLocator(name='worldSocket')[0]
        cmds.addAttr(worldSocket,longName='metaParent',attributeType='message')
        cmds.parent(worldSocket,worldCNT[0])
        
        cmds.connectAttr('%s.message' % metaWorld,'%s.metaParent' % worldCNT[0])
        cmds.connectAttr('%s.message' % metaWorldSocket,'%s.metaParent' % worldSocket) 
        cmds.connectAttr('%s.message' % root,'%s.metaParent' % metaWorld)
        cmds.connectAttr('%s.message' % root,'%s.metaParent' % metaWorldSocket)
        
        cmds.select(worldCNT)
        cmds.group(n='world_cnt_SN')
        cmds.group(n='world_cnt_PH')
    
    #getting module amount
    templateModules=list()
    for m in (cmds.ls(type='network')):
            if (cmds.getAttr('%s.type' % m))=='module' and (cmds.getAttr('%s.system' % m))=='template':
                templateModules.append(m)
    
    #executing the script data
    if len(templateModules)==0:
        raise RuntimeError, 'There are no templates found in the scene!'
    else:
        directory=braDir+'/templates'
        
        scriptsToExecute=list()
        
        for node in templateModules:
            component=cmds.getAttr('%s.component' % node)
            component+='.mel'
            
            scriptsToExecute.append(component)
        
        for script in scriptsToExecute:
            scripts=list()
            for root, dirs, files in os.walk(directory):
                for name in files:
                    path = os.path.join(root, name)
                    if name.endswith('.mel'):
                        scripts.append(name)
            
            for item in scripts:
                if item==script:
                    f=open(directory+'/'+script)
                    fData=f.read()
                    f.close()
                    
                    print ('Executing '+script)
                    mel.eval(fData)
    
    #clearing out scriptnodes
    for m in (cmds.ls(type='script')):
            cmds.delete(m)
    
    #connecting modules and ik controls to world control
    for m in (cmds.ls(type='network')):
        if (cmds.getAttr('%s.type' % m))=='module':
            for i in cmds.listConnections('%s.message' % m,type='network'):
                
                #getting all non spine plugs and connecting to nearest socket
                if (cmds.getAttr('%s.type' % i))=='plug' and (cmds.getAttr('%s.component' % i))!='spine':
                    obj=[]
                    dist=[]
                    distSort=[]
                    
                    #adding world socket to objs
                    obj.append(worldSocket)
                    dist.append(distance(worldSocket,(cmds.listConnections('%s.message' % i))[0]))
                    distSort.append(distance(worldSocket,(cmds.listConnections('%s.message' % i))[0]))
                    
                    #finding distances to sockets
                    for o in (cmds.ls(type='network')):
                        if (cmds.getAttr('%s.type' % o))=='module' and o!=m:
                            for k in cmds.listConnections('%s.message' % o,type='network'):
                                if (cmds.getAttr('%s.type' % k))=='socket':
                                    objK=(cmds.listConnections('%s.message' % k))[0]
                                    obj.append(objK)
                                    objI=(cmds.listConnections('%s.message' % i))[0]
                                    dist.append(distance(objK,objI))
                                    distSort.append(distance(objK,objI))
                    
                    #sorting dist list
                    distSort.sort()
                    
                    #if sockets are present > parent to world
                    if len(obj)!=0:
                        #establish plug
                        plug=(cmds.listConnections('%s.message' % i))[0]
                        
                        parentCheck=False
                        for x in range(0,len(obj)):
                            #getting socket data
                            socket=str(obj[dist.index(distSort[x])])
                            
                            metaSocket=(cmds.listConnections('%s.metaParent' % socket))[0]
                            socketModule=(cmds.listConnections('%s.metaParent' % metaSocket))[0]
                            
                            if (cmds.listConnections('%s.metaParent' % socketModule))==None and parentCheck==False:
                                #parenting to nearest socket
                                cmds.parentConstraint(socket,plug,maintainOffset=True)
                                cmds.scaleConstraint(socket,plug)
                                
                                cmds.connectAttr('%s.message' % socketModule,'%s.metaParent' % m,force=True)
                                
                                parentCheck=True
                    else:
                        plug=(cmds.listConnections('%s.message' % i))[0]
                        cmds.parentConstraint(worldSocket,plug,maintainOffset=True)
                        cmds.scaleConstraint(worldSocket,plug)
                
                #getting all spine plugs and connecting to world socket
                if (cmds.getAttr('%s.type' % i))=='plug' and (cmds.getAttr('%s.component' % i))=='spine':
                    plug=(cmds.listConnections('%s.message' % i))[0]
                    cmds.parentConstraint(worldSocket,plug,maintainOffset=True)
                    cmds.scaleConstraint(worldSocket,plug)
                    
                    metaSocket=(cmds.listConnections('%s.metaParent' % worldSocket))[0]
                    socketModule=(cmds.listConnections('%s.metaParent' % metaSocket))[0]
                    
                    cmds.connectAttr('%s.message' % socketModule,'%s.metaParent' % m,force=True)
                
                #getting all ik plugs and connecting to world socket
                if (cmds.getAttr('%s.type' % i))=='control' and (cmds.attributeQuery('system',n=i,ex=True))==True and (cmds.getAttr('%s.system' % i))=='ik' and (cmds.attributeQuery('worldspace',n=i,ex=True))==False:
                    cnt=cmds.listConnections('%s.message' % i)
                    snGroup=cmds.listRelatives(cnt[0],parent=True)
                    phGroup=cmds.listRelatives(snGroup[0],parent=True)
                    parentGroup=cmds.listRelatives(phGroup[0],parent=True)
                    print cnt[0]
                    try:
                        cmds.parentConstraint(worldSocket,parentGroup[0],maintainOffset=True)
                        cmds.scaleConstraint(worldSocket,parentGroup[0])
                    except:
                        print '%s could not be connected to world socket.' % cnt[0]
    
    colorRig()
    
def colorRig():
    for node in cmds.ls(type='network'):
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='root':
            for meta in cmds.listConnections('%s.message' % node,type='network'):
                if (cmds.attributeQuery('type',n=meta,ex=True))==True and (cmds.getAttr('%s.type' % meta))=='control':
                    cnt=cmds.listConnections('%s.message' % meta,type='transform')[0]
                    
                    cmds.setAttr('%s.overrideEnabled' % cnt,1)
                    cmds.setAttr('%s.overrideColor' % cnt,17)
        
        if (cmds.attributeQuery('type',n=node,ex=True))==True and (cmds.getAttr('%s.type' % node))=='module':
            side=cmds.getAttr('%s.side' % node)
            
            for meta in cmds.listConnections('%s.message' % node,type='network'):
                if (cmds.attributeQuery('type',n=meta,ex=True))==True and (cmds.getAttr('%s.type' % meta))=='control':
                    cnt=cmds.listConnections('%s.message' % meta,type='transform')[0]
                    
                    cmds.setAttr('%s.overrideEnabled' % cnt,1)
                    
                    if side=='c':
                        cmds.setAttr('%s.overrideColor' % cnt,6)
                    if side=='r':
                        cmds.setAttr('%s.overrideColor' % cnt,13)
                    if side=='l':
                        cmds.setAttr('%s.overrideColor' % cnt,14)

def browsePath():
    templatePath=cmds.fileDialog2(dialogStyle=1,fileMode=3)
    cmds.textField('raPathLineEdit',edit=True,text=templatePath[0])
    refreshList()
        
def refreshList():
    directory=cmds.textField('raPathLineEdit',query=True,text=True)
    
    templates = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            if name.endswith('.template'):
                templates.append(name)
    
    cmds.textScrollList('raTemplateScollList',edit=True,removeAll=True)
    for item in templates:
        cmds.textScrollList('raTemplateScollList',edit=True,append=item)
            
def importTemplate():
    items=cmds.textScrollList('raTemplateScollList',query=True,selectItem=True)

    #Error checking for zero items
    if items==None:
        raise RuntimeError, 'Nothing is selected to import!'
    
    for item in items:
        directory=cmds.textField('raPathLineEdit',query=True,text=True)
        cmds.file((directory+'/'+item),i=True,defaultNamespace=True)
        
def exportTemplate():
    basicFilter = "Template (*.template)"
    fileName=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1)
    if fileName!=None:
        templateNodes=list()
        
        for node in cmds.ls(type='network'):
            if (cmds.attributeQuery('system',n=node,ex=True))==True and (cmds.getAttr('%s.system' % node))=='template':
                templateNodes.append(node)
            
            for child in cmds.listConnections(node):
                if cmds.nodeType(child)=='transform':
                    templateNodes.append(child)
        
        cmds.select(templateNodes)
        newFileName=cmds.file(fileName[0],exportSelected=True,type='mayaAscii')
        move(newFileName,(os.path.splitext(newFileName)[0]))
        cmds.select(cl=True)
    refreshList()