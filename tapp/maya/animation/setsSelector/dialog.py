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

        self.refresh()

        self.create_connections()

    def refresh(self):

        self.ui.listWidget.clear()

        # Populate list
        if self.getSets():
            self.ui.listWidget.addItems(self.getSets())

    def create_connections(self):

        self.ui.listWidget.itemSelectionChanged.connect(
            self.on_listWidget_itemSelectionChanged
        )
        self.ui.pushButton.released.connect(self.on_pushButton_released)

    def on_pushButton_released(self):

        self.refresh()

    def on_listWidget_itemSelectionChanged(self):

        members = []
        # Getting members of sets
        if self.ui.listWidget.selectedItems():

            for item in self.ui.listWidget.selectedItems():

                members.extend(
                    cmds.listConnections(item.text() + ".dagSetMembers")
                )

        if members:
            cmds.select(members, toggle=self.ui.checkBox.isChecked())
        else:
            cmds.select(cl=True)

    def getSets(self):

        objectSets = []
        for node in cmds.ls(transforms=True):

            sets = cmds.listSets(object=node)
            if sets:
                objectSets.extend(sets)

        return list(set(objectSets))
