import os

from PySide import QtGui
from shiboken import wrapInstance

import maya.cmds as cmds
import pymel.core as pm
import maya.OpenMayaUI as omui

from .resources import dialog
from . import utils


def maya_main_window():

    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class Window(QtGui.QMainWindow, dialog.Ui_MainWindow):

    def __init__(self, parent=maya_main_window()):
        super(Window, self).__init__(parent)
        self.setupUi(self)

        self.create_connections()

    def create_connections(self):

        self.add_pushButton.released.connect(self.add_pushButton_released)
        self.remove_pushButton.released.connect(self.remove_pushButton_released)
        self.export_pushButton.released.connect(self.export_pushButton_released)
        self.import_pushButton.released.connect(self.import_pushButton_released)
        self.playblastQueue_pushButton.released.connect(self.playblastQueue_pushButton_released)
        self.outputFolder_pushButton.released.connect(self.outputFolder_pushButton_released)

    def add_pushButton_released(self):

        filePath = QtGui.QFileDialog.getOpenFileName(self, 'Open Maya File',
                                                     '../..',
                                                     'Maya File (*.ma)')
        filePath = filePath[0]
        if filePath:
            utils.SavePrompt()
            cmds.file(filePath, open=True, force=True)

            cameras = []
            for cam in pm.ls(type='camera'):
                if not cam.orthographic.get():
                    cameras.append(str(cam.getParent()))

            cameras.append('Close')
            msg = 'Select camera to add.'
            camera = cmds.confirmDialog(title='Cameras', message=msg,
                                        button=cameras)

            self.addRow(filePath, camera)

    def remove_pushButton_released(self):

        row = self.tableWidget.currentRow()
        if row >= 0:
            self.tableWidget.removeRow(row)
        else:
            msg = 'No item selected!'
            msg += ' Select a cell in the row you want to remove.'
            cmds.warning(msg)

    def export_pushButton_released(self):

        utils.ExportData(self.getData())

    def import_pushButton_released(self):

        data = utils.ImportData()
        if data:
            for item in data:
                filePath = os.path.join(item['folder'], item['file'])
                self.addRow(filePath, item['camera'])

    def outputFolder_pushButton_released(self):

        msg = 'Locate Output Folder'
        folder = QtGui.QFileDialog.getExistingDirectory(caption=msg)
        if folder:
            self.outputFolder_lineEdit.setText(folder)

    def playblastQueue_pushButton_released(self):

        outputFolder = self.outputFolder_lineEdit.text()
        utils.PlayblastData(self.getData(), output=outputFolder,
                            width=self.width_spinBox.value(),
                            height=self.height_spinBox.value())

    def getData(self):

        dataExport = []
        rowCount = self.tableWidget.rowCount()
        for count in range(0, rowCount):
            data = {}
            data['folder'] = self.tableWidget.item(count, 0).text()
            data['file'] = self.tableWidget.item(count, 1).text()
            data['camera'] = self.tableWidget.item(count, 2).text()
            dataExport.append(data)

        return dataExport

    def addRow(self, filePath, camera):

        folder = os.path.dirname(filePath)
        fileName = os.path.basename(filePath)

        rowCount = self.tableWidget.rowCount() + 1
        self.tableWidget.setRowCount(rowCount)

        item = QtGui.QTableWidgetItem(folder)
        self.tableWidget.setItem(rowCount - 1, 0, item)
        item = QtGui.QTableWidgetItem(fileName)
        self.tableWidget.setItem(rowCount - 1, 1, item)
        item = QtGui.QTableWidgetItem(camera)
        self.tableWidget.setItem(rowCount - 1, 2, item)

        self.tableWidget.repaint()
