import os
import sys

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import Tapp.Maya.Library.config as mlc

uiPath=os.path.dirname(mlc.__file__)+'/ui.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('tmLibrary')
        self.treeWidget.addTopLevelItem()

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='tmLibrary':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

show()