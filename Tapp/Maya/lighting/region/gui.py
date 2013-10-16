from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

import Tapp.Maya.lighting.region.resources.region as gui
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
        
        pass
    
    def create_connections(self):
        
        self.getPreviewRegion_pushButton.pressed.connect(self.on_getPreviewRgion_pressed)

win=Window()
win.show()