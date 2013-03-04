import os
import webbrowser

from PyQt4 import QtCore, QtGui
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omu
import sip

import character
import tools
import Tapp.Maya.utils.ZvParentMaster as muz
import Tapp.Maya.animation.utils as mau
import Tapp.Maya.animation.utils.ml_breakdownDragger as maumlb
import Tapp.Maya.animation.utils.ml_hold as maumlh
import Tapp.Maya.animation.utils.ml_keyValueDragger as maumlk

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)
    
class tatDialog(QtGui.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)
        
        self.setFixedWidth(265)
        
        self.create_layout()
        self.create_connections()
        
    def create_layout(self):
        #create character tab
        char_tab=QtGui.QWidget()
        
        tab_layout=QtGui.QVBoxLayout()
        char_tab.setLayout(tab_layout)
        
        gb=QtGui.QGroupBox(title='IK - FK Switching')
        gb_layout=QtGui.QHBoxLayout()
        self.fk_button=QtGui.QPushButton(text='FK')
        self.ik_button=QtGui.QPushButton(text='IK')
        gb_layout.addWidget(self.fk_button)
        gb_layout.addWidget(self.ik_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Rig Resolution')
        gb_layout=QtGui.QHBoxLayout()
        self.rigRezLow_button=QtGui.QPushButton(text='Low')
        self.rigRezMid_button=QtGui.QPushButton(text='Mid')
        self.rigRezHigh_button=QtGui.QPushButton(text='High')
        self.rigRezLow_button.setEnabled(False)
        self.rigRezMid_button.setEnabled(False)
        self.rigRezHigh_button.setEnabled(False)
        gb_layout.addWidget(self.rigRezLow_button)
        gb_layout.addWidget(self.rigRezMid_button)
        gb_layout.addWidget(self.rigRezHigh_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Zero Controls')
        gb_layout=QtGui.QHBoxLayout()
        self.zeroControl_button=QtGui.QPushButton(text='Control')
        self.zeroLimb_button=QtGui.QPushButton(text='Limb')
        self.zeroCharacter_button=QtGui.QPushButton(text='Character')
        gb_layout.addWidget(self.zeroControl_button)
        gb_layout.addWidget(self.zeroLimb_button)
        gb_layout.addWidget(self.zeroCharacter_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)

        gb=QtGui.QGroupBox(title='Key Controls')
        gb_layout=QtGui.QHBoxLayout()
        self.keyLimb_button=QtGui.QPushButton(text='Limb')
        self.keyCharacter_button=QtGui.QPushButton(text='Character')
        gb_layout.addWidget(self.keyLimb_button)
        gb_layout.addWidget(self.keyCharacter_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Select Controls')
        gb_layout=QtGui.QHBoxLayout()
        self.selectLimb_button=QtGui.QPushButton(text='Limb')
        self.selectCharacter_button=QtGui.QPushButton(text='Character')
        gb_layout.addWidget(self.selectLimb_button)
        gb_layout.addWidget(self.selectCharacter_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Flip Pose')
        gb_layout=QtGui.QHBoxLayout()
        self.flipLimb_button=QtGui.QPushButton(text='Limb')
        self.flipCharacter_button=QtGui.QPushButton(text='Character')
        self.flipLimb_button.setEnabled(False)
        self.flipCharacter_button.setEnabled(False)
        gb_layout.addWidget(self.flipLimb_button)
        gb_layout.addWidget(self.flipCharacter_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Mirror Pose')
        gb_layout=QtGui.QHBoxLayout()
        self.mirrorLimb_button=QtGui.QPushButton(text='Limb')
        self.mirrorCharacter_button=QtGui.QPushButton(text='Character')
        self.mirrorLimb_button.setEnabled(False)
        self.mirrorCharacter_button.setEnabled(False)
        gb_layout.addWidget(self.mirrorLimb_button)
        gb_layout.addWidget(self.mirrorCharacter_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Face Controls')
        gb_layout=QtGui.QHBoxLayout()
        self.faceControls_button=QtGui.QPushButton(text='Show Controls')
        self.faceControls_button.setEnabled(False)
        gb_layout.addWidget(self.faceControls_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #create tools tab
        tools_tab=QtGui.QWidget()
        tab_layout=QtGui.QVBoxLayout()
        tab_layout.setAlignment(QtCore.Qt.AlignTop)
        tools_tab.setLayout(tab_layout)
        
        gb=QtGui.QGroupBox(title='Space Switching')
        gb_layout=QtGui.QGridLayout()
        
        self.tools_zvParentMaster=QtGui.QPushButton(text='Zv Parent Master')
        gb_layout.addWidget(self.tools_zvParentMaster,0,0)
        self.tools_zvParentMasterHelp=QtGui.QPushButton(text='?')
        gb_layout.addWidget(self.tools_zvParentMasterHelp,0,1)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Keying')
        gb_layout=QtGui.QGridLayout()
        
        self.tools_breakdownDragger=QtGui.QPushButton(text='Breakdown Dragger')
        gb_layout.addWidget(self.tools_breakdownDragger,0,0)
        self.tools_breakdownDraggerHelp=QtGui.QPushButton(text='?')
        gb_layout.addWidget(self.tools_breakdownDraggerHelp,0,1)
        
        self.tools_holdKey=QtGui.QPushButton(text='Hold Key')
        gb_layout.addWidget(self.tools_holdKey,1,0)
        self.tools_holdKeyHelp=QtGui.QPushButton(text='?')
        gb_layout.addWidget(self.tools_holdKeyHelp,1,1)
        
        self.tools_keyValueDragger=QtGui.QPushButton(text='Key Value Dragger')
        gb_layout.addWidget(self.tools_keyValueDragger,2,0)
        self.tools_keyValueDraggerHelp=QtGui.QPushButton(text='?')
        gb_layout.addWidget(self.tools_keyValueDraggerHelp,2,1)
        
        self.tools_keyCleanUp=QtGui.QPushButton(text='Key Clean Up')
        gb_layout.addWidget(self.tools_keyCleanUp,3,0)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Export/Import Animation')
        gb_layout=QtGui.QGridLayout()
        
        self.tools_exportAnim=QtGui.QPushButton(text='Export')
        gb_layout.addWidget(self.tools_exportAnim,0,0)
        self.tools_exportAnimHelp=QtGui.QPushButton(text='?')
        gb_layout.addWidget(self.tools_exportAnimHelp,0,1)
        self.tools_exportAnimHelp.setEnabled(False)
        
        self.tools_importAnim=QtGui.QPushButton(text='Import')
        gb_layout.addWidget(self.tools_importAnim,1,0)
        self.tools_importAnim.setEnabled(False)
        self.tools_importAnimHelp=QtGui.QPushButton(text='?')
        gb_layout.addWidget(self.tools_importAnimHelp,1,1)
        self.tools_importAnimHelp.setEnabled(False)
        
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #create playblast tab
        playblast_tab=QtGui.QWidget()
        
        tab_layout=QtGui.QVBoxLayout()
        playblast_tab.setLayout(tab_layout)
        
        #create main tabs
        tabs=QtGui.QVBoxLayout()
        
        main_tabs = QtGui.QTabWidget()
        main_tabs.setMinimumWidth(240)
        tabs.addWidget(main_tabs)
        main_tabs.addTab(char_tab, 'Character')
        main_tabs.addTab(tools_tab, 'Tools')
        
        # Create the main layout
        main_layout = QtGui.QVBoxLayout()
        main_layout.setMargin(2)
        
        scrollArea=QtGui.QScrollArea()
        scrollArea.setLayout(tabs)
        scrollArea.setWidget(main_tabs)
        
        main_layout.addWidget(scrollArea)
        
        self.setLayout(main_layout)

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
        self.connect(self.tools_exportAnim, QtCore.SIGNAL('clicked()'),tools.exportAnim)
    
    def breakdownDraggerHelp(self):
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_breakdownDragger')
        
    def holdKeyHelp(self):
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_hold')
        
    def keyValueDraggerHelp(self):
        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_keyValueDragger')
        
    def zvParentMasterHelp(self):
        webbrowser.open('http://www.creativecrash.com/maya/downloads/scripts-plugins/animation/c/zv-parent-master')
    
    def keyCleanUp_click(self):
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

def show():
    #delete previous ui
    if cmds.dockControl('tmaDock',exists=True):
        cmds.deleteUI('tmaDock')
    
    #workaround to create dock control with dialog
    slider = cmds.floatSlider()
    dock = cmds.dockControl('tmaDock',label='Tapp Animation Tools',content=slider, area='right')
    dockPt = omu.MQtUtil.findControl(dock)
    dockWidget = sip.wrapinstance(long(dockPt), QtCore.QObject)
    dockWidget.setWidget(tatDialog())

#show()