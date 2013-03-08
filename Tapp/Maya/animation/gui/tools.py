import os

import maya.cmds as cmds

import Tapp.Maya.utils.paie as mup
import Tapp.Maya.utils.meta as mum
import Tapp.Maya.utils.yaml as muy

def __exportAnim__(filePath,objs):
    ''' Exports selection or rig animation. '''
    
    mup.exportData(filePath, 'anim')
    
    #getting controls data
    data={}
    for node in objs:
        
        nData=mum.GetControlData(node)
        if nData!=None:
            
            nodeName=nData['transform']
            
            del(nData['name'])
            del(nData['metaParent'])
            del(nData['transform'])
            del(nData['root_asset'])
            
            if 'switch' in nData:
                
                del(nData['switch'])
            
            data[nodeName]=nData
    
    #exporting controls data
    fileName=os.path.basename(filePath).split('.')[0]
    dirPath=os.path.dirname(filePath)
    
    f=open(dirPath+'/'+fileName+'.yml','w')
    muy.dump(data, f)
    f.close()

def ExportAnim():
    ''' User exports selection or rig animation. '''
    
    result=cmds.confirmDialog( title='Export Anim',
                               message='What do you want to export?',
                               button=['Selected','Rig','Cancel'])
    if result!='Cancel':
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
        
            #getting file path and name
            basicFilter = "ANIM (*.xad)"
            filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                                      caption='Export Animation')
            
            #case of selected export
            if result=='Selected':
                #exporting animation
                if filePath!=None:
                    
                    __exportAnim__(filePath[0],sel)
            
            #case of rig export
            if result=='Rig':
                
                #getting all controls
                root=mum.UpStream(sel[0], 'root')
                cnts=mum.DownStream(root, 'control', allNodes=True)
                
                nodes=[]
                for cnt in cnts:
                    
                    nodes.append(mum.GetTransform(cnt))
                
                #exporting animation
                __exportAnim__(filePath[0],nodes)
        else:
            if result=='Rig':
                cmds.warning('Need to select a control on the rig!')
            else:
                cmds.warning('Nothing is selected!')

def ImportAnim():
    ''' User import animation to selection or rig. '''
    
    result=cmds.confirmDialog( title='Import Anim',
                               message='Where do you want to import the animation?',
                               button=['Selected','Rig','Cancel'])
    if result!='Cancel':
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
        
            #getting file path and name
            basicFilter = "ANIM (*.xad)"
            filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                                      fileMode=1,
                                      caption='Import Animation')
            
            #case of selected export
            if result=='Selected':
                #exporting animation
                if filePath!=None:
                    
                    __importAnim__(filePath[0],selection=True)
            
            #case of rig export
            if result=='Rig':
                
                #exporting animation
                __importAnim__(filePath[0])
        else:
            if result=='Rig':
                cmds.warning('Need to select a control on the rig!')
            else:
                cmds.warning('Nothing is selected!')

def __importAnim__(filePath,selection=False):
    ''' Imports animation to selection or rig. '''
    
    #getting paie data
    mupd=mup.DataWrapper()
    mupd.load(filePath)
    
    #getting meta data
    fileName=os.path.basename(filePath).split('.')[0]
    dirPath=os.path.dirname(filePath)
    
    f=open(dirPath+'/'+fileName+'.yml','r')
    metaData=muy.load(f)
    
    #getting controls
    sel=cmds.ls(selection=True)
    nodes=[]
    
    #selection controls
    if selection:
        
        for node in sel:
            
            nodes.append(mum.GetMetaNode(node))
    #rig controls
    else:
        root=mum.UpStream(sel[0], 'root')
        nodes=mum.DownStream(root, 'control', allNodes=True)
    
    #building paie data
    paieId={}
    
    for node in nodes:
        
        data=mum.GetControlData(node)
        if data!=None:
        
            del(data['name'])
            del(data['metaParent'])
            del(data['transform'])
            #possible obsolete attribute
            del(data['root_asset'])
            
            if 'switch' in data:
                
                del(data['switch'])
            
            [metaMatch,pct]=mum.Compare(data, metaData)
            
            if pct>90.0:
                
                if metaMatch!=None:
        
                    for namespace in mupd.dataObj.listNamespaces():
                        
                        iddict=mupd.dataObj.getObjIdDict(namespace)
                        for nodeId in iddict:
                            
                            if iddict[nodeId].split('|')[-1]==metaMatch:
                                
                                nodeData={}
                                nodeData['node']=mum.GetTransform(node)
                                nodeData['namespace']=namespace
                                
                                paieId[nodeId]=nodeData
    
    mupd.writeToObjs(paieId, animOffset=cmds.currentTime(q=True))