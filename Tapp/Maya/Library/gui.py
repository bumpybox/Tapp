import os
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
        
        layout=QtGui.QVBoxLayout()
        self.setLayout(layout)
        
        self.treeView=QtGui.QTreeView(parent=self)
        
        self.setObjectName('tmLibrary')
        self.setWindowTitle('Tapp Library')
        
        self.setFixedHeight(500)
        self.setFixedWidth(500)
        
        self.model = QtGui.QFileSystemModel()
        self.model.setFilter(QtCore.QDir.Dirs|QtCore.QDir.NoDotAndDotDot)
        
        root=self.model.setRootPath('c:/library')
        
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(root)
        
        self.treeView.setHeaderHidden(True)
        self.treeView.setColumnHidden(1,True)
        self.treeView.setColumnHidden(2,True)
        self.treeView.setColumnHidden(3,True)
        
        layout.addWidget(self.treeView)
        
        self.treeView.clicked.connect(self.on_treeView_clicked)
        
        #------------------------------------------
        
        self.listwidget=QtGui.QListWidget()
        self.listwidget.setViewMode(QtGui.QListView.IconMode)
        self.listwidget.setMovement(QtGui.QListView.Static)
        self.listwidget.setIconSize(QtCore.QSize(100,100))
        
        self.listwidget.doubleClicked.connect(self.on_listwidget_doubleclicked)
        
        layout.addWidget(self.listwidget)
        
        #------------------------------------------
        
        self.thumbslider=QtGui.QSlider()
        self.thumbslider.setOrientation(QtCore.Qt.Horizontal)
        
        self.thumbslider.valueChanged.connect(self.on_thumbslider_changed)
        
        layout.addWidget(self.thumbslider)
        
        #--------------------------------------------
        
        
    
    def on_listwidget_doubleclicked(self):
        
        itemtext=self.listwidget.currentItem().text()
        
        indexItem = self.treeView.selectedIndexes()[0]
        
        filePath = self.model.filePath(indexItem)
        
        f=filePath+'/'+itemtext+'.mov'
        os.startfile(f)
    
    def on_thumbslider_changed(self):
        
        value=self.thumbslider.value()
        self.listwidget.setIconSize(QtCore.QSize(100+value,100+value))
    
    def on_treeView_clicked(self, index):
        self.listwidget.clear()
        
        indexItem = self.model.index(index.row(), 0, index.parent())
        
        filePath = self.model.filePath(indexItem)
        
        items=[]
        for f in os.listdir(filePath):
            
            if len(f.split('.'))>1:
                
                items.append(f.split('.')[0])
        
        filterItems=set(items)
        for f in filterItems:
            
            item = QtGui.QListWidgetItem(f)
            
            image=filePath+'/'+f+'.png'
            icon=QtGui.QIcon()
            icon.addFile(image)
            item.setIcon(icon)
            
            self.listwidget.addItem(item)

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tmLibrary':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

show()