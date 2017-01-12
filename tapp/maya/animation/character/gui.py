import maya.cmds as cmds
import maya.OpenMayaUI as omui

from PySide import QtGui
from shiboken import wrapInstance

from .resources import dialog
from . import utils


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

        self.start_pushButton.setEnabled(False)
        self.end_pushButton.setEnabled(False)

        self.start_lineEdit.setReadOnly(False)
        self.start_lineEdit.setReadOnly(False)

        self.start_lineEdit.setEnabled(False)
        self.end_lineEdit.setEnabled(False)

    def create_connections(self):

        self.ik_pushButton.released.connect(self.on_ik_pushButton_released)
        self.fk_pushButton.released.connect(self.on_fk_pushButton_released)

        self.range_checkBox.stateChanged.connect(self.range)
        self.start_pushButton.released.connect(self.start)
        self.end_pushButton.released.connect(self.end)
        self.getTimeline_pushButton.released.connect(self.timeline)

    def range(self):

        if self.range_checkBox.isChecked():
            self.start_pushButton.setEnabled(True)
            self.end_pushButton.setEnabled(True)

            self.start_lineEdit.setEnabled(True)
            self.end_lineEdit.setEnabled(True)

        if not self.range_checkBox.isChecked():
            self.start_pushButton.setEnabled(False)
            self.end_pushButton.setEnabled(False)

            self.start_lineEdit.setEnabled(False)
            self.end_lineEdit.setEnabled(False)

            self.start_lineEdit.clear()
            self.end_lineEdit.clear()

    def start(self):

        t = cmds.currentTime(q=True)
        self.start_lineEdit.setText(str(t))

    def end(self):

        t = cmds.currentTime(q=True)
        self.end_lineEdit.setText(str(t))

    def timeline(self):

        minT = cmds.playbackOptions(q=True, min=True)
        maxT = cmds.playbackOptions(q=True, max=True)

        self.start_lineEdit.setText(str(minT))
        self.end_lineEdit.setText(str(maxT))

    def on_ik_pushButton_released(self):

        if self.range_checkBox.isChecked():

            start = int(float(self.start_lineEdit.text()))
            end = int(float(self.end_lineEdit.text()))

            utils.switch('IK', timeRange=True, start=start, end=end)

        else:
            utils.switch('IK')

    def on_fk_pushButton_released(self):

        if self.range_checkBox.isChecked():

            start = int(float(self.start_lineEdit.text()))
            end = int(float(self.end_lineEdit.text()))

            utils.switch('FK', timeRange=True, start=start, end=end)

        else:
            utils.switch('FK')
