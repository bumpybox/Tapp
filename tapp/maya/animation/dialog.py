import os
import webbrowser

from Qt import QtWidgets, QtCompat

import maya.cmds as cmds
import maya.mel as mel

import resetAttributes
import setsSelector
import playblastQueue
import ZvParentMaster
import utils
from utils import ml_breakdownDragger
from utils import ml_hold
from utils import ml_keyValueDragger


class Dialog(QtWidgets.QDialog):

    def __init__(self):
        super(Dialog, self).__init__()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        fname = os.path.splitext(__file__)[0] + ".ui"
        self.ui = QtCompat.load_ui(fname=fname)
        layout.addWidget(self.ui)

        layout.addWidget(resetAttributes.dialog.Dialog())
        layout.addWidget(setsSelector.dialog.Dialog())

        self.create_connections()

    def create_connections(self):

        # ZvParentMaster
        self.ui.zvParentMaster_pushButton.released.connect(
            self.zvParentMaster_pushButton_released
        )
        self.ui.zvChain_pushButton.released.connect(
            self.zvChain_pushButton_released
        )
        self.ui.zvParentMasterHelp_pushButton.released.connect(
            self.zvParentMasterHelp_pushButton_released
        )

        # Other tools
        self.ui.breakDownDragger_pushButton.released.connect(
            self.breakDownDragger_pushButton_released
        )
        self.ui.breakDownDraggerHelp_pushButton.released.connect(
            self.breakDownDraggerHelp_pushButton_released
        )

        self.ui.holdKey_pushButton.released.connect(
            self.holdKey_pushButton_released
        )
        self.ui.holdKeyHelp_pushButton.released.connect(
            self.holdKeyHelp_pushButton_released
        )

        self.ui.keyValueDragger_pushButton.released.connect(
            self.keyValueDragger_pushButton_released
        )
        self.ui.keyValueDraggerHelp_pushButton.released.connect(
            self.keyValueDraggerHelp_pushButton_released
        )

        self.ui.keyCleanUp_pushButton.released.connect(
            self.keyCleanUp_pushButton_released
        )
        self.ui.keyCleanUpHelp_pushButton.released.connect(
            self.keyCleanUpHelp_pushButton_released
        )

        self.ui.changeRotationOrder_pushButton.released.connect(
            self.changeRotationOrder_pushButton_released
        )
        self.ui.changeRotationOrderHelp_pushButton.released.connect(
            self.changeRotationOrderHelp_pushButton_released
        )

        self.ui.ghosting_pushButton.released.connect(
            self.ghosting_pushButton_released
        )
        self.ui.ghostingHelp_pushButton.released.connect(
            self.ghostingHelp_pushButton_released
        )

        self.ui.localizeImagePlane_pushButton.released.connect(
            self.localizeImagePlane_pushButton_released
        )

        self.ui.rat_pushButton.released.connect(self.rat_pushButton_released)

        self.ui.paie_pushButton.released.connect(self.paie_pushButton_released)

        self.ui.collisionDeformer_pushButton.released.connect(
            self.collisionDeformer_released
        )

        self.ui.playblastQueue_pushButton.released.connect(
            self.playblastQueue_released
        )

    def playblastQueue_released(self):

        win = playblastQueue.Dialog()
        win.show()

    def collisionDeformer_released(self):

        cmds.loadPlugin('jlCollisionDeformer.py', quiet=True)

        try:
            mel.eval('jlCollisionDeformer()')
        except:
            msg = 'First select the collider mesh then the mesh that should '
            msg += 'be deformed.'
            cmds.warning(msg)

    def zvParentMaster_pushButton_released(self):

        ZvParentMaster.ZvParentMaster()

    def zvChain_pushButton_released(self):

        # Undo enable
        cmds.undoInfo(openChunk=True)

        ZvParentMaster.attach_chain()

        cmds.undoInfo(closeChunk=True)

    def zvParentMasterHelp_pushButton_released(self):

        webbrowser.open(
                'http://www.creativecrash.com/maya/script/zv-parent-master')

    def localizeImagePlane_pushButton_released(self):

        import tapp.maya.animation.utils.imageplane as ip

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

        # Execute redundant keys script
        path = os.path.dirname(utils.__file__).replace('\\', '/')

        mel.eval('source "' + path + '/deleteRedundantKeys.mel"')
        mel.eval('llDeleteRedundantKeys;')

        # Deleting static channels in scene or on selected object
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

        # Sourcing zoo utils
        melPath = path + '/zooUtils.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)

        # Sourcing zoo change
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

        # Sourcing ghost util
        melPath = path + '/bhGhost.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)

        mel.eval('bhGhost')

    def ghostingHelp_pushButton_released(self):

        webbrowser.open('https://vimeo.com/50029607')

    def rat_pushButton_released(self):

        path = os.path.dirname(utils.__file__)

        # Sourcing rat util
        melPath = path + '/RAT.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)

        # Launching rat gui
        uiPath = path + '/RAT_ui.ui'
        uiPath = uiPath.replace('\\', '/')
        mel.eval('RAT_GUI(1,"%s")' % uiPath)
