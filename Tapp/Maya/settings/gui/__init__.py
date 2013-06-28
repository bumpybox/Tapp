import os

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omu
import sip

import Tapp.Maya.settings as ms
import Tapp.Maya.utils as mu

uiPath=os.path.dirname(__file__)+'/resources/settings_gui.ui'
uiPath=r'C:\Users\tokejepsen\Documents\GitHub\Tapp\Tapp\Maya\settings\gui\resources/settings_gui.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('tapp_settings')
        
        self.repoPath=''
        self.launchWin=False
        
        self.readSettings()
    
    def readSettings(self):
        
        settings=ms.getSettings()
        
        #reading repository path
        repoPath=settings['repositoryPath']
        self.repository_label.setText(repoPath)
        self.repoPath=repoPath
        
        #reading launch at startup
        launchWin=settings['launchWindowAtStartup']
        self.launchWindowAtStartup_checkBox.setCheckState(launchWin)
        self.launchWin=launchWin
    
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

show()