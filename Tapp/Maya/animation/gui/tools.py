import os

import maya.cmds as cmds
import maya.mel as mel

import Tapp.Maya.utils.meta as mum

def exportAnim():
    
    sel=cmds.ls(selection=True)
    
    if len(sel)>0:
        
        #getting file path and name
        basicFilter = "ATOM (*.atom)"
        filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                                  caption='Export Animation')
        
        if filePath!=None:
            
            #prompt user for export type
            exportType=cmds.confirmDialog( title='Export', message='What do you want to export?',
                                           button=['Rig','Selected'], defaultButton='Yes',
                                           cancelButton='No')
            
            #filter filePath
            fileName=os.path.basename(filePath[0]).split('.')[0]
            path=os.path.dirname(filePath[0])
            
            #generate export cmd
            cmd='file -force -options "precision=8;statics=1;baked=1;sdk=0;constraint=0;animLayers=1;'
            cmd+='selected=selectedOnly;whichRange=1;range=1:10;hierarchy=none;controlPoints=0;'
            cmd+='useChannelBox=1;options=keys;copyKeyCmd=-animation objects '
            cmd+='-option keys -hierarchy none -controlPoints 0 " -typ "atomExport" -es "'+filePath[0]+'";'
            
            #loading plugin
            if not cmds.pluginInfo('atomImportExport',query=True, loaded=True ):
                cmds.loadPlugin('atomImportExport')
            
            #exporting anim
            mel.eval(cmd)
            
            #export control data
            sel=cmds.ls(selection=True)
            
            ymlFile=path+'/'+fileName+'.yml'
            
            if exportType=='Selected':
                mum.exportControlData(sel, ymlFile)
            else:
                mum.exportControlData(sel, ymlFile,selected=False)
    else:
        cmds.warning('Nothing is selected!')

def importAnim():
    
    pass