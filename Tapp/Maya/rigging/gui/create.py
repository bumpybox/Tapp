import os
import sys

import maya.cmds as cmds

import Tapp.Maya.rigging.modules as mrm
import Tapp.Maya.rigging.config as mrc
import Tapp.Maya.utils.meta as mum
import Tapp.Maya.rigging.utils as mru
import setup

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

def Delete():
    
    sel=cmds.ls(selection=True)
    
    if len(sel)<=0:
        cmds.warning('No modules selected!\nSelect a module to delete.')
    else:
        
        modules=[]
        
        for node in sel:
            modules.append(mum.UpStream(node, 'module'))
            modules.append(mum.UpStream(node, 'root'))
        
        modules=set(modules)
        
        for module in modules:
            if module!=None:
                try:
                    mru.Detach(module, detachChildren=True)
                except:
                    pass
                
                cnt=mum.DownStream(module, 'control')[0]
                tn=mum.GetTransform(cnt)
                
                cmds.delete(cmds.container(q=True,fc=tn))

def Create(module,dirPath):
    
    __importModule__(module,dirPath)
    
    return mrm.Create()

def Rig():
    ''' Rigs all modules in the scene. '''
    
    cmds.undoInfo(openChunk=True)
        
    sel=cmds.ls(selection=True)
    
    if len(sel)<=0:
        message='No modules are selected!\nDo you want to rig all modules in scene?'
        reply=cmds.confirmDialog( title='Rig Modules',
                                  message=message,
                                  button=['Yes','No'],
                                  defaultButton='Yes',
                                  cancelButton='No')
        
        if reply=='Yes':
            
            #rigging all modules in the scene
            modules=[]
            for meta in cmds.ls(type='network'):
                data=mum.GetData(meta)
                
                if data['type']=='root':
                    modules.append(meta)
            
            for module in modules:
                __rig__(module)
    
    else:
        #collecting modules
        modules=[]
        
        for node in sel:
            modules.append(mum.UpStream(node, 'root'))
        
        #removing duplicates
        modules=list(set(modules))
        
        for module in modules:
            __rig__(module)
    
    cmds.undoInfo(closeChunk=True)

def __rig__(module):
    ''' Rigs the provided module. '''
    
    cmds.undoInfo(openChunk=True)
    
    data=mum.GetData(module)
    moduleName=data['component']
    
    __importModule__(moduleName,mrc.config['modules'].replace('\\','/'))
    
    mrm.Rig(module)
    
    cmds.undoInfo(closeChunk=True)

def ExportTemplate():
    
    #getting file path and name
    basicFilter = "Template (*.ma)"
    filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,caption='Export Template')
    
    if filePath!=None:
        
        #getting containers
        containers=[]
        for node in cmds.ls(type='network'):
            
            data=mum.GetData(node)
            if data['type']=='root':
                
                cnts=mum.DownStream(node, 'control')
                cnt=mum.GetTransform(cnts[0])
                
                containers.append(cmds.container(q=True,fc=cnt))
        
        #exporting containers
        cmds.select(containers,r=True)
        
        cmds.file(filePath[0],exportSelected=True,type='mayaAscii')
        
        cmds.select(cl=True)
        
        #generating python file
        fileName=os.path.basename(filePath[0]).split('.')[0]
        dirPath=os.path.dirname(filePath[0])
        
        cmd='import os\n\n'
        cmd+='import maya.cmds as cmds\n\n'
        cmd+='def Create():\n\t'
        cmd+='path=os.path.realpath(__file__)\n\n\t'
        cmd+='filePath=path.replace(\'\\\\\',\'/\').split(\'.py\')[0]+\'.ma\'\n\n\t'
        cmd+='return cmds.file(filePath,i=True,defaultNamespace=False,'
        cmd+='returnNewNodes=True,renameAll=True,'
        cmd+='mergeNamespacesOnClash=True,'
        cmd+='namespace=\''+fileName+'\')'
        
        f=open(dirPath+'/'+fileName+'.py','w')
        f.write(cmd)
        f.close()

