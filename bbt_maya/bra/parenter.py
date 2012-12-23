from PyQt4.QtCore import *
from PyQt4.QtGui import *

import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

from bbt_maya.brt import utils

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QObject)

class parentDialog(QDialog):
    
    def __init__(self, parent=maya_main_window()):
        QDialog.__init__(self, parent)
        
        self.setObjectName('parentDialog')
        self.setWindowTitle('Parenter')
        
        self.createLayout()
    
    def createLayout(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        meta=utils.meta()
        data=meta.getHierarchies()
        
        self.model = QStandardItemModel()

        for node in data['None']:
            parentItem = self.model.invisibleRootItem()
            
            item = QStandardItem(QString(node))
            parentItem.appendRow(item)

        self.view = QTreeView()
        self.view.setModel(self.model)
        self.view.setDragDropMode(QAbstractItemView.InternalMove)
        
        self.main_layout.addWidget(self.view)

def show():
    #closing previous dialog
    for widget in qApp.allWidgets():
        if widget.objectName()=='parentDialog':
            widget.close()
    
    #showing new dialog
    win=parentDialog()
    win.show()

show()