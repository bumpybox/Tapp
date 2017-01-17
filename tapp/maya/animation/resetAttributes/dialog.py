import os

from Qt import QtWidgets, QtCompat

import maya.cmds as cmds


class Dialog(QtWidgets.QDialog):

    def __init__(self):
        super(Dialog, self).__init__()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)

        fname = os.path.splitext(__file__)[0] + ".ui"
        self.ui = QtCompat.load_ui(fname=fname)
        layout.addWidget(self.ui)

        self.create_connections()

    def create_connections(self):

        self.ui.pushButton.released.connect(self.pushButton_released)

    def pushButton_released(self):

        translation = self.ui.translation_checkBox.isChecked()
        rotation = self.ui.rotation_checkBox.isChecked()
        scale = self.ui.scale_checkBox.isChecked()
        userAttrs = self.ui.extraAttributes_checkBox.isChecked()

        self.resetSelection(translation, rotation, scale, userAttrs)

    def resetAttribute(self, node, attr):

        # Reset attributes to default if keyable
        if cmds.attributeQuery(attr, node=node, keyable=True):
            values = cmds.attributeQuery(attr, node=node, listDefault=True)

            try:
                cmds.setAttr(node + '.' + attr, *values)
            except:
                pass

    def resetAttributes(self, node, translation=True, rotation=True,
                        scale=True, userAttrs=True):

        if translation:
            self.resetAttribute(node, 'tx')
            self.resetAttribute(node, 'ty')
            self.resetAttribute(node, 'tz')

        if rotation:
            self.resetAttribute(node, 'rx')
            self.resetAttribute(node, 'ry')
            self.resetAttribute(node, 'rz')

        if scale:
            self.resetAttribute(node, 'sx')
            self.resetAttribute(node, 'sy')
            self.resetAttribute(node, 'sz')

        if userAttrs:
            if cmds.listAttr(node, userDefined=True):
                for attr in cmds.listAttr(node, userDefined=True):
                    self.resetAttribute(node, attr)

    def resetSelection(self, translation=True, rotation=True,
                       scale=True, userAttrs=True):

        # Undo enable
        cmds.undoInfo(openChunk=True)

        # Getting selection
        sel = cmds.ls(sl=True)

        # Zero nodes
        if len(sel) >= 1:
            for node in cmds.ls(sl=True):
                self.resetAttributes(
                    node, translation, rotation, scale, userAttrs
                )

            # Revert selection
            cmds.select(sel)
        else:
            cmds.warning('No nodes select!')

        cmds.undoInfo(closeChunk=True)
