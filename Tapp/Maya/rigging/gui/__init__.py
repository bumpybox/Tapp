import os
from PyQt4 import QtCore, QtGui,uic

import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import Tapp.Maya.rigging.modules as mrm
import create
import setup
import utilities

uiPath=os.path.dirname(__file__)+'/resources/gui.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)
    
class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('tmrDialog')
        self.setWindowTitle('Tapp Maya Rigging')
        
        self.create_path_lineEdit.setText(os.path.dirname(mrm.__file__))
        self.refreshList()
    
    def on_create_path_pushButton_released(self):
        self.browsePath()
    
    def on_create_path_lineEdit_returnPressed(self):
        self.refreshList()
    
    def on_create_import_pushButton_released(self):
        self.CreateImport()
    
    def on_create_export_pushButton_released(self):
        create.ExportTemplate()
    
    def on_create_mirror_pushButton_released(self):
        create.Mirror()
    
    def on_create_rig_pushButton_released(self):
        create.Rig()
    
    def on_create_character_pushButton_released(self):
        create.CreateCharacter()
    
    def on_create_delete_pushButton_released(self):
        create.Delete()
    
    def on_setup_connect_pushButton_released(self):
        setup.Connect()
    
    def on_setup_setWorld_pushButton_released(self):
        setup.SetWorld()
    
    def on_setup_createRoot_pushButton_released(self):
        setup.CreateRoot()
    
    def on_setup_exportHierarchy_pushButton_released(self):
        setup.HierarchyExport()
    
    def on_setup_importHierarchy_pushButton_released(self):
        setup.HierarchyImport()
    
    def on_setup_colorControls_pushButton_released(self):
        setup.ColorRig()
    
    def on_setup_exportControls_pushButton_released(self):
        setup.ControlsExport()
    
    def on_setup_importControls_pushButton_released(self):
        setup.ControlsImport()
    
    def on_setup_hide_pushButton_released(self):
        setup.Hide()
    
    def on_setup_unhide_pushButton_released(self):
        setup.Unhide()
    
    def on_setup_blackbox_pushButton_released(self):
        setup.Blackbox()
    
    def on_setup_unblackbox_pushButton_released(self):
        setup.Unblackbox()
    
    def on_utilities_skeletonParent_pushButton_released(self):
        utilities.SkeletonParent()
    
    def browsePath(self):
        path=cmds.fileDialog2(dialogStyle=1,fileMode=3)[0]
        self.create_path_lineEdit.setText(path)
        self.refreshList()
    
    def refreshList(self):
        path=str(self.create_path_lineEdit.text())
        
        modules = []
        for f in os.listdir(path):
            if f.endswith('.py') and f!='__init__.py':
                    modules.append(f)
        
        self.create_listWidget.clear()
        for module in modules:
            module=module.split('.')[0]
            
            self.create_listWidget.addItem(module)
    
    def CreateImport(self):
        module=str(self.create_listWidget.selectedItems()[0].text())
        
        dirPath=str(self.create_path_lineEdit.text())
        
        create.Create(module,dirPath)

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tmrDialog':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()