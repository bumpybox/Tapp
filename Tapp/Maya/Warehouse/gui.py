from PyQt4 import QtCore, QtGui

import maya.OpenMayaUI as omu
import sip

import config

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)
    
class tmWDialog(QtGui.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)
        
        self.setObjectName('tmWDialog')
        self.setWindowTitle('Tapp Warehouse')
        
        self.createLayout()
        self.createConnections()
        
        self.getFolders()
    
    def createLayout(self):
        #main layout----------------
        main_layout=QtGui.QVBoxLayout()
        
        self.setLayout(main_layout)
        
        #type layout----------------
        type_layout=QtGui.QGridLayout()
        
        main_layout.addLayout(type_layout)
        
        #labels
        categoryLabel=QtGui.QLabel('Category')
        typeLabel=QtGui.QLabel('Type')
        
        type_layout.addWidget(categoryLabel,0,0)
        type_layout.addWidget(typeLabel,0,1)
        
        #drop down menus
        self.categoryMenu = QtGui.QComboBox()
        self.typeMenu = QtGui.QComboBox()
        
        type_layout.addWidget(self.categoryMenu,1,0)
        type_layout.addWidget(self.typeMenu,1,1)
        
        #thumbnail layout------------
        thumbnail_layout=QtGui.QGridLayout()
        
        
    
    def createConnections(self):
        pass
    
    def getFolders(self):
        
        print config['storage']

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tmWDialog':
            widget.close()
    
    #showing new dialog
    win=tmWDialog()
    win.show()

show()