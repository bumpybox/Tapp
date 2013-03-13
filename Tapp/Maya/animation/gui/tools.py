import os
from shutil import move

import maya.cmds as cmds

import Tapp.Maya.utils.paie as mup
import Tapp.Maya.utils.meta as mum
import Tapp.Maya.utils.yaml as muy
import Tapp.Maya.animation.utils.playblast as maup

def __exportAnim__(filePath,objs,cam):
    ''' Exports selection or rig animation. '''
    
    #splitting filePath
    fileName=os.path.basename(filePath).split('.')[0]
    dirPath=os.path.dirname(filePath)
    
    #exporting animation data
    cmds.select(objs,r=True)
    
    mup.exportData(filePath, 'anim',overWrite=True)
    
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
    f=open(dirPath+'/'+fileName+'.yml','w')
    muy.dump(data, f)
    f.close()
    
    #exporting movie
    maup.__exportPlayblast__(dirPath+'/'+fileName+'.mov',cam)
    
    #exporting thumbnail
    maup.__exportPlayblast__(dirPath+'/'+fileName+'.png',cam,exportType='still')
    
    #exporting trax clip
    animCurves=[]
    for obj in objs:
        curves=cmds.listConnections(obj, source=True, type="animCurve")
        if curves!=None:
            for c in curves:
                animCurves.append(c)
    
    startTime=cmds.playbackOptions(q=True,minTime=True)
    endTime=cmds.playbackOptions(q=True,maxTime=True)
    
    charSet=cmds.character(objs)
    animClip=cmds.clip(charSet,sc=0,leaveOriginal=True,allAbsolute=True,
                       n=fileName,startTime=startTime,endTime=endTime)
    sourceClip=cmds.clip(animClip,q=True,scn=True)
    charClip=cmds.character(charSet,q=True,library=True)
    
    cmds.select(charClip,sourceClip,animCurves,r=True)
    oldFileName=cmds.file(dirPath+'/'+fileName+'.ma',type='mayaAscii',exportSelected=True)
    move(oldFileName,dirPath+'/'+fileName+'.traxclip')
    
    cmds.delete(charSet)
    
    #inform user of end of export
    cmds.warning('Export Successfull!')

def ExportAnim():
    ''' User exports selection or rig animation. '''
    
    sel=cmds.ls(selection=True)
    
    if len(sel)>0:
    
        #getting cameras in scene
        cams=[]
        exclude=['front','side','top']
        for cam in cmds.ls(cameras=True):
            
            tn=cmds.listRelatives(cam,parent=True)[0]
            
            if tn not in exclude:
                cams.append(tn)
        
        cams.append('Cancel')
        
        #user input
        result=cmds.confirmDialog( title='Export Anim',
                                   message='Select camera to preview from.',
                                   button=cams)
    
        if result!='Cancel':
        
            #getting file path and name
            basicFilter = "ANIM (*.xad)"
            filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                                      caption='Export Animation')
            
            if filePath!=None:
                    
                #getting all controls
                root=mum.UpStream(sel[0], 'root')
                cnts=mum.DownStream(root, 'control', allNodes=True)
                
                nodes=[]
                for cnt in cnts:
                    
                    nodes.append(mum.GetTransform(cnt))
                
                #exporting animation
                __exportAnim__(filePath[0],nodes,result)
            
            #revert selection
            cmds.select(sel,r=True)
    else:
        cmds.warning('Need to select a control on the rig!')

def ImportAnim():
    ''' User import animation to selection or rig. '''
    
    sel=cmds.ls(selection=True)
    
    if len(sel)>0:
        
        #getting file path and name
        basicFilter = "ANIM (*.xad)"
        filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                                  fileMode=1,
                                  caption='Import Animation')
        
        if filePath!=None:
            
            traxresult=cmds.confirmDialog( title='Import Anim',
                                           message='Using Trax Editor?',
                                           button=['Yes','No'])
            
            if traxresult=='Yes':
                traxresult=True
            else:
                traxresult=False
            
            #importing animation
            __importAnim__(filePath[0],selection=False,trax=traxresult)
        else:
            cmds.warning('Need to select a control on the rig!')

def __importAnim__(filePath,selection=False,trax=False):
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
    
    if trax:        
        #query existing character
        characters=cmds.ls(type='character')
        charNode=None
        if characters!=None:
            for char in characters:
                
                charobjs=cmds.character(char,q=True,nodesOnly=True)
                
                if nodes[0] in charobjs:
                    charNode=char
        
        #creating character if none is present
        if charNode==None:
            
            transformNodes=[]
            for node in nodes:
                
                tn=mum.GetTransform(node)
                transformNodes.append(tn)
                
            charNode=cmds.character(transformNodes)
        
        #importing nodes
        importNodes=cmds.file(dirPath+'/'+fileName+'.traxclip',
                              i=True,defaultNamespace=False,
                              returnNewNodes=True,renameAll=True,
                              mergeNamespacesOnClash=False,
                              namespace='clipImport_temp')
        
        animClip=cmds.ls(importNodes,type='animClip')[0]
        
        cmds.clip(animClip,copy=True)
        cmds.clip(charNode,paste=True,sc=True,allAbsolute=True)
        
        #delete imported nodes
        for node in importNodes:
            try:
                cmds.delete(node)
            except:
                pass
        
        #this might need to be a recursive function in the future
        namespaces=cmds.namespaceInfo('clipImport_temp',listOnlyNamespaces=True)
        for nSpace in namespaces:
            cmds.namespace(force=True,removeNamespace=nSpace)
        
        cmds.namespace(force=True,removeNamespace='clipImport_temp')
    else:
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
    
    #inform user of end of import
    cmds.warning('Import Successfull!')