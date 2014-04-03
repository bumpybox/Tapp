from PySide import QtGui
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

import Tapp.Maya.lighting.gui as lighting
reload(lighting)
import Tapp.Maya.animation.gui as animation
reload(animation)
import Tapp.Maya.rigging.gui as rigging
reload(rigging)
import Tapp.Maya.modelling.gui as modelling
reload(modelling)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class Window(QtGui.QDialog):
    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)

        self.setObjectName('tappDialog')

        self.main_layout = QtGui.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.main_tabs = QtGui.QTabWidget()
        self.main_layout.addWidget(self.main_tabs)

        self.main_tabs.addTab(modelling.Form(), 'Modelling')
        self.main_tabs.addTab(rigging.Window(), 'Rigging')
        self.main_tabs.addTab(animation.Window(), 'Animation')
        self.main_tabs.addTab(lighting.Window(), 'Lighting')

    def show(self):
        #delete previous ui
        if cmds.dockControl('tappWindow', exists=True):
            cmds.deleteUI('tappWindow')

        #creating ui
        win = Window()
        minSize = win.minimumSizeHint()
        cmds.dockControl('tappWindow', content='tappDialog', area='right',
                         label='Tapp', width=minSize.width())
