import os

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omu
import sip

uiPath=os.path.dirname(__file__)
#form,base=uic.loadUiType(uiPath)

print uiPath
'''
# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('MGdialog')

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='MGdialog':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()

show()
'''