def CreateCharacter():
    
    #user input for filepath
    basicFilter = 'Hierarchy (*.hierarchy)'
    hierarchyFilePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                              caption='Import Hierarchy',fileMode=1)
    
    #getting file path and name
    basicFilter = "Controls (*.controls)"
    controlsFilePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,fileMode=1)
    
    #rigging all modules in the scene
    modules=[]
    for meta in cmds.ls(type='network'):
        data=mum.GetData(meta)
        
        if data['type']=='root':
            modules.append(meta)
    
    for module in modules:
        __rig__(module)
    
    #builds hierarchy
    if hierarchyFilePath!=None:
        
        setup.__hierarchyImport__(hierarchyFilePath[0])
    else:
        cmds.warning('Hierarchy NOT build!')
    
    #builds controls
    if controlsFilePath!=None:
        
        setup.__controlsImport__(controlsFilePath[0])
    else:
        cmds.warning('Controls NOT build!')

def __createMirror__(component,module):
    
    dirPath=os.path.dirname(mrm.__file__)
    
    __importModule__(component, dirPath)
    
    return mrm.__createMirror__(module)

def Mirror():
    
    cmds.undoInfo(openChunk=True)
        
    sel=cmds.ls(selection=True)
    
    if len(sel)<=0:
        cmds.warning('No modules selected!\nSelect a module to mirror.')
    else:
        #collecting modules
        modules=[]
        
        for node in sel:
            modules.append(mum.UpStream(node, 'root'))
        
        #removing duplicates
        modules=list(set(modules))
        
        for module in modules:
            __mirror__(module)
    
    cmds.undoInfo(closeChunk=True)

def __mirror__(module):
    
    #getting module data
    mData=mum.GetData(module)
    
    cnts=mum.DownStream(module, 'control')
    
    container=cmds.container(q=True,fc=mum.GetTransform(cnts[0]))
    
    #getting imported controls
    importcnts=[]
    
    importNodes=__createMirror__(mData['component'],module)
    
    for node in importNodes:
        if cmds.nodeType(node)=='network':
            print node
            
            data=mum.GetData(node)
            if data['type']=='control':
                importcnts.append(node)
    
    #copy container values
    icontainer=cmds.container(q=True,fc=mum.GetTransform(importcnts[0]))
    
    cmds.copyAttr(container,icontainer,values=True)
    
    #getting control data
    cntsdata={}
    for cnt in cnts:
        cntsdata[cnt]=mum.GetData(cnt)
    
    #mirroring translation and rotation
    for cnt in importcnts:
        
        data=mum.GetData(cnt)
        
        metaMatch=mum.Compare(data, cntsdata)[0]
        cntMatch=mum.GetTransform(metaMatch)
        
        tn=mum.GetTransform(cnt)
        parent=cmds.nodeType(cmds.listRelatives(tn,p=True))
        
        if parent==None or parent=='dagContainer':
            
            [tx,ty,tz]=cmds.xform(cntMatch,ws=True,query=True,translation=True)
            [rx,ry,rz]=cmds.xform(cntMatch,ws=True,query=True,rotation=True)
        
            cmds.xform(tn,ws=True,translation=(-tx,ty,tz))
            cmds.xform(tn,ws=True,rotation=(rx,-ry,-rz))
            
            cmds.rotate(0,180,0,tn,relative=True,os=True)
        
        else:
            
            [tx,ty,tz]=cmds.xform(cntMatch,os=True,query=True,translation=True)
            [rx,ry,rz]=cmds.xform(cntMatch,os=True,query=True,rotation=True)
            
            cmds.xform(tn,os=True,translation=(tx,ty,tz))
            cmds.xform(tn,os=True,rotation=(rx,-ry,-rz))

#__mirror__('meta_finger4','meta_finger7')