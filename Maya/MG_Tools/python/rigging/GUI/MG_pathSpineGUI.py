import os

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import MG_Tools.python.rigging.script.MG_pathSpine as mgps

uiPath=os.path.dirname(__file__)+'/resources/MG_pathSpineGUI.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('MG_pathSpine')
        
        self.loadedStyleSheet='QPushButton {color: white;background-color: green}'
        self.curve=''
        self.root=''
    
    def on_loadCurve_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==1:
                
                node=sel[0]
                shape=cmds.listRelatives(node,shapes=True)[0]
                
                if cmds.nodeType(shape)=='nurbsCurve':
                    
                    self.curve_label.setText('\'%s\' loaded!' % node)
                    self.curve=node
                    self.loadCurve_pushButton.setStyleSheet(self.loadedStyleSheet)
                else:
                    cmds.warning('%s is not a nurbsCurve!' % node)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_root_checkBox_stateChanged(self,state):
        
        #create root on
        if state==2:
            
            self.loadRoot_pushButton.hide()
            self.root_label.hide()
        
        #create root off
        if state==0:
            
            self.loadRoot_pushButton.show()
            self.root_label.show()
    
    def on_loadRoot_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==1:
                
                self.root_label.setText('\'%s\' loaded!' % sel[0])
                self.root=sel[0]
                self.loadRoot_pushButton.setStyleSheet(self.loadedStyleSheet)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_create_pushButton_released(self):
        
        #getting curve
        curve=self.curve
        
        if curve!='':
            
            #getting root
            root='default'
            
            if self.root_checkBox.checkState()==0:
                
                root=self.root
            
            #get locator amount
            locAmount=self.locators_spinBox.value()
            
            #get check box state
            state=self.skinCurve_checkBox.checkState()
            
            if state==0:
                skinCurve=False
            if state==2:
                skinCurve=True
            
            #get check box state
            state=self.defaultValues_checkBox.checkState()
            
            if state==0:
                defaultValues=False
            if state==2:
                defaultValues=True
            
            #create MG_pathSpine
            mgps.MG_pathSpine(curve,locAmount,skinCurve,defaultValues,root)
        else:
            cmds.warning('No curve loaded!')

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='MG_pathSpine':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()