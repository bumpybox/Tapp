import os
import webbrowser

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omu
import sip

import Tapp.Maya.modelling.utils as mmu

uiPath=os.path.dirname(__file__)+'/resources/modelling.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('tapp_modelling')
        
        self.loadedStyleSheet='QPushButton {color: white;background-color: green}'
        
        self.posVerts=None
        self.upVert=None
    
    def on_loadPositionVerts_pushButton_released(self):
        
        sel=cmds.ls(selection=True,flatten=True)
        
        if len(sel)>0:
            
            shape=cmds.ls(selection=True,objectsOnly=True)[0]
            
            if cmds.nodeType(shape)=='mesh':
                if cmds.polyEvaluate()['vertexComponent']>0:
                
                    verts=[]
                    for vert in sel:
                        
                        verts.append(vert)
                    
                    if len(verts)==2:
                        self.posVerts=verts
                        self.positionVerts_label.setText('Verts loaded!')
                        self.loadPositionVerts_pushButton.setStyleSheet(self.loadedStyleSheet)
                    else:
                        cmds.warning('More or Less than two verts selected. Please select only 2 verts.')
                else:
                    cmds.warning('No verts selected!')
            else:
                cmds.warning('Selection is not a vertex!')
        else:
            cmds.warning('Nothing is selected!')
    
    def on_loadUpVert_pushButton_released(self):
        
        sel=cmds.ls(selection=True,flatten=True)
        
        if len(sel)>0:
            
            shape=cmds.ls(selection=True,objectsOnly=True)[0]
            
            if cmds.nodeType(shape)=='mesh':
                if cmds.polyEvaluate()['vertexComponent']>0:
                
                    verts=[]
                    for vert in sel:
                        
                        verts.append(vert)
                    
                    self.upVert=verts
                    self.upVert_label.setText('Vert loaded!')
                    self.loadUpVert_pushButton.setStyleSheet(self.loadedStyleSheet)
                else:
                    cmds.warning('No vert selected!')
            else:
                cmds.warning('Selection is not a vertex!')
        else:
            cmds.warning('Nothing is selected!')
    
    def on_create_pushButton_released(self):
        
        if self.posVerts!=None and self.upVert!=None:
            
            #get check box state
            state=self.locator_checkBox.checkState()
            
            if state==0:
                locatorPivot=False
            if state==2:
                locatorPivot=True
            
            #get check box state
            state=self.mesh_checkBox.checkState()
            
            if state==0:
                meshPivot=False
            if state==2:
                meshPivot=True
            
            #execute
            mmu.triangulatePivot(self.posVerts, self.upVert, locatorPivot, meshPivot)
            
        else:
            cmds.warning('Position Verts and Upvector Vert not loaded!')
    
    def on_scatter_pushButton_released(self):
        
        melPath=os.path.dirname(__file__)+'/icPolyScatter.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        mel.eval('icPolyScatter')
    
    def on_scatterInfo_pushButton_released(self):
        
        webbrowser.open('http://www.braverabbit.de/playground/?p=474')
    
    def on_symmetry_pushButton_released(self):
        
        melPath=os.path.dirname(__file__)+'/kk_symmetry.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        mel.eval('kk_symmetry')
    
    def on_detachSeparate_pushButton_released(self):
        
        melPath=os.path.dirname(__file__)+'/detachSeparate.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        mel.eval('detachSeparate')

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tapp_modelling':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()