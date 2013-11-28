import os
import webbrowser

from PySide import QtGui
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

import Tapp.Maya.animation.tools.resources.dialog as dialog
import Tapp.Maya.animation.tools.setsSelector.gui as ssGui
import Tapp.Maya.utils.ZvParentMaster as muz
import Tapp.Maya.animation.utils.ml_breakdownDragger as maumlb
import Tapp.Maya.animation.utils.ml_hold as maumlh
import Tapp.Maya.animation.utils.ml_keyValueDragger as maumlk
import Tapp.Maya.animation.utils as mau

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
    
    def zvParentMaster_pushButton_released(self):
        
        muz.ZvParentMaster()
    
    def zvChain_pushButton_released(self):
        
        #undo enable
        cmds.undoInfo(openChunk=True)
        
        muz.attach_chain()
        
        cmds.undoInfo(closeChunk=True)
    
    def zvParentMasterHelp_pushButton_released(self):
        
        webbrowser.open('http://www.creativecrash.com/maya/script/zv-parent-master')
    
    def localizeImagePlane_pushButton_released(self):
        
        import Tapp.Maya.animation.utils.imageplane as ip
        
        ip.localizeImagePlane()
    
    def paie_pushButton_released(self):
        
        from ..utils import paie as paie
        
        paie.GUI()
    
    def breakDownDragger_pushButton_released(self):
        
        maumlb.drag()
    
    def breakDownDraggerHelp_pushButton_released(self):
        
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_breakdownDragger')
    
    def holdKey_pushButton_released(self):
        
        maumlh.ui()
    
    def holdKeyHelp_pushButton_released(self):
        
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_hold')
    
    def keyValueDragger_pushButton_released(self):
        
        maumlk.drag()
    
    def keyValueDraggerHelp_pushButton_released(self):
        
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_keyValueDragger')
    
    def keyCleanUp_pushButton_released(self):
        
        cmds.undoInfo(openChunk=True)
        
        #execute redundant keys script
        path=os.path.dirname(mau.__file__).replace('\\','/')
        
        mel.eval('source "'+path+'/deleteRedundantKeys.mel"')
        mel.eval('llDeleteRedundantKeys;')
        
        #deleting static channels in scene or on selected object
        sel=cmds.ls(selection=True)
        
        if len(sel)>0:
            cmds.delete(staticChannels=True)
        else:
            cmds.delete(staticChannels=True,all=True)
        
        cmds.undoInfo(closeChunk=True)
    
    def keyCleanUpHelp_pushButton_released(self):
        
        msg='This cleans any static channels and redundant keys.\n'
        msg+='If nothing is selected, everything in the scene gets cleaned.'
        
        cmds.confirmDialog( title='Key Clean Up Info', message=msg,defaultButton='OK')
    
    def changeRotationOrder_pushButton_released(self):
        
        path=os.path.dirname(__file__)
        parentDir=os.path.abspath(os.path.join(path, os.pardir))
        
        #sourcing zoo utils
        melPath=parentDir+'/animation/utils/zooUtils.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        #sourcing zoo change
        melPath=parentDir+'/animation/utils/zooChangeRoo.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        mel.eval('zooChangeRoo %s' % self.tools_changeRotationOrder_comboBox.currentText())
    
    def changeRotationOrderHelp_pushButton_released(self):
        
        webbrowser.open('http://www.creativecrash.com/maya/script/zoochangeroo')
    
    def ghosting_pushButton_released(self):
        
        path=os.path.dirname(__file__)
        parentDir=os.path.abspath(os.path.join(path, os.pardir))
        
        #sourcing ghost util
        melPath=parentDir+'/animation/utils/bhGhost.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        mel.eval('bhGhost')
    
    def ghostingHelp_pushButton_released(self):
        
        webbrowser.open('https://vimeo.com/50029607')
    
    def rat_pushButton_released(self):
        
        path=os.path.dirname(__file__)
        parentDir=os.path.abspath(os.path.join(path, os.pardir))
        
        #sourcing rat util
        melPath=parentDir+'/animation/utils/RAT.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        #launching rat gui
        uiPath=parentDir+'/animation/utils/RAT_ui.ui'
        uiPath=uiPath.replace('\\','/')
        mel.eval('RAT_GUI(1,"%s")' % uiPath)