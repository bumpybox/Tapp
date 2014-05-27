import os

import maya.mel as mel
import maya.OpenMayaUI as omui

from PySide import QtGui
from shiboken import wrapInstance

from .resources import dialog
from . import spherePreview
from . import constraints


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

        #adding Sphere Preview to dialog
        layout.addWidget(spherePreview.Window())

    def create_connections(self):

        self.doraSkin_pushButton.released.connect(self.doraSkin_pushButton_released)
        self.sculptInbetweenEditor_pushButton.released.connect(self.sculptInbetweenEditor_pushButton_released)
        self.zvRadialBlendshape_pushButton.released.connect(self.zvRadialBlendshape_pushButton_released)
        self.si_poseDeformer_pushButton.released.connect(self.si_poseDeformer_pushButton_released)
        self.ngSkinTools_pushButton.released.connect(self.ngSkinTools_pushButton_released)

        self.cylinderPreviewCreate_pushButton.released.connect(self.on_cylinderPreviewCreate_pushButton_released)
        self.cylinderPreviewDelete_pushButton.released.connect(self.on_cylinderPreviewDelete_pushButton_released)

        self.latticeAdd_pushButton.released.connect(self.latticeAdd_pushButton_released)
        self.latticeRemove_pushButton.released.connect(self.latticeRemove_pushButton_released)

        self.constraintsExport_pushButton.released.connect(self.constraintsExport_pushButton_released)
        self.constraintsImport_pushButton.released.connect(self.constraintsImport_pushButton_released)
        self.constraintsDelete_pushButton.released.connect(self.constraintsDelete_pushButton_released)

    def constraintsExport_pushButton_released(self):

        constraints.ExportData()

    def constraintsImport_pushButton_released(self):

        constraints.ImportData()

    def constraintsDelete_pushButton_released(self):

        constraints.Delete()

    def sculptInbetweenEditor_pushButton_released(self):

        from .sculptInbetweenEditor import dslSculptInbetweenEditor
        create = dslSculptInbetweenEditor.SculptInbetweenEditor()
        create.ui()

    def doraSkin_pushButton_released(self):

        path = os.path.dirname(__file__)

        #sourcing dora util
        melPath = path + '/DoraSkinWeightImpExp.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)

        #launching dora gui
        mel.eval('DoraSkinWeightImpExp()')

    def si_poseDeformer_pushButton_released(self):

        path = os.path.dirname(__file__)

        #sourcing dora util
        melPath = path + '/si_poseDeformer.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)

        #launching dora gui
        mel.eval('si_poseDeformer()')

    def zvRadialBlendshape_pushButton_released(self):

        from . import ZvRadialBlendShape as zv

        zv.ZvRadialBlendShape()

    def ngSkinTools_pushButton_released(self):

        from Tapp.Maya.ngSkinTools.ui.mainwindow import MainWindow
        MainWindow.open()

    def on_cylinderPreviewCreate_pushButton_released(self):

        from . import cylinderPreview
        cylinderPreview.Create()

    def on_cylinderPreviewDelete_pushButton_released(self):

        from . import cylinderPreview
        cylinderPreview.Delete()

    def latticeAdd_pushButton_released(self):

        from . import lattice
        lattice.latticeAdd()

    def latticeRemove_pushButton_released(self):

        from . import lattice
        lattice.latticeRemove()
