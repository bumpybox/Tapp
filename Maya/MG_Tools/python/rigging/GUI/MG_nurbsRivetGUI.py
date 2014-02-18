import os

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import MG_Tools.python.rigging.script.MG_nurbsRivet as mgnr 

uiPath=os.path.dirname(__file__)+'/resources/MG_nurbsRivetGUI.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('MG_nurbsRivet')
        
        self.loadedStyleSheet='QPushButton {color: white;background-color: green}'
        self.mesh=''
        self.rivetobject=''
    
    def on_loadMesh_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==1:
                
                node=sel[0]
                shape=cmds.listRelatives(node,shapes=True)[0]
                
                if cmds.nodeType(shape)=='nurbsSurface':
                    
                    self.mesh_label.setText('\'%s\' loaded!' % node)
                    self.loadMesh_pushButton.setStyleSheet(self.loadedStyleSheet)
                    self.mesh=node
                else:
                    cmds.warning('%s is not a nurbsSurface!' % node)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_loadRivetObject_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==1:
                
                self.rivetObject_label.setText('\'%s\' loaded!' % sel[0])
                self.loadRivetObject_pushButton.setStyleSheet(self.loadedStyleSheet)
                self.rivetobject=sel[0]
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_create_pushButton_released(self):
        
        #getting mesh
        mesh=self.mesh
        
        if mesh!='':
            
            #getting root
            rivetObj=self.rivetobject
            
            if rivetObj!='':
                
                #get maintain offset check state
                state=self.maintainOffset_checkBox.checkState()
                
                if state==0:
                    maintainOffset=False
                if state==2:
                    maintainOffset=True
                
                #create nurbs rivet
                mgnr.MG_nurbsRivet(surface = mesh , target = rivetObj, mo = maintainOffset)
                
            else:
                cmds.warning('No Rivet Object loaded!')
        else:
            cmds.warning('No Nurbs Surface loaded!')

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='MG_nurbsRivet':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()