from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

import Tapp.Maya.lighting.region.resources.region as gui
reload(gui)
import Tapp.Maya.lighting.region.utils as utils

'''
import Tapp.utils.pyside.compileUi as upc
#uiPath=os.path.dirname(__file__)+'/resources/timing.ui'
uiPath=r'C:\Users\tokejepsen\Documents\GitHub\Tapp\Tapp\Maya\lighting\region\resources\region.ui'
upc.compileUi(uiPath)
'''

def maya_main_window():
    main_window_ptr=omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

class Window(QtGui.QMainWindow,gui.Ui_MainWindow):
    
    def __init__(self, parent=maya_main_window()):
        super(Window,self).__init__(parent)
        self.setupUi(self)
        
        self.mod_layout()
        
        self.create_connections()
    
    def mod_layout(self):
        
        nodes=utils.getRegionNode()
        
        for node in nodes:
            
            renderlayer=cmds.listConnections(node+'.renderlayer')[0]
            self.renderlayer_listWidget.addItem(renderlayer)
    
    def create_connections(self):
        
        self.renderlayer_listWidget.SelectedClicked.connect(self.on_renderlayer_pressed)
        
        self.refresh_pushButton.pressed.connect(self.refresh)
        
        self.getPreviewRegion_pushButton.pressed.connect(self.on_getPreviewRegion_pressed)
        
        self.getObjectRegion_pushButton.pressed.connect(self.on_getObjectRegion_pressed)
        
        self.connectArnold_pushButton.pressed.connect(self.on_connectArnold_pressed)
        self.disconnectArnold_pushButton.pressed.connect(self.on_disconnectArnold_pressed)
        
        self.connectPreview_pushButton.pressed.connect(self.on_connectPreview_pressed)
        self.disconnectPreview_pushButton.pressed.connect(self.on_disconnectPreview_pressed)
    
    def on_renderlayer_pressed(self):
    
    def refresh(self):
        
        self.renderlayer_listWidget.clear()
        
        nodes=utils.getRegionNode()
        
        for node in nodes:
            
            renderlayer=cmds.listConnections(node+'.renderlayer')[0]
            self.renderlayer_listWidget.addItem(renderlayer)
    
    def on_getPreviewRegion_pressed(self):
        
        utils.getRegionDraw()
    
    def on_getObjectRegion_pressed(self):
        
        utils.getMeshAnimation()
    
    def on_connectArnold_pressed(self):
        
        utils.connectArnold()
    
    def on_disconnectArnold_pressed(self):
        
        utils.disconnectArnold()
    
    def on_connectPreview_pressed(self):
        
        utils.connectPreview()
    
    def on_disconnectPreview_pressed(self):
        
        utils.disconnectPreview()

win=Window()
win.show()