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

import Tapp.Maya.lighting.alembic as alembic

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

uiPath=os.path.dirname(__file__)+'/resources/animation.ui'
form,base=loadUiType(uiPath)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(Form,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('tapp_lighting')
        
        self.create_connections()
    
    def create_connections(self):
        
        self.fileTextureManager_pushButton.released.connect(self.on_fileTextureManager_pushButton_released)
        self.addRimLight_pushButton.released.connect(self.on_addRimLight_pushButton_released)
        
        self.exportAlembic_pushButton.released.connect(self.on_exportAlembic_pushButton_released)
        self.importAlembic_pushButton.released.connect(self.on_importAlembic_pushButton_released)
        self.swapAlembic_pushButton.released.connect(self.on_swapAlembic_pushButton_released)
        
        self.addSubdivision_pushButton.released.connect(self.on_addSubdivision_pushButton_released)
        self.setSubdivision_pushButton.released.connect(self.on_setSubdivision_pushButton_released)
        self.addDomeLight_pushButton.released.connect(self.on_addDomeLight_pushButton_released)
        self.createTechPasses_pushButton.released.connect(self.on_createTechPasses_pushButton_released)
        self.addObjectID_pushButton.released.connect(self.on_addObjectID_pushButton_released)
    
    def on_exportAlembic_pushButton_released(self):
        
        #exporting alembic
        alembic.exportAlembic()
    
    def on_importAlembic_pushButton_released(self):
        
        #importing alembic
        abc=alembic.importAlembic()
        
        #undo start
        cmds.undoInfo(openChunk=True)
        
        #swapping alembic
        if abc:
            alembic.swapAlembic(abc)
        
        #undo end
        cmds.undoInfo(closeChunk=True)
    
    def on_swapAlembic_pushButton_released(self):
        
        #undo start
        cmds.undoInfo(openChunk=True)
        
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            if len(sel)==1:
                
                node=sel[0]
                
                if cmds.nodeType(node)=='AlembicNode':
                    
                    alembic.swapAlembic(node)
                else:
                    cmds.warning('%s is not a nurbsCurve!' % node)
            else:
                cmds.warning('More than one node is selected! Please select only one node.')
        else:
            
            cmds.warning('Nothing is selected! Please an Alembic node')
        
        #undo end
        cmds.undoInfo(closeChunk=True)
    
    def on_addRimLight_pushButton_released(self):
        
        import Tapp.Maya.lighting.AddRimLight as mla
        mla.addRimRamp()
    
    def on_addSubdivision_pushButton_released(self):
        
        import Tapp.Maya.lighting.vray as mlv
        mlv.addSubdivision()
    
    def on_setSubdivision_pushButton_released(self):
        
        import Tapp.Maya.lighting.vray as mlv
        level=self.subdivision_spinBox.value()
        mlv.setSubdivision(level)
    
    def on_addDomeLight_pushButton_released(self):
        
        #export alembic
        fileFilter = "HDRI (*.hdr)"
        f=cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=1,fileMode=1)
        
        if f:
            #get check box state
            state=self.domeLightCameraSpace_checkBox.checkState()
            
            if state==0:
                cameraSpace=False
            if state==2:
                cameraSpace=True
            
            import Tapp.Maya.lighting.vray as mlv
            mlv.addDomeLight(f[0], cameraSpace)
    
    def on_createTechPasses_pushButton_released(self):
        
        import Tapp.Maya.lighting.vray as mlv
        mlv.createTechPasses()
    
    def on_addObjectID_pushButton_released(self):
        
        import Tapp.Maya.lighting.vray as mlv
        mlv.addObjectID()
    
    def on_fileTextureManager_pushButton_released(self):
        
        melPath=os.path.dirname(__file__)+'/FileTextureManager.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        mel.eval('FileTextureManager')
        
def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tapp_lighting':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

#show()