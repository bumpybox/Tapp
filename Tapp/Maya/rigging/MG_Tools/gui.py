import os

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import utils

uiPath=os.path.dirname(__file__)+'/resources/ui.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('MG_Tools_dialog')
    
    def on_ps_create_pushButton_released(self):
        
        #selection failsafe
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            
            #node check
            for node in sel:
                
                shape=cmds.listRelatives(node,shapes=True)
                if cmds.nodeType(shape)=='nurbsCurve':
                    
                    #get locator amount
                    locAmount=self.ps_locators_spinBox.value()
                    
                    #get check box state
                    state=self.ps_skinCurve_checkBox.checkState()
                    
                    if state==0:
                        skinCurve=False
                    if state==2:
                        skinCurve=True
                    
                    #get check box state
                    state=self.ps_defaultValues_checkBox.checkState()
                    
                    if state==0:
                        defaultValues=False
                    if state==2:
                        defaultValues=True
                    
                    #create MG_pathSpine
                    utils.MG_pathSpine(node,locAmount,skinCurve,defaultValues)
                    
                else:
                    cmds.warning('%s is not a nurbsCurve!' % node)
        else:
            cmds.warning('Nothing is selected! Please select a curve.')

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='MG_Tools_dialog':
            widget.close()
    
    #showing new dialog
    win=Form()
    win.show()