import os

import maya.cmds as cmds

import Tapp.Maya.utils.paie as mup
import Tapp.Maya.utils.meta as mum
import Tapp.Maya.utils.yaml as muy

def ExportAnim():
    
    sel=cmds.ls(selection=True)
    
    if len(sel)>0:
        
        #getting file path and name
        basicFilter = "ANIM (*.xad)"
        filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                                  caption='Export Animation')
        
        #exporting animation
        if filePath!=None:
            mup.exportData(filePath[0], 'anim')
        
            #getting controls data
            data={}
            for node in sel:
                
                nData=mum.GetControlData(node)
                if nData!=None:
                    
                    nodeName=nData['transform']
                    
                    del(nData['name'])
                    del(nData['metaParent'])
                    del(nData['transform'])
                    
                    data[nodeName]=nData
            
            #exporting controls data
            fileName=os.path.basename(filePath[0]).split('.')[0]
            dirPath=os.path.dirname(filePath[0])
            
            f=open(dirPath+'/'+fileName+'.yml','w')
            muy.dump(data, f)
            f.close()
    else:
        cmds.warning('Nothing is selected!')

def ImportAnim(filePath):
    
    #getting paie data
    mupd=mup.DataWrapper()
    mupd.load(filePath)
    '''
    #getting meta data
    fileName=os.path.basename(filePath).split('.')[0]
    dirPath=os.path.dirname(filePath)
    
    f=open(dirPath+'/'+fileName+'.yml','r')
    metaData=muy.load(f)
    
    #getting scene controls
    for node in cmds.ls(type='network'):
        
        data=mum.GetControlData(node)
        if data!=None:
        
            del(data['name'])
            del(data['metaParent'])
            del(data['transform'])
            
            [metaMatch,pct]=mum.Compare(data, metaData)
            
            if pct>90.0:
                
                pass
    
    for namespace in mupd.dataObj.listNamespaces():
        
        for node in mupd.dataObj.listObjs(namespace):
            
            print node.split('|')[-1]
            '''
    sel=cmds.ls(selection=True)
    mupd.writeToScene(sel, selectOrder=True, namespace='grandpa:', animOffset=0)
        
#ImportAnim('c:/Users/toke.jepsen/Desktop/temp.xad')