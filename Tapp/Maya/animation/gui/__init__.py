import os
import webbrowser

from PyQt4 import QtCore, QtGui,uic
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omu
import sip

import Tapp.Maya.animation.character as character
import Tapp.Maya.animation.tools as tools
import Tapp.Maya.utils.ZvParentMaster as muz
import Tapp.Maya.animation.utils as mau
import Tapp.Maya.animation.utils.ml_breakdownDragger as maumlb
import Tapp.Maya.animation.utils.ml_hold as maumlh
import Tapp.Maya.animation.utils.ml_keyValueDragger as maumlk

uiPath=os.path.dirname(__file__)+'/resources/animation.ui'
uiPath=r'C:\Users\tokejepsen\Documents\GitHub\Tapp\Tapp\Maya\animation\gui'+'/resources/animation.ui'
form,base=uic.loadUiType(uiPath)

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class Form(base,form):
    def __init__(self, parent=maya_main_window()):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
        self.setObjectName('tatDock')
    
    def create_connections(self):
        #///character connections///
        self.connect(self.ik_button, QtCore.SIGNAL('clicked()'),character.IkSwitch)
        self.connect(self.fk_button, QtCore.SIGNAL('clicked()'),character.FkSwitch)
        self.connect(self.zeroControl_button, QtCore.SIGNAL('clicked()'),character.ZeroControl)
        self.connect(self.zeroLimb_button, QtCore.SIGNAL('clicked()'),character.ZeroLimb)
        self.connect(self.zeroCharacter_button, QtCore.SIGNAL('clicked()'),character.ZeroCharacter)
        self.connect(self.keyLimb_button, QtCore.SIGNAL('clicked()'),character.KeyLimb)
        self.connect(self.keyCharacter_button, QtCore.SIGNAL('clicked()'),character.KeyCharacter)
        self.connect(self.selectLimb_button, QtCore.SIGNAL('clicked()'),character.SelectLimb)
        self.connect(self.selectCharacter_button, QtCore.SIGNAL('clicked()'),character.SelectCharacter)
        
        #///tools connections///
        self.connect(self.tools_zvParentMaster, QtCore.SIGNAL('clicked()'),muz.ZvParentMaster)
        self.connect(self.tools_zvParentMasterHelp, QtCore.SIGNAL('clicked()'),self.zvParentMasterHelp)
        self.connect(self.tools_breakdownDragger, QtCore.SIGNAL('clicked()'),maumlb.drag)
        self.connect(self.tools_breakdownDraggerHelp, QtCore.SIGNAL('clicked()'),self.breakdownDraggerHelp)
        self.connect(self.tools_holdKey, QtCore.SIGNAL('clicked()'),maumlh.ui)
        self.connect(self.tools_holdKeyHelp, QtCore.SIGNAL('clicked()'),self.holdKeyHelp)
        self.connect(self.tools_keyValueDragger, QtCore.SIGNAL('clicked()'),maumlk.drag)
        self.connect(self.tools_keyValueDraggerHelp, QtCore.SIGNAL('clicked()'),self.keyValueDraggerHelp)
        self.connect(self.tools_keyCleanUp, QtCore.SIGNAL('clicked()'),self.keyCleanUp_click)
        self.connect(self.tools_exportAnim, QtCore.SIGNAL('clicked()'),tools.ExportAnim)
        self.connect(self.tools_importAnim, QtCore.SIGNAL('clicked()'),tools.ImportAnim)
    
    def on_character_ik_pushButton_released(self):
        
        character.IkSwitch()
    
    def on_character_fk_pushButton_released(self):
        
        character.FkSwitch()
    
    def on_character_zerocontrol_pushButton_released(self):
        
        character.ZeroControl()
    
    def on_character_zerolimb_pushButton_released(self):
        
        character.ZeroLimb()
    
    def on_character_zerocharacter_pushButton_released(self):
        
        character.ZeroCharacter()
    
    def on_character_keylimb_pushButton_released(self):
        
        character.KeyLimb()
    
    def on_character_keycharacter_pushButton_released(self):
        
        character.KeyCharacter()
    
    def on_character_selectlimb_pushButton_released(self):
        
        character.SelectLimb()
    
    def on_character_selectcharacter_pushButton_released(self):
        
        character.SelectCharacter()
    
    def on_tools_zvparentmaster_pushButton_released(self):
        
        muz.ZvParentMaster()
    
    def on_tools_zvparentmasterhelp_pushButton_released(self):
        
        webbrowser.open('http://www.creativecrash.com/maya/downloads/scripts-plugins/animation/c/zv-parent-master')
    
    def on_tools_breakdowndragger_pushButton_released(self):
        
        maumlb.drag()
    
    def on_tools_breakdowndraggerhelp_pushButton_released(self):
        
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_breakdownDragger')
    
    def on_tools_holdkey_pushButton_released(self):
        
        maumlh.ui()
    
    def on_tools_holdkeyhelp_pushButton_released(self):
        
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_hold')
    
    def on_tools_keyvaluedragger_pushButton_released(self):
        
        maumlk.drag()
    
    def on_tools_keyvaluedraggerhelp_pushButton_released(self):
        
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_keyValueDragger')
    
    def on_tools_keycleanup_pushButton_released(self):
        
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
    
    def on_tools_keycleanuphelp_pushButton_released(self):
        
        msg='This cleans any static channels and redundant keys.\n'
        msg+='If nothing is selected, everything in the scene gets cleaned.'
        
        cmds.confirmDialog( title='Key Clean Up Info', message=msg,defaultButton='OK')
    
    def on_tools_exportanimation_pushButton_released(self):
        
        tools.ExportAnim()
    
    def on_tools_exportanimationhelp_pushButton_released(self):
        
        pass
    
    def on_tools_importanimation_pushButton_released(self):
        
        tools.ImportAnim()
    
    def on_tools_importanimationhelp_pushButton_released(self):
        
        pass
    
    def on_tools_changeRotationOrder_pushButton_released(self):
        
        path=os.path.dirname(__file__)
        parentDir=os.path.abspath(os.path.join(path, os.pardir))
        
        #sourcing zoo utils
        melPath=parentDir+'/utils/zooUtils.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        #sourcing zoo change
        melPath=parentDir+'/utils/zooChangeRoo.mel'
        melPath=melPath.replace('\\','/')
        mel.eval('source "%s"' % melPath)
        
        mel.eval('zooChangeRoo %s' % self.tools_changeRotationOrder_comboBox.currentText())
    
    def on_tools_changeRotationOrderHelp_pushButton_released(self):
        
        webbrowser.open('http://www.creativecrash.com/maya/downloads/scripts-plugins/animation/c/zoochangeroo')

def show():
    #delete previous ui
    if cmds.dockControl('tatDock',exists=True):
        cmds.deleteUI('tatDock')
    
    #workaround to create dock control with dialog
    slider = cmds.floatSlider()
    dock = cmds.dockControl('tatDock',label='Tapp Animation Tools',content=slider, area='right')
    dockPt = omu.MQtUtil.findControl(dock)
    dockWidget = sip.wrapinstance(long(dockPt), QtCore.QObject)
    dockWidget.setWidget(Form())

show()