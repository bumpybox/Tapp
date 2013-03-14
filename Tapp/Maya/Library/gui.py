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
        
        
        self.graphicsView=QtGui.QGraphicsView()
        self._scene = QtGui.QGraphicsScene()
        
        images=['c:/library/animations/dance.png']
        
        current = 0
        for image in images:
            #print current, 'of', total, os.path.basename(image)
            if os.path.isdir(image) or os.path.basename(image).startswith('.'):
                continue
            current += 1
 
            item = QdGraphicsPixmapItem(image)
            item.setPos(0, 200*current)
            self._scene.addItem(item)
 
        self._scene.setSceneRect(0, 0, 200, 200*current)
        self.graphicsView.setScene(self._scene)
        
        layout.addWidget(self.graphicsView)
    
    def on_treeView_clicked(self, index):
        indexItem = self.model.index(index.row(), 0, index.parent())

        fileName = self.model.fileName(indexItem)
        filePath = self.model.filePath(indexItem)
        
        print fileName
        print filePath

class QdGraphicsPixmapItem(QtGui.QGraphicsPixmapItem):
    def __init__(self, image, parent=None):
        QtGui.QGraphicsPixmapItem.__init__(self, parent)
        self._image = image
        self._loaded = False
        self.setFlags(self.flags() | QtGui.QGraphicsItem.ItemIsSelectable | QtGui.QGraphicsItem.ItemIsMovable )
        
    def paint(self, painter, styleopt, widget):
        if not self._loaded:
            self._loaded = True
            pixmap = QtGui.QPixmap(self._image)
            thumb = pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.setPixmap(QtGui.QPixmap(self._image).scaled(200, 200))
        QtGui.QGraphicsPixmapItem.paint(self, painter, styleopt, widget)

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tmLibrary':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

show()