import os

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from PySide import QtGui
from shiboken import wrapInstance

from .resources import dialog
#from . import alembic


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
        pass

    def create_connections(self):

        self.fileTextureManager_pushButton.released.connect(self.on_fileTextureManager_pushButton_released)
        self.addRimLight_pushButton.released.connect(self.on_addRimLight_pushButton_released)

        self.fgshooter_pushButton.released.connect(self.on_fgshooter_pushButton_released)

        self.exportAlembic_pushButton.released.connect(self.on_exportAlembic_pushButton_released)

        self.arnold_addSubdivision_pushButton.released.connect(self.on_arnold_addSubdivision_pushButton_released)

        self.addSubdivision_pushButton.released.connect(self.on_addSubdivision_pushButton_released)
        self.setSubdivision_pushButton.released.connect(self.on_setSubdivision_pushButton_released)
        self.addDomeLight_pushButton.released.connect(self.on_addDomeLight_pushButton_released)
        self.createTechPasses_pushButton.released.connect(self.on_createTechPasses_pushButton_released)
        self.addObjectID_pushButton.released.connect(self.on_addObjectID_pushButton_released)

    def on_fgshooter_pushButton_released(self):

        from . import fgshooter
        fgshooter.ui()

    def on_exportAlembic_pushButton_released(self):

        #exporting alembic
        #alembic.exportAlembic()
        pass

    def on_addRimLight_pushButton_released(self):

        import Tapp.Maya.lighting.AddRimLight as mla
        mla.addRimRamp()

    def on_addSubdivision_pushButton_released(self):

        import Tapp.Maya.lighting.vray as mlv
        mlv.addSubdivision()

    def on_setSubdivision_pushButton_released(self):

        import Tapp.Maya.lighting.vray as mlv
        level = self.subdivision_spinBox.value()
        mlv.setSubdivision(level)

    def on_addDomeLight_pushButton_released(self):

        #export alembic
        fileFilter = "HDRI (*.hdr)"
        f = cmds.fileDialog2(fileFilter=fileFilter, dialogStyle=1, fileMode=1)

        if f:
            #get check box state
            state = self.domeLightCameraSpace_checkBox.checkState()

            if state == 0:
                cameraSpace = False
            if state == 2:
                cameraSpace = True

            import Tapp.Maya.lighting.vray as mlv
            mlv.addDomeLight(f[0], cameraSpace)

    def on_createTechPasses_pushButton_released(self):

        import Tapp.Maya.lighting.vray as mlv
        mlv.createTechPasses()

    def on_addObjectID_pushButton_released(self):

        import Tapp.Maya.lighting.vray as mlv
        mlv.addObjectID()

    def on_fileTextureManager_pushButton_released(self):

        melPath = os.path.dirname(__file__) + '/FileTextureManager.mel'
        melPath = melPath.replace('\\', '/')
        mel.eval('source "%s"' % melPath)
        mel.eval('FileTextureManager')

    def on_arnold_addSubdivision_pushButton_released(self):

        import Tapp.Maya.lighting.arnold as mla
        mla.addSubdivision()


def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName() == 'tapp_lighting':
            widget.close()

    #showing new dialog
    win = Window()
    win.show()
