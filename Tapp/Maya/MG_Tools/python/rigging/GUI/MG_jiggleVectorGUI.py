import os

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import MG_Tools.python.rigging.script.MG_jiggleVector as mgjiggle

uiPath=os.path.dirname(__file__)+'/resources/MG_jiggleVectorGUI.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('MG_jiggleVector')
        
        self.loadedStyleSheet='QPushButton {color: white;background-color: green}'
        self.targetNode=None
        self.outputNode=None
    
    def on_loadTargetNode_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==1:
                
                node=sel[0]
                    
                self.targetNode_label.setText('\'%s\' loaded!' % node)
                self.targetNode=node
                self.loadTargetNode_pushButton.setStyleSheet(self.loadedStyleSheet)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_loadOutputNode_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==1:
                
                node=sel[0]
                    
                self.outputNode_label.setText('\'%s\' loaded!' % node)
                self.outputNode=node
                self.loadOutputNode_pushButton.setStyleSheet(self.loadedStyleSheet)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_create_pushButton_released(self):
        
        mgjiggle.MG_jiggleVector(self.targetNode, self.outputNode)

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='MG_jiggleVector':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()