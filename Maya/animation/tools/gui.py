import os
import webbrowser

from PySide import QtGui
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from .resources import dialog
from . import setsSelector
from . import playblastQueue
from . import resetAttributes
from ...utils import ZvParentMaster
from ..utils import ml_breakdownDragger
from ..utils import ml_hold
from ..utils import ml_keyValueDragger
from .. import utils


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class Window(QtGui.QMainWindow, dialog.Ui_MainWindow):

    def __init__(self, parent=maya_main_window()):
        super(Window, self).__init__(parent)
        self.setupUi(self)

        self.modify_dialog()

        self.create_connections()

    def modify_dialog(self):

        layout = self.central_verticalLayout

        #adding Reset Attributes to dialog
        layout.addWidget(resetAttributes.Window())

        #adding Sets Selector to dialog
        layout.addWidget(setsSelector.Window())

    def create_connections(self):

        self.channelBoxLeft_pushButton.released.connect(self.channelBoxLeft)
        self.channelBoxRight_pushButton.released.connect(self.channelBoxRight)

        self.zvParentMaster_pushButton.released.connect(
                                    self.zvParentMaster_pushButton_released)
        self.zvChain_pushButton.released.connect(
                                             self.zvChain_pushButton_released)
        self.zvParentMasterHelp_pushButton.released.connect(
                                self.zvParentMasterHelp_pushButton_released)

        self.breakDownDragger_pushButton.released.connect(
                                  self.breakDownDragger_pushButton_released)
        self.breakDownDraggerHelp_pushButton.released.connect(
                              self.breakDownDraggerHelp_pushButton_released)

        self.holdKey_pushButton.released.connect(
                                             self.holdKey_pushButton_released)
        self.holdKeyHelp_pushButton.released.connect(
                                         self.holdKeyHelp_pushButton_released)

        self.keyValueDragger_pushButton.released.connect(
                                     self.keyValueDragger_pushButton_released)
        self.keyValueDraggerHelp_pushButton.released.connect(
                                 self.keyValueDraggerHelp_pushButton_released)

        self.keyCleanUp_pushButton.released.connect(
                                        self.keyCleanUp_pushButton_released)
        self.keyCleanUpHelp_pushButton.released.connect(
                                    self.keyCleanUpHelp_pushButton_released)

        self.changeRotationOrder_pushButton.released.connect(
                                 self.changeRotationOrder_pushButton_released)
        self.changeRotationOrderHelp_pushButton.released.connect(
                             self.changeRotationOrderHelp_pushButton_released)

        self.ghosting_pushButton.released.connect(
                                          self.ghosting_pushButton_released)
        self.ghostingHelp_pushButton.released.connect(
                                      self.ghostingHelp_pushButton_released)

        self.localizeImagePlane_pushButton.released.connect(
                                self.localizeImagePlane_pushButton_released)

        self.rat_pushButton.released.connect(self.rat_pushButton_released)

        self.paie_pushButton.released.connect(self.paie_pushButton_released)

        self.collisionDeformer_pushButton.released.connect(
                                               self.collisionDeformer_released)

        self.playblastQueue_pushButton.released.connect(
                                               self.playblastQueue_released)

    def channelBoxLeft(self):

        toggle = self.channelBoxLeft_pushButton.isChecked()

        if toggle:

            #toggling right channelbox
            rightToggle = self.channelBoxRight_pushButton.isChecked()
            self.channelBoxRight_pushButton.setChecked(False)

            if rightToggle:
                self.channelBoxRight_widget.setParent(None)

            #creating left channelbox
            ptr = omui.MQtUtil.findControl(cmds.channelBox())
            self.channelBoxLeft_widget = wrapInstance(long(ptr), QtGui.QWidget)

            layout = self.channelBoxLeft_horizontalLayout
            layout.addWidget(self.channelBoxLeft_widget)

            self.resize(400, 0)

            self.updateGeometry()
        else:

            self.channelBoxLeft_widget.setParent(None)

    def channelBoxRight(self):

        toggle = self.channelBoxRight_pushButton.isChecked()

        if toggle:

            #toggling left channelbox
            leftToggle = self.channelBoxLeft_pushButton.isChecked()
            self.channelBoxLeft_pushButton.setChecked(False)

            if leftToggle:
                self.channelBoxLeft_widget.setParent(None)

            #creating Right channelbox
            ptr = omui.MQtUtil.findControl(cmds.channelBox())
            self.channelBoxRight_widget = wrapInstance(long(ptr),
                                                      QtGui.QWidget)

            layout = self.channelBoxRight_horizontalLayout
            layout.addWidget(self.channelBoxRight_widget)

            self.resize(400, 0)

            self.updateGeometry()
        else:

            self.channelBoxRight_widget.setParent(None)

    def playblastQueue_released(self):

        win = playblastQueue.Window()
        win.show()

    def collisionDeformer_released(self):

        cmds.loadPlugin('jlCollisionDeformer.py', quiet=True)

        try:
            mel.eval('jlCollisionDeformer()')
        except:
            cmds.warning(
     'First select the collider mesh then the mesh that should be deformed.')

    def zvParentMaster_pushButton_released(self):

        ZvParentMaster.ZvParentMaster()

    def zvChain_pushButton_released(self):

        #undo enable
        cmds.undoInfo(openChunk=True)

        ZvParentMaster.attach_chain()

        cmds.undoInfo(closeChunk=True)

    def zvParentMasterHelp_pushButton_released(self):

        webbrowser.open(
                'http://www.creativecrash.com/maya/script/zv-parent-master')

    def localizeImagePlane_pushButton_released(self):

        import Tapp.Maya.animation.utils.imageplane as ip

        ip.localizeImagePlane()

    def paie_pushButton_released(self):

        from ..utils import paie as paie

        paie.GUI()

    def breakDownDragger_pushButton_released(self):

        ml_breakdownDragger.drag()

    def breakDownDraggerHelp_pushButton_released(self):

        webbrowser.open(
                'http://morganloomis.com/wiki/tools.html#ml_breakdownDragger')

    def holdKey_pushButton_released(self):

        ml_hold.ui()

    def holdKeyHelp_pushButton_released(self):

        webbrowser.open('http://morganloomis.com/wiki/tools.html#ml_hold')

    def keyValueDragger_pushButton_released(self):

        ml_keyValueDragger.drag()

    def keyValueDraggerHelp_pushButton_released(self):

        webbrowser.open(
                'http://morganloomis.com/wiki/tools.html#ml_keyValueDragger')

    def keyCleanUp_pushButton_released(self):

        cmds.undoInfo(openChunk=True)

        #execute redundant keys script
        path = os.path.dirname(utils.__file__).replace('\\', '/')

        mel.eval('source "' + path + '/deleteRedundantKeys.mel"')
        mel.eval('llDeleteRedundantKeys;')

        #deleting static channels in scene or on selected object
        sel = cmds.ls(selection=True)

        if len(sel) > 0:
            cmds.delete(staticChannels=True)
        else:
            cmds.delete(staticChannels=True, all=True)

        cmds.undoInfo(closeChunk=True)

    def keyCleanUpHelp_pushButton_released(self):

        msg = 'This cleans any static channels and redundant keys.\n'
        msg += 'If nothing is selected, everything in the scene gets cleaned.'

        cmds.confirmDialog(title='Key Clean Up Info', message=msg,
                           defaultButton='OK')

    def changeRotationOrder_pushButton_released(self):

        path = os.path.dirname(utils.__file__)

        #sourcing zoo utils
        melPath = path + '/zooUtils.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)

        #sourcing zoo change
        melPath = path + '/zooChangeRoo.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)

        mel.eval('zooChangeRoo %s' %
                 self.tools_changeRotationOrder_comboBox.currentText())

    def changeRotationOrderHelp_pushButton_released(self):

        webbrowser.open(
                    'http://www.creativecrash.com/maya/script/zoochangeroo')

    def ghosting_pushButton_released(self):

        path = os.path.dirname(utils.__file__)

        #sourcing ghost util
        melPath = path + '/bhGhost.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)

        mel.eval('bhGhost')

    def ghostingHelp_pushButton_released(self):

        webbrowser.open('https://vimeo.com/50029607')

    def rat_pushButton_released(self):

        path = os.path.dirname(utils.__file__)

        #sourcing rat util
        melPath = path + '/RAT.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)

        #launching rat gui
        uiPath = path + '/RAT_ui.ui'
        uiPath = uiPath.replace('\\', '/')
        mel.eval('RAT_GUI(1,"%s")' % uiPath)
