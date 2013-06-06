import os

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omu
import sip

import Tapp.Maya.lighting.alembic as alembic

uiPath=os.path.dirname(__file__)+'/resources/lighting_gui.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('tapp_lighting')
    
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