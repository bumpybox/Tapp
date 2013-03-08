import os
import sys
from PyQt4 import QtCore, QtGui

import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import Tapp.Maya.rigging.modules as mrm
import create
import setup
import utilities

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)
    
class tmrDialog(QtGui.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)
        
        self.setObjectName('tmrDialog')
        self.setWindowTitle('Tapp Maya Rigging')
        
        self.createLayout()
        self.createConnections()
        
        self.setFixedSize(287,471)
        
        self.create_pathLineEdit.setText(os.path.dirname(mrm.__file__))
        self.refreshList()
    
    def createLayout(self):
        #///create create tab///
        create_tab=QtGui.QWidget()
        
        #tab layout
        tab_layout=QtGui.QGridLayout()
        create_tab.setLayout(tab_layout)
        
        #list widget
        self.create_moduleList=QtGui.QListWidget()
        tab_layout.addWidget(self.create_moduleList,0,0,1,2)
        
        #path browser       
        self.create_pathButton=QtGui.QPushButton('Path:')
        self.create_pathLineEdit=QtGui.QLineEdit()
        
        tab_layout.addWidget(self.create_pathButton,1,0)
        tab_layout.addWidget(self.create_pathLineEdit,1,1)
        
        #buttons
        self.create_importButton=QtGui.QPushButton('Import')
        self.create_exportButton=QtGui.QPushButton('Export')
        self.create_deleteButton=QtGui.QPushButton('Delete')
        self.create_mirrorButton=QtGui.QPushButton('Mirror')
        self.create_mirrorButton.setEnabled(False)
        self.create_rigButton=QtGui.QPushButton('Create Rig')
        self.create_characterButton=QtGui.QPushButton('Create Character')
        
        tab_layout.addWidget(self.create_importButton,2,0)
        tab_layout.addWidget(self.create_exportButton,2,1)
        tab_layout.addWidget(self.create_deleteButton,3,0)
        tab_layout.addWidget(self.create_mirrorButton,3,1)
        tab_layout.addWidget(self.create_rigButton,4,0)
        tab_layout.addWidget(self.create_characterButton,4,1)
        
        #///create setup tab///
        setup_tab=QtGui.QWidget()
        
        #tab layout
        tab_layout=QtGui.QVBoxLayout()
        setup_tab.setLayout(tab_layout)
        
        #connect modules
        gb=QtGui.QGroupBox(title='Connect Modules')
        gb_layout=QtGui.QHBoxLayout()
        
        self.setup_connectButton=QtGui.QPushButton('Connect')
        label=QtGui.QLabel('Select targets first.\nSelect parent last.')
        
        gb_layout.addWidget(self.setup_connectButton)
        gb_layout.addWidget(label)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #utilities
        gb=QtGui.QGroupBox(title='Utilities')
        gb_layout=QtGui.QHBoxLayout()
        
        self.setup_setWorld=QtGui.QPushButton('Set World')
        self.setup_createRoot=QtGui.QPushButton('Create Root')
        
        gb_layout.addWidget(self.setup_setWorld)
        gb_layout.addWidget(self.setup_createRoot)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #hierarchy
        gb=QtGui.QGroupBox(title='Hierarchy')
        gb_layout=QtGui.QHBoxLayout()
        
        self.setup_hierarchyExportButton=QtGui.QPushButton('Export')
        self.setup_hierarchyImportButton=QtGui.QPushButton('Import')
        
        gb_layout.addWidget(self.setup_hierarchyExportButton)
        gb_layout.addWidget(self.setup_hierarchyImportButton)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #control shapes
        gb=QtGui.QGroupBox(title='Controls')
        gb_layout=QtGui.QVBoxLayout()
        
        self.setup_controlColorButton=QtGui.QPushButton('Color Controls')
        self.setup_controlExportButton=QtGui.QPushButton('Export')
        self.setup_controlImportButton=QtGui.QPushButton('Import')
        
        gb_layout.addWidget(self.setup_controlColorButton)
        
        layout=QtGui.QHBoxLayout()
        layout.addWidget(self.setup_controlExportButton)
        layout.addWidget(self.setup_controlImportButton)
        gb_layout.addLayout(layout)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #control shapes
        gb=QtGui.QGroupBox(title='Rig Preparation')
        gb_layout=QtGui.QGridLayout()
        
        self.setup_hideRigButton=QtGui.QPushButton('Hide')
        self.setup_unhideRigButton=QtGui.QPushButton('Unhide')
        self.setup_blackboxRigButton=QtGui.QPushButton('Blackbox')
        self.setup_unblackboxRigButton=QtGui.QPushButton('Unblackbox')
        
        gb_layout.addWidget(self.setup_hideRigButton,0,0)
        gb_layout.addWidget(self.setup_unhideRigButton,0,1)
        gb_layout.addWidget(self.setup_blackboxRigButton,1,0)
        gb_layout.addWidget(self.setup_unblackboxRigButton,1,1)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #///create utils tab///
        utils_tab=QtGui.QWidget()
        
        #tab layout
        tab_layout=QtGui.QVBoxLayout()
        utils_tab.setLayout(tab_layout)
        
        #sphere preview
        gb=QtGui.QGroupBox(title='Sphere Preview')
        gb_layout=QtGui.QHBoxLayout()
        
        self.utils_sphereCreateButton=QtGui.QPushButton('Create')
        self.utils_sphereCreateButton.setEnabled(False)
        self.utils_sphereRemoveButton=QtGui.QPushButton('Remove All')
        self.utils_sphereRemoveButton.setEnabled(False)
        
        gb_layout.addWidget(self.utils_sphereCreateButton)
        gb_layout.addWidget(self.utils_sphereRemoveButton)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #weights maps
        gb=QtGui.QGroupBox(title='Weight Maps')
        gb_layout=QtGui.QHBoxLayout()
        
        self.utils_weightImportButton=QtGui.QPushButton('Import')
        self.utils_weightImportButton.setEnabled(False)
        self.utils_weightExportButton=QtGui.QPushButton('Export')
        self.utils_weightExportButton.setEnabled(False)
        
        gb_layout.addWidget(self.utils_weightImportButton)
        gb_layout.addWidget(self.utils_weightExportButton)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #skeleton parent
        self.utils_skeletonParentButton=QtGui.QPushButton('Skeleton Parent')
        
        tab_layout.addWidget(self.utils_skeletonParentButton)
        
        #create main tabs
        tabs=QtGui.QVBoxLayout()
        
        main_tabs = QtGui.QTabWidget()
        tabs.addWidget(main_tabs)
        main_tabs.addTab(create_tab, 'Create')
        main_tabs.addTab(setup_tab, 'Setup')
        main_tabs.addTab(utils_tab, 'Utilities')
        
        # Create the main layout
        main_layout = QtGui.QVBoxLayout()
        main_layout.setMargin(2)
        
        scrollArea=QtGui.QScrollArea()
        scrollArea.setLayout(tabs)
        scrollArea.setWidget(main_tabs)
        
        main_layout.addWidget(scrollArea)
        
        self.setLayout(main_layout)
    
    def createConnections(self):
        #///create connections///
        self.connect(self.create_pathButton, QtCore.SIGNAL('clicked()'),self.browsePath)
        self.connect(self.create_pathLineEdit, QtCore.SIGNAL('returnPressed()'),self.refreshList)
        self.connect(self.create_importButton, QtCore.SIGNAL('clicked()'),self.CreateImport)
        self.connect(self.create_exportButton, QtCore.SIGNAL('clicked()'),create.ExportTemplate)
        self.connect(self.create_rigButton, QtCore.SIGNAL('clicked()'),create.Rig)
        self.connect(self.create_characterButton, QtCore.SIGNAL('clicked()'),create.CreateCharacter)
        self.connect(self.create_deleteButton, QtCore.SIGNAL('clicked()'),create.Delete)
        
        #///setup connections///
        self.connect(self.setup_connectButton, QtCore.SIGNAL('clicked()'),setup.Connect)
        self.connect(self.setup_hideRigButton, QtCore.SIGNAL('clicked()'),setup.Hide)
        self.connect(self.setup_unhideRigButton, QtCore.SIGNAL('clicked()'),setup.Unhide)
        self.connect(self.setup_blackboxRigButton, QtCore.SIGNAL('clicked()'),setup.Blackbox)
        self.connect(self.setup_unblackboxRigButton, QtCore.SIGNAL('clicked()'),setup.Unblackbox)
        self.connect(self.setup_setWorld, QtCore.SIGNAL('clicked()'),setup.SetWorld)
        self.connect(self.setup_createRoot, QtCore.SIGNAL('clicked()'),setup.CreateRoot)
        self.connect(self.setup_hierarchyImportButton, QtCore.SIGNAL('clicked()'),setup.HierarchyImport)
        self.connect(self.setup_hierarchyExportButton, QtCore.SIGNAL('clicked()'),setup.HierarchyExport)
        self.connect(self.setup_controlExportButton, QtCore.SIGNAL('clicked()'),setup.ControlsExport)
        self.connect(self.setup_controlImportButton, QtCore.SIGNAL('clicked()'),setup.ControlsImport)
        self.connect(self.setup_controlColorButton, QtCore.SIGNAL('clicked()'),setup.ColorRig)
        
        #///setup utilities///
        self.connect(self.utils_skeletonParentButton, QtCore.SIGNAL('clicked()'),utilities.SkeletonParent)
    
    def browsePath(self):
        path=cmds.fileDialog2(dialogStyle=1,fileMode=3)[0]
        self.create_pathLineEdit.setText(path)
        self.refreshList()
    
    def refreshList(self):
        path=str(self.create_pathLineEdit.text())
        
        modules = []
        for f in os.listdir(path):
            if f.endswith('.py') and f!='__init__.py':
                    modules.append(f)
        
        self.create_moduleList.clear()
        for module in modules:
            module=module.split('.')[0]
            
            self.create_moduleList.addItem(module)
    
    def CreateImport(self):
        module=str(self.create_moduleList.selectedItems()[0].text())
        
        dirPath=str(self.create_pathLineEdit.text())
        
        create.Create(module,dirPath)

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tmrDialog':
            widget.close()
    
    #showing new dialog
    win=tmrDialog()
    win.show()