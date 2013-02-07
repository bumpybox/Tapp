import os
import sys
from PyQt4 import QtCore, QtGui

import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import modules

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
        
        self.setFixedSize(287,371)
        
        self.create_pathLineEdit.setText(os.path.dirname(__file__).replace('\\','/')+'/modules')
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
        
        #control shapes
        gb=QtGui.QGroupBox(title='Control Shapes')
        gb_layout=QtGui.QHBoxLayout()
        
        self.setup_controlExportButton=QtGui.QPushButton('Export')
        self.setup_controlImportButton=QtGui.QPushButton('Import')
        
        gb_layout.addWidget(self.setup_controlExportButton)
        gb_layout.addWidget(self.setup_controlImportButton)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #control shapes
        gb=QtGui.QGroupBox(title='Hierarchy')
        gb_layout=QtGui.QHBoxLayout()
        
        self.setup_hierarchyExportButton=QtGui.QPushButton('Export')
        self.setup_hierarchyImportButton=QtGui.QPushButton('Import')
        
        gb_layout.addWidget(self.setup_hierarchyExportButton)
        gb_layout.addWidget(self.setup_hierarchyImportButton)
        
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
        self.utils_sphereRemoveButton=QtGui.QPushButton('Remove All')
        
        gb_layout.addWidget(self.utils_sphereCreateButton)
        gb_layout.addWidget(self.utils_sphereRemoveButton)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #weights maps
        gb=QtGui.QGroupBox(title='Weight Maps')
        gb_layout=QtGui.QHBoxLayout()
        
        self.utils_weightImportButton=QtGui.QPushButton('Import')
        self.utils_weightExportButton=QtGui.QPushButton('Export')
        
        gb_layout.addWidget(self.utils_weightImportButton)
        gb_layout.addWidget(self.utils_weightExportButton)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #proxy parent
        self.utils_proxyParentButton=QtGui.QPushButton('Proxy Parent')
        
        tab_layout.addWidget(self.utils_proxyParentButton)
        
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
        #///character connections///
        self.connect(self.create_pathButton, QtCore.SIGNAL('clicked()'),self.browsePath)
        self.connect(self.create_pathLineEdit, QtCore.SIGNAL('returnPressed()'),self.refreshList)
        self.connect(self.create_importButton, QtCore.SIGNAL('clicked()'),self.CreateImport)
    
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
            self.create_moduleList.addItem(module)
    
    def CreateImport(self):
        path=str(self.create_pathLineEdit.text())
        modulePath=str(self.create_moduleList.selectedItems()[0].text())
        
        self.__createImport__(path+'/'+modulePath)
        
        modules.Create()
    
    def __createImport__(self,modulePath):
        f = os.path.basename( modulePath )
        d = os.path.dirname( modulePath )
     
        toks = f.split( '.' )
        modname = toks[0]
     
        # Check if dirrectory is really a directory
        if( os.path.exists( d ) ):
     
        # Check if the file directory already exists in the sys.path array
            paths = sys.path
            pathfound = 0
            for path in paths:
                if(d == path):
                    pathfound = 1
     
        # If the dirrectory is not part of sys.path add it
            if not pathfound:
                sys.path.append( d )
     
        # exec works like MEL's eval but you need to add in globals() 
        # at the end to make sure the file is imported into the global 
        # namespace else it will only be in the scope of this function
        exec ('import ' + modname+' as modules') in globals()

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tmrDialog':
            widget.close()
    
    #showing new dialog
    win=tmrDialog()
    win.show()