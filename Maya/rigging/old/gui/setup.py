import os
import sys
from shutil import move

import maya.cmds as cmds

import Tapp.Maya.rigging.modules as mrm
import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.config as mrc
import Tapp.utils.yaml as muy

def __importModule__(module,dirPath):
    f = module+'.py'
    d = dirPath
 
    toks = f.split( '.' )
    modname = toks[0]
 
    # Check if dirrectory is really a directory
    if( os.path.exists( d ) ):
 
    # Check if the file directory already exists in the sys.path array
        paths = sys.path
        pathfound = 0
        for path in paths:
            if(d == path):
                pathfound = 1
 
    # If the dirrectory is not part of sys.path add it
        if not pathfound:
            sys.path.append( d )
 
    # exec works like MEL's eval but you need to add in globals() 
    # at the end to make sure the file is imported into the global 
    # namespace else it will only be in the scope of this function
    exec ('import ' + modname+' as mrm') in globals()

def Connect():
    
    sel=cmds.ls(selection=True)
    
    #collecting modules
    modules=[]
    
    for node in sel:
        modules.append(mum.UpStream(node, 'module'))
    
    #connecting modules
    if len(modules)>1:
        
        childModules=modules[0:-1]
        parentModule=modules[-1]
        
        for module in childModules:
            
            #importing module
            data=mum.GetData(module)
            
            __importModule__(data['component'],mrc.config['modules'].replace('\\','/'))
            
            #attaching modules
            mrm.Attach(module, parentModule)
    else:
        cmds.warning('Not enough modules selected!')

def Hide():
    
    cmds.undoInfo(openChunk=True)
    
    nodes=[]
    
    for node in cmds.ls(type='network'):
        
        data=mum.GetData(node)
        if data['type']=='module':
            cnts=mum.DownStream(node, 'control')
            
            tn=mum.GetTransform(cnts[0])
            container=cmds.container(q=True,fc=tn)
            
            for obj in cmds.container(container,q=True,nodeList=True):
                nodes.append(obj)
    
    for node in nodes:
                
        if cmds.nodeType(node)=='transform':
            
            shape=cmds.listRelatives(node,shapes=True)
            if cmds.nodeType(shape)=='locator':
            
                cmds.setAttr('%s.visibility' % shape[0],False)
            
            if cmds.nodeType(shape)=='implicitBox':
                
                cmds.setAttr('%s.visibility' % shape[0],False)
                
        if cmds.nodeType(node)=='ikHandle':
            
            cmds.setAttr('%s.visibility' % node,False)
            
        if cmds.nodeType(node)=='cluster':
            
            p=cmds.listConnections(node+'.matrix')[0]
            cmds.setAttr('%s.visibility' % p,False)
            
        if cmds.nodeType(node)=='joint':
            
            cmds.setAttr('%s.drawStyle' % node,2)
    
    cmds.undoInfo(closeChunk=True)

def Unhide():
    
    cmds.undoInfo(openChunk=True)
    
    nodes=[]
    
    for node in cmds.ls(type='network'):
        
        data=mum.GetData(node)
        if data['type']=='module':
            cnts=mum.DownStream(node, 'control')
            
            tn=mum.GetTransform(cnts[0])
            container=cmds.container(q=True,fc=tn)
            
            for obj in cmds.container(container,q=True,nodeList=True):
                nodes.append(obj)
    
    for node in nodes:
                
        if cmds.nodeType(node)=='transform':
            
            shape=cmds.listRelatives(node,shapes=True)
            if cmds.nodeType(shape)=='locator':
            
                cmds.setAttr('%s.visibility' % shape[0],True)
                
        if cmds.nodeType(node)=='ikHandle':
            
            cmds.setAttr('%s.visibility' % node,True)
            
        if cmds.nodeType(node)=='cluster':
            
            p=cmds.listConnections(node+'.matrix')[0]
            cmds.setAttr('%s.visibility' % p,True)
            
        if cmds.nodeType(node)=='joint':
            
            cmds.setAttr('%s.drawStyle' % node,0)
    
    cmds.undoInfo(closeChunk=True)

def Unblackbox():
    
    for node in cmds.ls(type='container'):
        
        cmds.setAttr(node+'.blackBox',0)

def Blackbox():
    
    for node in cmds.ls(type='container'):
        
        cmds.setAttr(node+'.blackBox',1)

def CreateRoot():
    
    cmds.undoInfo(openChunk=True)
        
    sel=cmds.ls(selection=True)
    
    if len(sel)>0:
        
        if len(sel)>=1:
            
            module=mum.UpStream(sel[0], 'module')
            
            result = cmds.promptDialog(
                    title='Name of Asset',
                    message='Enter Name:',
                    button=['OK', 'Cancel'],
                    defaultButton='OK',
                    cancelButton='Cancel',
                    dismissString='Cancel')
            
            if result == 'OK':
                text = cmds.promptDialog(query=True, text=True)
                __createRoot__(text,module)
        else:
            cmds.warning('Multiple modules selected!\nPlease select only one.')
    else:
        cmds.warning('No modules selected!')
    
    cmds.undoInfo(closeChunk=True)

