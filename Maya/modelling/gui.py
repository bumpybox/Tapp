import os
import webbrowser
import xml.etree.ElementTree as xml
from cStringIO import StringIO

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omu

import shiboken
import pysideuic
from PySide import QtGui

import Tapp.Maya.modelling.utils as mmu

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

uiPath=os.path.dirname(__file__)+'/resources/modelling.ui'
form,base=loadUiType(uiPath)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(Form,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('tapp_modelling')
        
        self.loadedStyleSheet='QPushButton {color: white;background-color: green}'
        
        self.posVerts=None
        self.upVert=None
    
        self.create_connections()
    
    def create_connections(self):
        
        self.loadPositionVerts_pushButton.released.connect(self.on_loadPositionVerts_pushButton_released)
        self.loadUpVert_pushButton.released.connect(self.on_loadUpVert_pushButton_released)
        self.create_pushButton.released.connect(self.on_create_pushButton_released)
        self.scatter_pushButton.released.connect(self.on_scatter_pushButton_released)
        self.scatterInfo_pushButton.released.connect(self.on_scatterInfo_pushButton_released)
        self.symmetry_pushButton.released.connect(self.on_symmetry_pushButton_released)
        self.detachSeparate_pushButton.released.connect(self.on_detachSeparate_pushButton_released)
        self.roadKill_pushButton.released.connect(self.on_roadKill_pushButton_released)
    
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
    
    def on_roadKill_pushButton_released(self):
        
        melPath=os.path.dirname(__file__)+'/RoadKill.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        #get useLSCM
        state=self.roadkill_useLSCM_checkBox.checkState()
        
        if state==0:
            LSCMText='",-abf"'
        if state==2:
            LSCMText='",-lscm"'
        
        #get holesText
        state=self.roadkill_dontFillHoles_checkBox.checkState()
        
        if state==0:
            holesText='",-nofillholes"'
        if state==2:
            holesText='",-fillholes"'
        
        #get liveText
        state=self.roadkill_liveUnwrap_checkBox.checkState()
        
        if state==0:
            liveText='",-notlive"'
        if state==2:
            liveText='",-live"'
        
        exeDir='"'+os.path.dirname(__file__)+'"'
        exeDir=exeDir.replace('\\','/')
        
        mel.eval('DoUnwrap(%s,%s,%s,%s)' % (LSCMText,holesText,liveText,exeDir))

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tapp_modelling':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()