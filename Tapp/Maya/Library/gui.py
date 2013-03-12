#import os
#import sys

from PyQt4 import QtGui
from PyQt4 import QtCore
#from PyQt4 import uic
#import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

#import Tapp.Maya.Library.config as mlc

#uiPath=os.path.dirname(mlc.__file__)+'/ui.ui'
#form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(QtGui.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)

        self.treeView=QtGui.QTreeView(parent=self)
        
        self.setObjectName('tmLibrary')
        
        self.setFixedHeight(500)
        self.setFixedWidth(500)
        
        self.model = QtGui.QFileSystemModel()
        
        root=self.model.setRootPath('c:/temp')
        
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(root)
        
        self.treeView.setHeaderHidden(True)
        self.treeView.setColumnHidden(1,True)
        self.treeView.setColumnHidden(2,True)
        self.treeView.setColumnHidden(3,True)
        
        self.treeView.clicked.connect(self.on_treeView_clicked)
    
    def on_treeView_clicked(self, index):
        indexItem = self.model.index(index.row(), 0, index.parent())

        fileName = self.model.fileName(indexItem)
        filePath = self.model.filePath(indexItem)
        
        print fileName
        print filePath

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tmLibrary':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

show()