def __createRoot__(assetName,childModule):
    
    data={'asset':assetName}
    root=mum.SetData('meta_'+assetName, 'root', None, None, data)
    
    cmds.connectAttr(root+'.message',childModule+'.metaParent',force=True)

def SetWorld():
    ''' Sets the world for the selected modules. '''
    
    cmds.undoInfo(openChunk=True)
    
    sel=cmds.ls(selection=True)
    
    #collecting modules
    modules=[]
    
    for node in sel:
        modules.append(mum.UpStream(node, 'module'))
    
    #connecting modules
    #if no modules selected
    if len(modules)>1:
        
        #if two modules selected
        if len(modules)>2:
            
            childModules=modules[0:-1]
            parentModule=modules[-1]
            
            for module in childModules:
                
                #importing module
                data=mum.GetData(module)
                
                __importModule__(data['component'],mrc.config['modules'].replace('\\','/'))
                
                #setting world for modules
                mrm.SetWorld(module, parentModule)
        else:
            module=modules[0]
            parentModule=modules[-1]
            
            message='Only one child module selected.\nDo you want to set world on downstream modules?'
            reply=cmds.confirmDialog( title='Set World',
                                      message=message,
                                      button=['Yes','No'],
                                      defaultButton='Yes',
                                      cancelButton='No')
            
            if reply=='Yes':
                
                #importing module
                data=mum.GetData(module)
                
                __importModule__(data['component'],mrc.config['modules'].replace('\\','/'))
                
                #setting world for modules
                mrm.SetWorld(module, parentModule,downStream=True)
            else:
                
                #importing module
                data=mum.GetData(module)
                
                __importModule__(data['component'],mrc.config['modules'].replace('\\','/'))
                
                #setting world for modules
                mrm.SetWorld(module, parentModule)
    else:
        cmds.warning('Not enough modules selected!')
    
    cmds.undoInfo(closeChunk=True)

def __hierarchyData__(root):
    ''' Queries the hierarchy of the meta rig.
    
        returns dict with module name and metaParent info.
    '''
    
    modules=mum.DownStream(root, 'module', allNodes=True)
    modules.append(root)
    
    hierarchyData={}
    
    for module in modules:
        
        data=mum.GetData(module)
        
        moduleData={}
        
        moduleData['metaParent']=data['metaParent']
        
        hierarchyData[str(module)]=moduleData
    
    return hierarchyData

def HierarchyExport():
    ''' Exports hierarchy data to external hierarchy files. '''
    
    #getting root node
    root=None
    
    for node in cmds.ls(type='network'):
        
        data=mum.GetData(node)
        if data['type']=='root':
            
            root=node
    
    #root node checking
    if root!=None:
        
        #user input for filepath
        basicFilter = 'Hierarchy (*.hierarchy)'
        filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                                  caption='Export Hierarchy')
        
        #generating data
        data=__hierarchyData__(root)
        
        data['root']=mum.GetData(root)
        rootchild=mum.DownStream(root, 'module', allNodes=False)
        data['root']['child']=str(rootchild[0])
        
        #exporting hierarchy data
        f=open(filePath[0],'w')
        muy.dump(data, f)
        f.close()
    else:
        cmds.warning('No root nodes in scene!')

def HierarchyImport():
    ''' Queries user for hierarchy files and
        sets up the hierarchy.
    '''
    
    #user input for filepath
    basicFilter = 'Hierarchy (*.hierarchy)'
    filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                              caption='Import Hierarchy',fileMode=1)
    
    if filePath!=None:
        
        __hierarchyImport__(filePath[0])

def __hierarchyImport__(filePath):
    ''' Builds hierarchy from hierarchy file
    '''
    
    #getting hierarchy data
    f=open(filePath,'r')
    hierarchyData=muy.load(f)
    
    #checking for existing root node
    root=False
    
    for node in cmds.ls(type='network'):
        
        data=mum.GetData(node)
        if data['type']=='root':
            root=True
    
    #hierarchy data process
    for module in hierarchyData:
        
        #building hierarchy
        parent=hierarchyData[module]['metaParent']
        
        if parent!=None:
            if cmds.objExists(parent)!=False:
            
                moduleCnts=mum.DownStream(module, 'control')
                moduleCnt=mum.GetTransform(moduleCnts[0])
                
                parentCnts=mum.DownStream(parent, 'control')
                if len(parentCnts)>0:
                    
                    parentCnt=mum.GetTransform(parentCnts[0])
                    
                    cmds.select(moduleCnt,parentCnt,r=True)
                    
                    Connect()
                    
                    cmds.select(cl=True)
                
        #creating root node
        if not root:
            if module=='root':
                
                assetName=hierarchyData[module]['asset']
                data={'asset':assetName}
                root=mum.SetData('meta_'+assetName, 'root', None, None, data)
                
                #attaching root node
                rootchild=hierarchyData[module]['child']
                
                cmds.connectAttr(root+'.message',rootchild+'.metaParent',force=True)

