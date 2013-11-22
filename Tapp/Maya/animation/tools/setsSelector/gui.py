import os

from PySide import QtGui
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

from .resources import dialog as dialog

#rebuild ui
import Tapp.utils.pyside.compileUi as upc
uiPath=os.path.dirname(dialog.__file__)+'/dialog.ui'
upc.compileUi(uiPath)
reload(dialog)

def maya_main_window():
    main_window_ptr=omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

class Window(QtGui.QMainWindow,dialog.Ui_MainWindow):
    
    def __init__(self, parent=maya_main_window()):
        super(Window,self).__init__(parent)
        self.setupUi(self)
        
        self.modify_dialog()
        
        self.refresh()
        
        self.create_connections()
    
    def modify_dialog(self):
        
        pass
    
    def refresh(self):
        
        #populate list
        if self.getSets():
            self.listWidget.addItems(self.getSets())
    
    def create_connections(self):
        
        self.listWidget.itemSelectionChanged.connect(self.on_listWidget_itemSelectionChanged)
        
        self.pushButton.released.connect(self.on_pushButton_released)
    
    def on_pushButton_released(self):
        
        self.refresh()
    
    def on_listWidget_itemSelectionChanged(self):
        
        sets=[]
        for item in self.listWidget.selectedItems():
            
            sets.append(item.text())
        
        cmds.select(sets)
    
    def getSets(self):
        
        objectSets=[]
        for node in cmds.ls(transforms=True):
            
            sets=cmds.listSets(object=node)
            if sets:
                objectSets.extend(sets)
        
        return list(set(objectSets))