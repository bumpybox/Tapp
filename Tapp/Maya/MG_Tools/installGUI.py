import os
import sys
import shutil

from PyQt4 import QtGui
from PyQt4 import uic

uiPath=os.path.dirname(__file__)+'/python/utils/resources/installGUI.ui'
form,base=uic.loadUiType(uiPath)

class Form(base,form):
    def __init__(self, parent=None):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
    def on_install_pushButton_released(self):
        
        if self.Maya2013x64_checkBox.checkState():
            
            #copy plugin file to plugin folder
            mayaDir=QtGui.QFileDialog.getExistingDirectory(parent=None,caption='Locate Maya 2013 64-bit directory!')
            
            pluginDir=mayaDir+'/bin/plug-ins'
            
            plugin=os.path.dirname(__file__)+'/build/1.2/win/2013x64/pro/MG_rigToolsPro.mll'
            
            shutil.copyfile(plugin,str(pluginDir+'/MG_rigToolsPro.mll'))
            
            #copy python folder
            pythonFolder=os.path.dirname(__file__)+'/python'
            scriptsFolder=os.environ['USERPROFILE']+'/Documents/maya/2013-x64/scripts'
            
            if os.path.exists(scriptsFolder+'/MG_Tools'):
                
                shutil.rmtree(scriptsFolder+'/MG_Tools')
            
            shutil.copytree(pythonFolder, scriptsFolder+'/MG_Tools/python')
            shutil.copyfile(pythonFolder+'/__init__.py', scriptsFolder+'/MG_Tools/__init__.py')
            
            #modify userSetup to build MG_Tools menu
            cmd='import maya.cmds as cmds\ncmds.evalDeferred(\'import MG_Tools.python.menu\')'
            
            if not os.path.exists(scriptsFolder+'/userSetup.py'):
                
                f=open(scriptsFolder+'/userSetup.py','w')
                f.write(cmd)
                f.close()
            else:
                
                f=open(scriptsFolder+'/userSetup.py','r')
                fdata=f.read()
                
                fdict=fdata.split('\n')
                
                #check if cmd is not already in userSetup
                if not cmd in fdict:
                    
                    #writing cmd to userSetup
                    data=cmd+'\n'+fdata
                    
                    f=open(scriptsFolder+'/userSetup.py','w')
                    f.write(data)
                    f.close()
            
            sys.exit()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = Form()
    myapp.show()
    sys.exit(app.exec_())