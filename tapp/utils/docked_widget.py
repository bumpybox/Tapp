from Qt import QtWidgets

import utils


class Dock(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(Dock, self).__init__(parent)
        QtWidgets.QVBoxLayout(self)
        self.setObjectName("tapp.dock")


def get_docked_widget():

    if "maya" in utils.get_host():
        return get_maya_dock_widget()

    if "nuke" in utils.get_host():
        return get_nuke_dock_widget()

    return None


def get_maya_dock_widget():
    import maya.cmds as cmds

    main_window = None
    for obj in QtWidgets.qApp.topLevelWidgets():
        if obj.objectName() == "MayaWindow":
            main_window = obj

    if cmds.dockControl("MayaWindow|Tapp", q=True, ex=True):
        cmds.deleteUI("MayaWindow|Tapp")

    dock = Dock(parent=main_window)

    allowedAreas = ["right", "left"]
    cmds.dockControl("Tapp", label="Tapp", area="right",
                     content="tapp.dock", allowedArea=allowedAreas,
                     visible=True)

    return dock


def get_nuke_dock_widget():
    from nukescripts import panels
    import nuke

    # delete existing dock
    for obj in QtWidgets.QApplication.allWidgets():
        if obj.objectName() == "tapp.dock":
            obj.deleteLater()

    pane = nuke.getPaneFor("Properties.1")
    panel = panels.registerWidgetAsPanel("tapp.docked_widget.Dock",
                                         "Tapp",
                                         "tapp.dock",
                                         True).addToPane(pane)

    return panel.customKnob.getObject().widget
