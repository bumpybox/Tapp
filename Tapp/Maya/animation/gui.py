from PyQt4 import QtCore, QtGui
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omu
import sip

from Tapp.Maya.animation.utils import character

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)
    
class batDialog(QtGui.QDialog):
    
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
        gb_layout.addWidget(self.flipLimb_button)
        gb_layout.addWidget(self.flipCharacter_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Mirror Pose')
        gb_layout=QtGui.QHBoxLayout()
        self.mirrorLimb_button=QtGui.QPushButton(text='Limb')
        self.mirrorCharacter_button=QtGui.QPushButton(text='Character')
        gb_layout.addWidget(self.mirrorLimb_button)
        gb_layout.addWidget(self.mirrorCharacter_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Face Controls')
        gb_layout=QtGui.QHBoxLayout()
        self.faceControls_button=QtGui.QPushButton(text='Show Controls')
        gb_layout.addWidget(self.faceControls_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #create tools tab
        tools_tab=QtGui.QWidget()
        tab_layout=QtGui.QVBoxLayout()
        tab_layout.setAlignment(QtCore.Qt.AlignTop)
        tools_tab.setLayout(tab_layout)
        
        gb=QtGui.QGroupBox(title='Space Switching')
        gb_layout=QtGui.QHBoxLayout()
        self.zvParentMaster_button=QtGui.QPushButton(text='Zv Parent Master')
        gb_layout.addWidget(self.zvParentMaster_button)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        gb=QtGui.QGroupBox(title='Keying')
        gb_layout=QtGui.QVBoxLayout()
        self.breakdownDragger=QtGui.QPushButton(text='Breakdown Dragger')
        gb_layout.addWidget(self.breakdownDragger)
        self.holdKey=QtGui.QPushButton(text='Hold Key')
        gb_layout.addWidget(self.holdKey)
        self.keyValueDragger=QtGui.QPushButton(text='Key Value Dragger')
        gb_layout.addWidget(self.keyValueDragger)
        self.keyCleanUp=QtGui.QPushButton(text='Key Clean Up')
        gb_layout.addWidget(self.keyCleanUp)
        gb.setLayout(gb_layout)
        tab_layout.addWidget(gb)
        
        #create tools tab
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
        #///characte connections///
        self.connect(self.ik_button, QtCore.SIGNAL('clicked()'),character.ikSwitch)
        self.connect(self.fk_button, QtCore.SIGNAL('clicked()'),character.fkSwitch)
        
        self.connect(self.rigRezLow_button, QtCore.SIGNAL('clicked()'),character.lowRezRig)
        self.connect(self.rigRezMid_button, QtCore.SIGNAL('clicked()'),character.midRezRig)
        self.connect(self.rigRezHigh_button, QtCore.SIGNAL('clicked()'),character.highRezRig)
        
        self.connect(self.zeroControl_button, QtCore.SIGNAL('clicked()'),character.zeroControl)
        self.connect(self.zeroLimb_button, QtCore.SIGNAL('clicked()'),character.zeroLimb)
        self.connect(self.zeroCharacter_button, QtCore.SIGNAL('clicked()'),character.zeroCharacter)
        
        self.connect(self.keyLimb_button, QtCore.SIGNAL('clicked()'),character.keyLimb)
        self.connect(self.keyCharacter_button, QtCore.SIGNAL('clicked()'),character.keyCharacter)
        
        self.connect(self.selectLimb_button, QtCore.SIGNAL('clicked()'),character.selectLimb)
        self.connect(self.selectCharacter_button, QtCore.SIGNAL('clicked()'),character.selectCharacter)
        
        self.connect(self.flipLimb_button, QtCore.SIGNAL('clicked()'),character.flipLimb)
        self.connect(self.flipCharacter_button, QtCore.SIGNAL('clicked()'),character.flipCharacter)
        
        self.connect(self.mirrorLimb_button, QtCore.SIGNAL('clicked()'),character.mirrorLimb)
        self.connect(self.mirrorCharacter_button, QtCore.SIGNAL('clicked()'),character.mirrorCharacter)
        
        self.connect(self.faceControls_button, QtCore.SIGNAL('clicked()'),self.faceControls_button_click)
        
        #///tools connections///
        self.connect(self.zvParentMaster_button, QtCore.SIGNAL('clicked()'),self.zvParentMaster_button_click)
        
        self.connect(self.breakdownDragger, QtCore.SIGNAL('clicked()'),self.breakdownDragger_click)
        self.connect(self.holdKey, QtCore.SIGNAL('clicked()'),self.holdKey_click)
        self.connect(self.keyValueDragger, QtCore.SIGNAL('clicked()'),self.keyValueDragger_click)
        self.connect(self.keyCleanUp, QtCore.SIGNAL('clicked()'),self.keyCleanUp_click)

    def faceControls_button_click(self):
        import bbt_maya.bat.face.gui
        
        bbt_maya.bat.face.gui.show()

    def zvParentMaster_button_click(self):
        from bbt_maya.python import ZvParentMaster
        
        ZvParentMaster.ZvParentMaster()
    
    def breakdownDragger_click(self):
        from bbt_maya.python import ml_breakdownDragger
        
        ml_breakdownDragger.drag()
    
    def holdKey_click(self):
        from bbt_maya.python import ml_hold
        
        ml_hold.ui()
    
    def keyValueDragger_click(self):
        from bbt_maya.python import ml_keyValueDragger
        
        ml_keyValueDragger.drag()
    
    def keyCleanUp_click(self):
        cmds.undoInfo(openChunk=True)
        
        #execute redundant keys mel script
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
    if cmds.dockControl('batDock',exists=True):
        cmds.deleteUI('batDock')
    
    #workaround to create dock control with dialog
    slider = cmds.floatSlider()
    dock = cmds.dockControl('batDock',label='Bumpybox Animation Tools',content=slider, area='right')
    dockPt = omu.MQtUtil.findControl(dock)
    dockWidget = sip.wrapinstance(long(dockPt), QtCore.QObject)
    dockWidget.setWidget(batDialog())

show()