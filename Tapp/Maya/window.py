from PyQt4 import QtCore, QtGui
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

import Tapp.Maya.lighting.gui as lighting
import Tapp.Maya.animation.gui as animation
#import Tapp.Maya.rigging.gui as rigging
import Tapp.Maya.modelling.gui as modelling

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Window(QtGui.QDialog):
    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)
        
        self.setObjectName('tapp')
        
        main_layout = QtGui.QVBoxLayout()
        self.setLayout(main_layout)
        
        main_tabs = QtGui.QTabWidget()
        main_layout.addWidget(main_tabs)
        
        main_tabs.addTab(modelling.Form(), 'Modelling')
        #main_tabs.addTab(rigging.Form(), 'Rigging')
        main_tabs.addTab(animation.Form(), 'Animation')
        main_tabs.addTab(lighting.Form(), 'Lighting')
        

def show():
    #delete previous ui
    if cmds.dockControl('tapp',exists=True):
        cmds.deleteUI('tapp')
    
    #workaround to create dock control with dialog
    slider = cmds.floatSlider()
    dock = cmds.dockControl('tapp',label='Tapp Tools',content=slider, area='right')
    dockPt = omu.MQtUtil.findControl(dock)
    dockWidget = sip.wrapinstance(long(dockPt), QtCore.QObject)
    dockWidget.setWidget(Window())

#show()