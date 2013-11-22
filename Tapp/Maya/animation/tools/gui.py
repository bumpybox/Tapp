import os

from PySide import QtGui
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

#from .resources import dialog as dialog
#from .setsSelector import gui as ssGui

import Tapp.Maya.animation.tools.resources.dialog as dialog
import Tapp.Maya.animation.tools.setsSelector.gui as ssGui

#rebuild ui
#import Tapp.utils.pyside.compileUi as upc
#uiPath=os.path.dirname(dialog.__file__)+'/dialog.ui'
#upc.compileUi(uiPath)
#reload(dialog)

def maya_main_window():
    main_window_ptr=omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

class Window(QtGui.QMainWindow,dialog.Ui_MainWindow):
    
    def __init__(self, parent=maya_main_window()):
        super(Window,self).__init__(parent)
        self.setupUi(self)
        
        self.modify_dialog()
        
        self.create_connections()
    
    def modify_dialog(self):
        
        #adding Sets Selector to dialog
        layout=self.centralwidget.layout()
        layout.addWidget(ssGui.Window())
    
    def create_connections(self):
        
        self.zvParentMaster_pushButton.released.connect(self.zvParentMaster_pushButton_released)
        self.zvChain_pushButton.released.connect(self.zvChain_pushButton_released)
        self.zvParentMasterHelp_pushButton.released.connect(self.zvParentMasterHelp_pushButton_released)
        
        self.breakDownDragger_pushButton.released.connect(self.breakDownDragger_pushButton_released)
        self.breakDownDraggerHelp_pushButton.released.connect(self.breakDownDraggerHelp_pushButton_released)
        
        self.holdKey_pushButton.released.connect(self.holdKey_pushButton_released)
        self.holdKeyHelp_pushButton.released.connect(self.holdKeyHelp_pushButton_released)
        
        self.keyValueDragger_pushButton.released.connect(self.keyValueDragger_pushButton_released)
        self.keyValueDraggerHelp_pushButton.released.connect(self.keyValueDraggerHelp_pushButton_released)
        
        self.keyCleanUp_pushButton.released.connect(self.keyCleanUp_pushButton_released)
        self.keyCleanUpHelp_pushButton.released.connect(self.keyCleanUpHelp_pushButton_released)
        
        self.changeRotationOrder_pushButton.released.connect(self.changeRotationOrder_pushButton_released)
        self.changeRotationOrderHelp_pushButton.released.connect(self.changeRotationOrderHelp_pushButton_released)
        
        self.ghosting_pushButton.released.connect(self.ghosting_pushButton_released)
        self.ghostingHelp_pushButton.released.connect(self.ghostingHelp_pushButton_released)
        
        self.localizeImagePlane_pushButton.released.connect(self.localizeImagePlane_pushButton_released)
        
        self.rat_pushButton.released.connect(self.rat_pushButton_released)
        
        self.paie_pushButton.released.connect(self.paie_pushButton_released)
        
        self.collisionDeformer_pushButton.released.connect(self.collisionDeformer_released)
    
    def collisionDeformer_released(self):
        
        cmds.loadPlugin('jlCollisionDeformer.py',quiet=True)
        
        try:
            mel.eval('jlCollisionDeformer()')
        except:
            cmds.warning('First select the collider mesh then the mesh that should be deformed.')
    
    def zvChain_pushButton_released(self):
        
        #undo enable
        cmds.undoInfo(openChunk=True)
        
        muz.attach_chain()
        
        cmds.undoInfo(closeChunk=True)
    
    def localizeImagePlane_pushButton_released(self):
        
        import Tapp.Maya.animation.utils.imageplane as ip
        
        ip.localizeImagePlane()
    
    def paie_released(self):
        
        paie.GUI()