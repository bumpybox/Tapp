import os

import maya.cmds as cmds
import maya.mel as mel

class project():
    
    def setup(self):
        
        self.set()
        
        #changing maya ui commands
        mel.eval('buildFileMenu();')
        cmds.menuItem("openProject",command='import bbt_maya.bgt.utils;project=bbt_maya.bgt.utils.project();project.openScene()',edit=True)
        cmds.menuItem("newProject",command='import bbt_maya.bgt.utils;project=bbt_maya.bgt.utils.project();project.newScene()',edit=True)
    
    def openScene(self):
        
        mel.eval('OpenScene;')
        self.set()
        
    def newScene(self):
        
        mel.eval('NewScene;')
        self.set()
    
    def set(self):
        path=(cmds.file(q=True,sn=True))
        fileName=(cmds.file(q=True,sn=True,shn=True))

        if fileName!='':
            temp=path.partition(fileName)
            cmds.workspace(temp[0],openWorkspace=True)
            
            print 'File Inherit Project Set'
        else:
            #checks if default project directory is set
            if cmds.optionVar(q='ProjectsDir')==0:
                #default project directory is not set
                defaultDir=os.getenv("HOME")+'/maya/projects/default'
                
                if not os.path.exists(defaultDir):
                    os.makedirs(defaultDir)
                
                cmds.workspace(defaultDir, openWorkspace=True)
            else:
                cmds.workspace(((cmds.optionVar(q='ProjectsDir'))), openWorkspace=True)
            
            print 'Default Project Set'