import os
import webbrowser
import xml.etree.ElementTree as xml
from cStringIO import StringIO

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omu

import shiboken
import pysideuic
from PySide import QtGui, QtCore

import Tapp.Maya.settings as ms
import Tapp.Maya.utils as mu

def maya_main_window():
    """
    Get the main Maya window as a QtGui.QMainWindow instance
    @return: QtGui.QMainWindow instance of the top level Maya windows
    """
    ptr = omu.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken.wrapInstance(long(ptr), QtGui.QMainWindow)


def loadUiType(uiFile):
    """
    Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
    and then execute it in a special frame to retrieve the form_class.
    """
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        pysideuic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        #Fetch the base_class and form class based on their type in the xml from designer
        form_class = frame['Ui_%s'%form_class]
        base_class = eval('QtGui.%s'%widget_class)
    return form_class, base_class

uiPath=os.path.dirname(__file__)+'/resources/settings_gui.ui'
form,base=loadUiType(uiPath)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(Form,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('tapp_settings')
        
        self.repoPath=''
        self.launchWin=False
        
        self.readSettings()
        
        self.create_connections()
    
    def readSettings(self):
        
        settings=ms.getSettings()
        
        print settings
        
        #reading repository path
        repoPath=settings['repositoryPath']
        self.repository_label.setText(repoPath)
        self.repoPath=repoPath
        
        #reading launch at startup
        launchWin=settings['launchWindowAtStartup']
        if launchWin==True:
            self.launchWindowAtStartup_checkBox.setCheckState(QtCore.Qt.CheckState(True))
            self.launchWin=True
        else:
            self.launchWindowAtStartup_checkBox.setCheckState(QtCore.Qt.CheckState(False))
    
    def create_connections(self):
        
        self.setRepository_pushButton.released.connect(self.on_setRepository_pushButton_released)
        self.saveSettings_pushButton.released.connect(self.on_saveSettings_pushButton_released)
    
    def on_setRepository_pushButton_released(self):
        
        repoPath=cmds.fileDialog2(dialogStyle=1,fileMode=3)
        
        if repoPath:
            repoPath=repoPath[0].replace('\\','/')
            
            check=False
            #checking all subdirectories
            for name in os.listdir(repoPath):
                
                #confirm that this is the Tapp directory
                if name=='Tapp':
                    check=True
            
            if check:
                
                self.repository_label.setText(repoPath)
                self.repoPath=repoPath
                
            else:
                cmds.warning('Selected directory is not the \'Tapp\' directory. Please try again')
    
    def on_saveSettings_pushButton_released(self):
        
        #get check box state
        state=self.launchWindowAtStartup_checkBox.checkState()
        
        launchWin=False
        if state==0:
            launchWin=False
        if state==2:
            launchWin=True
                
        #collecting data
        data={'repositoryPath':self.repoPath,'launchWindowAtStartup':launchWin}
        
        ms.setSettings(data)
        
        self.close()
        
def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tapp_settings':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()