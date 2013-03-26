import maya.cmds as cmds
import os
import sys

def TappInstall_UI():
    if cmds.window('TappInstall_UI', exists=True):
        cmds.deleteUI('TappInstall_UI')
    
    window=cmds.window('TappInstall_UI',title='Tapp Install',w=300,h=110,titleBarMenu=False,sizeable=False)
    
    cmds.columnLayout(w=300,h=110)
    formLayout=cmds.formLayout(w=300,h=110)
    
    text=cmds.text(label='Tapp repository is not found!\nWould you like to locate it?',w=300)
    
    cancelButton=cmds.button(label='Cancel',w=140,h=50,c=TappInstall_cancel)
    browseButton=cmds.button(label='Browse',w=140,h=50,c=TappInstall_browse)
    
    cmds.formLayout(formLayout,edit=True,af=[(text,'left',10),(text,'top',10)])
    cmds.formLayout(formLayout,edit=True,af=[(cancelButton,'left',5),(cancelButton,'top',50)])
    cmds.formLayout(formLayout,edit=True,af=[(browseButton,'right',5),(browseButton,'top',50)])

    cmds.showWindow(window)

def TappInstall_browse(*args):
    repoPath=cmds.fileDialog2(dialogStyle=1,fileMode=3)[0]
    
    check=False
    #checking all subdirectories
    for name in os.listdir(repoPath):
        
        #confirm that this is the Tapp directory
        if name=='Tapp':
            check=True
    
    if check:
        #create the text file that contains the Tapp directory path
        path=cmds.internalVar(upd=True)+'Tapp.config'
        
        f=open(path,'w')
        f.write(repoPath)
        f.close()

        #run setup
        sys.path.append(repoPath)
        
        cmds.evalDeferred('import Tapp')
        
        #delete ui
        cmds.deleteUI('TappInstall_UI')
        
    else:
        cmds.warning('Selected directory is not the \'Tapp\' directory. Please try again')

def TappInstall_cancel(*args):
    cmds.deleteUI('TappInstall_UI')

def Tapp():
    path=cmds.internalVar(upd=True)+'Tapp.config'

    if os.path.exists(path):
        f=open(path,'r')
        path=f.readline()

        if os.path.exists(path):
            if not path in sys.path:
                sys.path.append(path)
            
            #run setup
            cmds.evalDeferred('import Tapp')
        else:
            TappInstall_UI()
    else:
        TappInstall_UI()

scriptJobNum=cmds.scriptJob(event=('NewSceneOpened',Tapp))
scriptJobNum=cmds.scriptJob(event=('SceneOpened',Tapp))