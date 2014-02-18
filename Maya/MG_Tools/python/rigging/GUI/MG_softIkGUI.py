import os

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import MG_Tools.python.rigging.script.MG_softIk as mgsi

uiPath=os.path.dirname(__file__)+'/resources/MG_softIkGUI.ui'

form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('MG_softIk')
        
        self.loadedStyleSheet='QPushButton {color: white;background-color: green}'
        
        self.joints=None
        self.startMatrix=None
        self.endMatrix=None
        self.ikHandle=None
    
    def on_loadJoints_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==3:
                
                jointsCheck=True
                
                for node in sel:
                    if cmds.nodeType(node)!='joint':
                        jointsCheck=False
                
                if jointsCheck:
                    
                    self.joints_label.setText('Joints loaded!')
                    self.joints=sel
                    self.loadJoints_pushButton.setStyleSheet(self.loadedStyleSheet)
                else:
                    cmds.warning('Not all nodes selected are joints!')
            else:
                cmds.warning('Please select only three nodes.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_loadStartMatrix_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        node=sel[0]
        
        if len(sel)>0:
            if len(sel)==1:
                
                if cmds.nodeType(node)=='transform':
                    
                    self.startMatrix_label.setText('\'%s\' loaded!' % node)
                    self.startMatrix=node
                    self.loadStartMatrix_pushButton.setStyleSheet(self.loadedStyleSheet)
                else:
                    cmds.warning('%s is not a transform!' % node)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_loadEndMatrix_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        node=sel[0]
        
        if len(sel)>0:
            if len(sel)==1:
                
                if cmds.nodeType(node)=='transform':
                    
                    self.endMatrix_label.setText('\'%s\' loaded!' % node)
                    self.endMatrix=node
                    self.loadEndMatrix_pushButton.setStyleSheet(self.loadedStyleSheet)
                else:
                    cmds.warning('%s is not a transform!' % node)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_loadIkHandle_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        node=sel[0]
        
        if len(sel)>0:
            if len(sel)==1:
                
                if cmds.nodeType(node)=='ikHandle':
                    
                    self.ikHandle_label.setText('\'%s\' loaded!' % node)
                    self.ikHandle=node
                    self.loadIkHandle_pushButton.setStyleSheet(self.loadedStyleSheet)
                else:
                    cmds.warning('%s is not an ik handle!' % node)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')

    def on_startMatrix_checkBox_stateChanged(self,state):
        
        #create startMatrix on
        if state==2:
            
            self.loadStartMatrix_pushButton.hide()
            self.startMatrix_label.hide()
        
        #create startMatrix off
        if state==0:
            
            self.loadStartMatrix_pushButton.show()
            self.startMatrix_label.show()
    
    def on_endMatrix_checkBox_stateChanged(self,state):
        
        #create endMatrix on
        if state==2:
            
            self.loadEndMatrix_pushButton.hide()
            self.endMatrix_label.hide()
        
        #create endMatrix off
        if state==0:
            
            self.loadEndMatrix_pushButton.show()
            self.endMatrix_label.show()
    
    def on_ikHandle_checkBox_stateChanged(self,state):
        
        #create ikHandle on
        if state==2:
            
            self.loadIkHandle_pushButton.hide()
            self.ikHandle_label.hide()
        
        #create ikHandle off
        if state==0:
            
            self.loadIkHandle_pushButton.show()
            self.ikHandle_label.show()
    
    def on_create_pushButton_released(self):
        
        #getting curve
        joints=self.joints
        
        if joints!=None:
            
            #getting start matrix
            startMatrix=None
            
            if self.startMatrix_checkBox.checkState()==0:
                
                startMatrix=self.startMatrix
            
            #getting end matrix
            endMatrix=None
            
            if self.endMatrix_checkBox.checkState()==0:
                
                endMatrix=self.endMatrix
            
            #getting end matrix
            ikHandle=None
            
            if self.ikHandle_checkBox.checkState()==0:
                
                ikHandle=self.ikHandle
            
            #create MG_pathSpine
            mgsi.MG_softIk(joints, startMatrix, endMatrix, ikHandle)
        else:
            cmds.warning('No joints loaded!')

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='MG_softIk':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()