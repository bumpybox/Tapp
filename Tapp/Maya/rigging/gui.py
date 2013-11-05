import os

#import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from PySide import QtGui
#from PySide import QtCore
from shiboken import wrapInstance

import Tapp.Maya.rigging.resources.rigging as gui
reload(gui)

def maya_main_window():
    main_window_ptr=omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

class Window(QtGui.QMainWindow,gui.Ui_MainWindow):
    
    def __init__(self, parent=maya_main_window()):
        super(Window,self).__init__(parent)
        self.setupUi(self)
        
        self.create_connections()
    
    def create_connections(self):
        
        self.doraSkin_pushButton.released.connect(self.doraSkin_pushButton_released)
        self.sculptInbetweenEditor_pushButton.released.connect(self.sculptInbetweenEditor_pushButton_released)
    
    def sculptInbetweenEditor_pushButton_released(self):
        
        import Tapp.Maya.rigging.utils.sculptInbetweenEditor.dslSculptInbetweenEditor as dsl
        create=dsl.SculptInbetweenEditor()
        create.ui()
    
    def doraSkin_pushButton_released(self):
        
        path=os.path.dirname(__file__)
        
        #sourcing dora util
        melPath=path+'/utils/DoraSkinWeightImpExp.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        #launching dora gui
        mel.eval('DoraSkinWeightImpExp()')

def show():
    #showing new dialog
    win=Window()
    win.show()