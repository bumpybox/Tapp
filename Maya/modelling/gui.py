import os
import webbrowser

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from PySide import QtGui
from shiboken import wrapInstance

from .resources import dialog
from . import utils
from . import blendshapes


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

        self.setObjectName('tapp_modelling')

        self.loadedStyleSheet='QPushButton {color: white;background-color: green}'

        self.posVerts = None
        self.upVert = None

    def create_connections(self):

        self.mirrorBlendshape_pushButton.released.connect(self.on_mirrorBlendshape_pushButton_released)
        self.UVSymmetry_pushButton.released.connect(self.on_UVSymmetry_pushButton_released)
        self.loadPositionVerts_pushButton.released.connect(self.on_loadPositionVerts_pushButton_released)
        self.loadUpVert_pushButton.released.connect(self.on_loadUpVert_pushButton_released)
        self.create_pushButton.released.connect(self.on_create_pushButton_released)
        self.scatter_pushButton.released.connect(self.on_scatter_pushButton_released)
        self.scatterInfo_pushButton.released.connect(self.on_scatterInfo_pushButton_released)
        self.symmetry_pushButton.released.connect(self.on_symmetry_pushButton_released)
        self.detachSeparate_pushButton.released.connect(self.on_detachSeparate_pushButton_released)
        self.roadKill_pushButton.released.connect(self.on_roadKill_pushButton_released)

    def on_mirrorBlendshape_pushButton_released(self):

        blendshapes.mirrorBlendshape()

    def on_UVSymmetry_pushButton_released(self):

        blendshapes.symmetry()

    def on_loadPositionVerts_pushButton_released(self):

        sel = cmds.ls(selection=True, flatten=True)

        if len(sel) > 0:

            shape = cmds.ls(selection=True, objectsOnly=True)[0]

            if cmds.nodeType(shape) == 'mesh':
                if cmds.polyEvaluate()['vertexComponent'] > 0:

                    verts = []
                    for vert in sel:

                        verts.append(vert)

                    if len(verts) == 2:
                        self.posVerts = verts
                        self.positionVerts_label.setText('Verts loaded!')
                        self.loadPositionVerts_pushButton.setStyleSheet(self.loadedStyleSheet)
                    else:
                        cmds.warning('More or Less than two verts selected. Please select only 2 verts.')
                else:
                    cmds.warning('No verts selected!')
            else:
                cmds.warning('Selection is not a vertex!')
        else:
            cmds.warning('Nothing is selected!')

    def on_loadUpVert_pushButton_released(self):

        sel = cmds.ls(selection=True,flatten=True)

        if len(sel) > 0:

            shape = cmds.ls(selection=True, objectsOnly=True)[0]

            if cmds.nodeType(shape) == 'mesh':
                if cmds.polyEvaluate()['vertexComponent']>0:

                    verts = []
                    for vert in sel:

                        verts.append(vert)

                    self.upVert = verts
                    self.upVert_label.setText('Vert loaded!')
                    self.loadUpVert_pushButton.setStyleSheet(self.loadedStyleSheet)
                else:
                    cmds.warning('No vert selected!')
            else:
                cmds.warning('Selection is not a vertex!')
        else:
            cmds.warning('Nothing is selected!')

    def on_create_pushButton_released(self):

        if self.posVerts != None and self.upVert != None:

            #get check box state
            state = self.locator_checkBox.checkState()

            if state == 0:
                locatorPivot = False
            if state == 2:
                locatorPivot = True

            #get check box state
            state = self.mesh_checkBox.checkState()

            if state == 0:
                meshPivot = False
            if state == 2:
                meshPivot = True

            #execute
            utils.triangulatePivot(self.posVerts, self.upVert, locatorPivot, meshPivot)

        else:
            cmds.warning('Position Verts and Upvector Vert not loaded!')

    def on_scatter_pushButton_released(self):

        melPath = os.path.dirname(__file__) + '/icPolyScatter.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)
        mel.eval('icPolyScatter')

    def on_scatterInfo_pushButton_released(self):

        webbrowser.open('http://www.braverabbit.de/playground/?p=474')

    def on_symmetry_pushButton_released(self):

        melPath = os.path.dirname(__file__) + '/kk_symmetry.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)
        mel.eval('kk_symmetry')

    def on_detachSeparate_pushButton_released(self):

        melPath = os.path.dirname(__file__) + '/detachSeparate.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)
        mel.eval('detachSeparate')

    def on_roadKill_pushButton_released(self):

        melPath = os.path.dirname(__file__) + '/RoadKill.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)

        #get useLSCM
        state = self.roadkill_useLSCM_checkBox.checkState()

        if state == 0:
            LSCMText = '",-abf"'
        if state == 2:
            LSCMText = '",-lscm"'

        #get holesText
        state = self.roadkill_dontFillHoles_checkBox.checkState()

        if state == 0:
            holesText = '",-nofillholes"'
        if state == 2:
            holesText = '",-fillholes"'

        #get liveText
        state = self.roadkill_liveUnwrap_checkBox.checkState()

        if state == 0:
            liveText = '",-notlive"'
        if state == 2:
            liveText = '",-live"'

        exeDir = '"' + os.path.dirname(__file__) + '"'
        exeDir = exeDir.replace('\\', '/')

        mel.eval('DoUnwrap(%s,%s,%s,%s)' % (LSCMText, holesText, liveText, exeDir))


def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName() == 'tapp_modelling':
            widget.close()

    #showing new dialog
    win = Window()
    win.show()
