from PySide import QtGui
import shiboken

import maya.cmds as cmds
import maya.OpenMayaUI as omu
import pymel.core as pmc

import Tapp.Maya.lighting.gui as lighting
import Tapp.Maya.animation.gui as animation
#import Tapp.Maya.rigging.gui as rigging
import Tapp.Maya.modelling.gui as modelling

def maya_main_window():
    """
    Get the main Maya window as a QtGui.QMainWindow instance
    @return: QtGui.QMainWindow instance of the top level Maya windows
    """
    ptr = omu.MQtUtil.mainWindow()
    if ptr is not None:
        return shiboken.wrapInstance(long(ptr), QtGui.QMainWindow)

class Window(QtGui.QDialog):
    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)
        
        self.setObjectName('tappDialog')
        
        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)
        
        self.main_tabs = QtGui.QTabWidget()
        self.main_layout.addWidget(self.main_tabs)
        
        self.main_tabs.addTab(modelling.Form(), 'Modelling')
        #main_tabs.addTab(rigging.Form(), 'Rigging')
        self.main_tabs.addTab(animation.Form(), 'Animation')
        self.main_tabs.addTab(lighting.Form(), 'Lighting')

def show():
    #delete previous ui
    if cmds.dockControl('tappWindow',exists=True):
        cmds.deleteUI('tappWindow')

    #creating ui
    Window()
    cmds.dockControl('tappWindow',content='tappDialog', area='right',label='Tapp')
    

#show()
