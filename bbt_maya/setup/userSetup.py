import maya.cmds as cmds
import os
import sys

def bumpyboxToolsInstall_UI():
    if cmds.window('bumpyboxToolsInstall_UI', exists=True):
        cmds.deleteUI('bumpyboxToolsInstall_UI')
    
    window=cmds.window('bumpyboxToolsInstall_UI',title='Bumpybox Tools Install',w=300,h=110,titleBarMenu=False,sizeable=False)
    
    mainLayout=cmds.columnLayout(w=300,h=110)
    formLayout=cmds.formLayout(w=300,h=110)
    
    text=cmds.text(label='ERROR: Could not find \'bumpyboxTools\' directory.\nPlease locate using the \'Browse\' button',w=300)
    
    cancelButton=cmds.button(label='Cancel',w=140,h=50,c=bumpyboxToolsInstall_cancel)
    browseButton=cmds.button(label='Browse',w=140,h=50,c=bumpyboxToolsInstall_browse)
    
    cmds.formLayout(formLayout,edit=True,af=[(text,'left',10),(text,'top',10)])
    cmds.formLayout(formLayout,edit=True,af=[(cancelButton,'left',5),(cancelButton,'top',50)])
    cmds.formLayout(formLayout,edit=True,af=[(browseButton,'right',5),(browseButton,'top',50)])

    cmds.showWindow(window)

def bumpyboxToolsInstall_browse(*args):
    bumpyboxToolsDir=cmds.fileDialog2(dialogStyle=1,fileMode=3)[0]
    
    #confirm that this is the maya tools directory
    if bumpyboxToolsDir.rpartition('\\')[-1]!='bumpyboxTools':
        cmds.warning('Selected directory is not the \'bumpyboxTools\' directory. Please try again')
    else:
        cmds.deleteUI('bumpyboxToolsInstall_UI')
        
        #create the text file that contains the bumpybox tools directory path
        path=cmds.internalVar(upd=True)+'bumpyboxTools.txt'
        
        f=open(path,'w')
        f.write(bumpyboxToolsDir)
        f.close()

        #run setup
        sys.path.append(bumpyboxToolsDir)
        
        cmds.evalDeferred('import bbt_maya')

def bumpyboxToolsInstall_cancel(*args):
    cmds.deleteUI('bumpyboxToolsInstall_UI')

def bumpyboxTools():
    path=cmds.internalVar(upd=True)+'bumpyboxTools.txt'

    if os.path.exists(path):
        f=open(path,'r')
        path=f.readline()

        if os.path.exists(path):
            if not path in sys.path:
                sys.path.append(path)
        
        #run setup
        cmds.evalDeferred('import bbt_maya')
    else:
        bumpyboxToolsInstall_UI()

scriptJobNum=cmds.scriptJob(event=('NewSceneOpened',bumpyboxTools))
scriptJobNum=cmds.scriptJob(event=('SceneOpened',bumpyboxTools))
