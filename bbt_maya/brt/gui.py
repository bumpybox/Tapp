import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QObject)
    
class brtDialog(QDialog):
    
    def __init__(self, parent=maya_main_window()):
        QDialog.__init__(self, parent)
        
        self.setObjectName('brtDialog')
        self.setWindowTitle('Bumpybox Rigging Tools')
        
        self.createLayout()
        self.createConnections()
        
        self.setFixedSize(287,371)
    
    def createLayout(self):
        #///create create tab///
        create_tab=QWidget()
        
        #tab layout
        tab_layout=QGridLayout()
        create_tab.setLayout(tab_layout)
        
        #list widget
        self.create_templateList=QListWidget()
        tab_layout.addWidget(self.create_templateList,0,0,1,2)
        
        #path browser       
        self.create_pathButton=QPushButton('Path:')
        self.create_pathLineEdit=QLineEdit()
        
        tab_layout.addWidget(self.create_pathButton,1,0)
        tab_layout.addWidget(self.create_pathLineEdit,1,1)
        
        #buttons
        self.create_importButton=QPushButton('Import')
        self.create_exportButton=QPushButton('Export')
        self.create_deleteButton=QPushButton('Delete')
        self.create_mirrorButton=QPushButton('Mirror')
        self.create_rigButton=QPushButton('Create Rig')
        self.create_characterButton=QPushButton('Create Character')
        
        tab_layout.addWidget(self.create_importButton,2,0)
        tab_layout.addWidget(self.create_exportButton,2,1)
        tab_layout.addWidget(self.create_deleteButton,3,0)
        tab_layout.addWidget(self.create_mirrorButton,3,1)
        tab_layout.addWidget(self.create_rigButton,4,0)
        tab_layout.addWidget(self.create_characterButton,4,1)
        
        #///create setup tab///
        setup_tab=QWidget()
        
        #tab layout
        tab_layout=QVBoxLayout()
        setup_tab.setLayout(tab_layout)
        
        #connect modules
        gb=QGroupBox(title='Connect Modules')
        gb_layout=QHBoxLayout()
        
        self.setup_connectButton=QPushButton('Connect')
        label=QLabel('Select targets first.\nSelect parent last.')
        
        gb_layout.addWidget(self.setup_connectButton)
        gb_layout.addWidget(label)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #control shapes
        gb=QGroupBox(title='Control Shapes')
        gb_layout=QHBoxLayout()
        
        self.setup_controlExportButton=QPushButton('Export')
        self.setup_controlImportButton=QPushButton('Import')
        
        gb_layout.addWidget(self.setup_controlExportButton)
        gb_layout.addWidget(self.setup_controlImportButton)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #control shapes
        gb=QGroupBox(title='Hierarchy')
        gb_layout=QHBoxLayout()
        
        self.setup_hierarchyExportButton=QPushButton('Export')
        self.setup_hierarchyImportButton=QPushButton('Import')
        
        gb_layout.addWidget(self.setup_hierarchyExportButton)
        gb_layout.addWidget(self.setup_hierarchyImportButton)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #control shapes
        gb=QGroupBox(title='Rig Preparation')
        gb_layout=QGridLayout()
        
        self.setup_hideRigButton=QPushButton('Hide')
        self.setup_unhideRigButton=QPushButton('Unhide')
        self.setup_blackboxRigButton=QPushButton('Blackbox')
        self.setup_unblackboxRigButton=QPushButton('Unblackbox')
        
        gb_layout.addWidget(self.setup_hideRigButton,0,0)
        gb_layout.addWidget(self.setup_unhideRigButton,0,1)
        gb_layout.addWidget(self.setup_blackboxRigButton,1,0)
        gb_layout.addWidget(self.setup_unblackboxRigButton,1,1)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #///create utils tab///
        utils_tab=QWidget()
        
        #tab layout
        tab_layout=QVBoxLayout()
        utils_tab.setLayout(tab_layout)
        
        #sphere preview
        gb=QGroupBox(title='Sphere Preview')
        gb_layout=QHBoxLayout()
        
        self.utils_sphereCreateButton=QPushButton('Create')
        self.utils_sphereRemoveButton=QPushButton('Remove All')
        
        gb_layout.addWidget(self.utils_sphereCreateButton)
        gb_layout.addWidget(self.utils_sphereRemoveButton)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #weights maps
        gb=QGroupBox(title='Weight Maps')
        gb_layout=QHBoxLayout()
        
        self.utils_weightImportButton=QPushButton('Import')
        self.utils_weightExportButton=QPushButton('Export')
        
        gb_layout.addWidget(self.utils_weightImportButton)
        gb_layout.addWidget(self.utils_weightExportButton)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #proxy parent
        self.utils_proxyParentButton=QPushButton('Proxy Parent')
        
        tab_layout.addWidget(self.utils_proxyParentButton)
        
        #create main tabs
        tabs=QVBoxLayout()
        
        main_tabs = QTabWidget()
        tabs.addWidget(main_tabs)
        main_tabs.addTab(create_tab, 'Create')
        main_tabs.addTab(setup_tab, 'Setup')
        main_tabs.addTab(utils_tab, 'Utilities')
        
        # Create the main layout
        main_layout = QVBoxLayout()
        main_layout.setMargin(2)
        
        scrollArea=QScrollArea()
        scrollArea.setLayout(tabs)
        scrollArea.setWidget(main_tabs)
        
        main_layout.addWidget(scrollArea)
        
        self.setLayout(main_layout)
    
    def createConnections(self):
        #///character connections///
        self.connect(self.create_pathButton, SIGNAL('clicked()'),self.browsePath)
        self.connect(self.create_pathLineEdit, SIGNAL('returnPressed()'),self.refreshList)
    
    def browsePath(self):
        templatePath=cmds.fileDialog2(dialogStyle=1,fileMode=3)[0]
        self.create_pathLineEdit.setText(templatePath)
        self.refreshList()
    
    def refreshList(self):
        directory=str(self.create_pathLineEdit.text())
        
        templates = []
        for root, dirs, files in os.walk(directory):
            for name in files:
                path = os.path.join(root, name)
                if name.endswith('.template'):
                    templates.append(name)
        
        self.create_templateList.clear()
        for item in templates:
            self.create_templateList.addItem(item)

def show():
    #closing previous dialog
    for widget in qApp.allWidgets():
        if widget.objectName()=='brtDialog':
            widget.close()
    
    #showing new dialog
    win=brtDialog()
    win.show()