def ControlsExport():
    
    #getting file path and name
    basicFilter = "Controls (*.controls)"
    fileName=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,caption='Export Controls')
    
    if fileName!=None:
        
        controls=[]
        for node in cmds.ls(type='network'):
            
            data=mum.GetData(node)
            if data['type']=='control':
                
                controls.append(mum.GetTransform(node))
        
        cmds.select(controls,r=True)
        
        newFileName=cmds.file(fileName[0],exportSelected=True,type='mayaAscii')
        move(newFileName,(os.path.splitext(newFileName)[0]))
        
        cmds.select(cl=True)

def ControlsImport():
    
    #getting file path and name
    basicFilter = "Controls (*.controls)"
    filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,fileMode=1)
    
    if filePath!=None:
        
        __controlsImport__(filePath[0])

def __controlsImport__(filePath):
    ''' Builds controls from controls file. '''
    
    cnts={}
    for node in cmds.ls(type='network'):
        
        data=mum.GetData(node)
        if data['type']=='control':
            cnts[node]=data
            
            module=mum.UpStream(node, 'module')
            mData=mum.GetData(module)
            
            cnts[node]['module_side']=mData['side']
            cnts[node]['module']=mData['component']
            cnts[node]['module_index']=mData['index']
            cnts[node]['module_subcomponent']=mData['subcomponent']
        
    #importing nodes
    importNodes=cmds.file(filePath,i=True,defaultNamespace=False,
                     returnNewNodes=True,renameAll=True,
                     mergeNamespacesOnClash=False,
                     namespace='mr_importControls')
    
    importCnts=[]
    #importNodes loop
    for node in importNodes:
        
        if cmds.nodeType(node)=='network':
            
            data=mum.GetData(node)
            if data['type']=='control':
                importCnts.append(mum.GetTransform(node))
    
    for cnt in importCnts:
        
        data=mum.GetData(cnt)
        
        module=mum.UpStream(cnt, 'module')
        mData=mum.GetData(module)
        
        data['module_side']=mData['side']
        data['module']=mData['component']
        data['module_index']=mData['index']
        data['module_subcomponent']=mData['subcomponent']
        
        metaMatch=mum.Compare(data, cnts)[0]
        cntMatch=mum.GetTransform(metaMatch)
        
        shapeNode=cmds.listRelatives(cnt,shapes=True)
        
        origShapeNode=cmds.listRelatives(cntMatch,shapes=True)[0]
        
        #delete original shape node
        tempGroup=cmds.createNode( 'transform', ss=True )
        
        cmds.parent(origShapeNode,tempGroup,absolute=True,shape=True)
        
        cmds.delete(tempGroup)
        
        #adding new shape node
        cmds.parent(shapeNode,cntMatch,add=True,shape=True)
        
        cmds.rename(shapeNode,shapeNode[0].split(':')[-1])
        
    #delete imported nodes
    for node in importNodes:
        try:
            cmds.delete(node)
        except:
            pass
    
    cmds.namespace(force=True,removeNamespace='mr_importControls')

def ColorRig():
    ''' Color code rig into center,right and left. '''
    
    #finding root in scene
    root=False
    for node in cmds.ls(type='network'):
        
        data=mum.GetData(node)
        if data['type']=='root':
            
            root=node
            modules=mum.DownStream(node, 'module', allNodes=True)
            for module in modules:
                
                __colorModule__(module)
    
    #execute color rig if root is found
    if not root:
        cmds.warning('No root node found in scene!')
    else:
        modules=mum.DownStream(root, 'module', allNodes=True)
        for module in modules:
            
            __colorModule__(module)

def __colorModule__(module):
    
    cnts=mum.DownStream(module, 'control')
    
    mData=mum.GetData(module)
    side=mData['side']
    color=1
    
    if side=='center':
        color=6
    if side=='right':
        color=13
    if side=='left':
        color=14
    
    for cnt in cnts:
        
        tn=mum.GetTransform(cnt)
        
        shape=cmds.listRelatives(tn,shapes=True)[0]
        
        cmds.setAttr('%s.overrideEnabled' % shape,1)
            
        cmds.setAttr('%s.overrideColor' % shape,color)

def __copyShape__(src,trg):
    
    temp=cmds.duplicate(src,returnRootsOnly=True)
    
    shapeNode=cmds.listRelatives(temp,shapes=True)
    
    origShapeNode=cmds.listRelatives(trg,shapes=True)[0]
    
    #delete original shape node
    tempGroup=cmds.createNode( 'transform', ss=True )
    
    cmds.parent(origShapeNode,tempGroup,absolute=True,shape=True)
    
    cmds.delete(tempGroup)
    
    #adding new shape node
    cmds.parent(shapeNode,trg,add=True,shape=True)
    
    cmds.rename(shapeNode,shapeNode[0].split(':')[-1])
    
    #remove temp node
    cmds.delete(temp)