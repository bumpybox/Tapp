import os

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import MG_Tools.python.rigging.script.MG_twist as mgtwist

uiPath=os.path.dirname(__file__)+'/resources/MG_twistGUI.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('MG_twist')
        
        self.loadedStyleSheet='QPushButton {color: white;background-color: green}'
        self.startMatrix=None
        self.endMatrix=None
    
    def on_loadStartMatrix_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==1:
                
                node=sel[0]
                    
                self.startMatrix_label.setText('\'%s\' loaded!' % node)
                self.startMatrix=node
                self.loadStartMatrix_pushButton.setStyleSheet(self.loadedStyleSheet)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_loadEndMatrix_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==1:
                
                node=sel[0]
                    
                self.endMatrix_label.setText('\'%s\' loaded!' % node)
                self.endMatrix=node
                self.loadEndMatrix_pushButton.setStyleSheet(self.loadedStyleSheet)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_create_pushButton_released(self):
        
        #getting locator amount
        locAmount=self.locators_spinBox.value()
        
        #getting twist axis
        twistAxis='X'
        
        if self.y_radioButton.isChecked():
            twistAxis='Y'
        if self.z_radioButton.isChecked():
            twistAxis='Z'
        
        mgtwist.MG_twist(self.startMatrix, self.endMatrix, locAmount, twistAxis)

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='MG_twist':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()