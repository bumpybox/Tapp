import os

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import MG_Tools.python.rigging.script.MG_extrudeEdge as mpme

uiPath=os.path.dirname(__file__)+'/resources/MG_extrudeEdgeGUI.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('MG_extrudeEdgeGUI')
        
        self.loadedStyleSheet='QPushButton {color: white;background-color: green}'
        self.verts=[]
        self.mesh=''
    
    def on_loadMesh_pushButton_released(self):
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==1:
                
                node=sel[0]
                shape=cmds.listRelatives(node,shapes=True)[0]
                
                if cmds.nodeType(shape)=='mesh':
                    
                    self.mesh=node
                    self.mesh_label.setText('\'%s\' loaded!' % node)
                    self.loadMesh_pushButton.setStyleSheet(self.loadedStyleSheet)
                    
                else:
                    cmds.warning('%s is not a mesh!' % node)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_loadVerts_pushButton_released(self):
        
        sel=cmds.ls(selection=True,flatten=True)
        
        if len(sel)>0:
            
            shape=cmds.ls(selection=True,objectsOnly=True)[0]
            
            if cmds.nodeType(shape)=='mesh':
                if cmds.polyEvaluate()['vertexComponent']>0:
                
                    verts=[]
                    for vert in sel:
                        
                        verts.append(int(vert.split('[')[-1].split(']')[0]))
                    
                    self.verts=verts
                    self.verts_label.setText('Verts loaded!')
                    self.loadVerts_pushButton.setStyleSheet(self.loadedStyleSheet)
                else:
                    cmds.warning('No verts selected!')
            else:
                cmds.warning('Selection is not a vertex!')
            
        else:
            
            cmds.warning('Nothing is selected!')
    
    def on_selectVerts_pushButton_released(self):
        
        if len(self.verts)!=0:
            if self.mesh!='':
                
                cmds.select(cl=True)
                for vert in self.verts:
                    cmds.select(self.mesh+'.vtx[%s]' % vert,add=True)
            
            else:
                cmds.warning('No Mesh Loaded!')
            
        else:
            
            cmds.warning('No Verts Loaded!')
    
    def on_create_pushButton_released(self):
        
        if self.mesh!='':
            if len(self.verts)!=0:
                
                mpme.MG_extrudeEdge(self.mesh, self.verts)
                
            else:
                cmds.warning('No Verts Loaded!')
        else:
            cmds.warning('No Mesh Loaded!')
        
def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='MG_extrudeEdgeGUI':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()