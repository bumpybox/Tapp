import os

from Qt import QtWidgets, QtCompat

import maya.cmds as cmds
import pymel.core as pm

import utils


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

        self.ui.add_pushButton.released.connect(self.add_pushButton_released)
        self.ui.remove_pushButton.released.connect(
            self.remove_pushButton_released
        )
        self.ui.export_pushButton.released.connect(
            self.export_pushButton_released
        )
        self.ui.import_pushButton.released.connect(
            self.import_pushButton_released
        )
        self.ui.playblastQueue_pushButton.released.connect(
            self.playblastQueue_pushButton_released
        )
        self.ui.outputFolder_pushButton.released.connect(
            self.outputFolder_pushButton_released
        )

    def add_pushButton_released(self):

        msg = 'Do you want to add an empty row,'
        msg += ' or open a file to fill in the row?'
        addRow = cmds.confirmDialog(
            title='Cameras',
            message=msg,
            button=['Empty', 'Open File']
        )

        if addRow == 'Open File':

            filePath = QtWidgets.QFileDialog.getOpenFileName(
                self,
                'Open Maya File',
                '../..',
                'Maya File (*.ma)'
            )
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
                camera = cmds.confirmDialog(
                    title='Cameras',
                    message=msg,
                    button=cameras
                )

                self.addRow(filePath, camera)
        else:
            self.addRow('', '')

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
        folder = QtWidgets.QFileDialog.getExistingDirectory(caption=msg)
        if folder:
            self.ui.outputFolder_lineEdit.setText(folder)

    def playblastQueue_pushButton_released(self):

        outputFolder = self.outputFolder_lineEdit.text()
        utils.PlayblastData(
            self.getData(),
            output=outputFolder,
            width=self.ui.width_spinBox.value(),
            height=self.ui.height_spinBox.value()
        )

    def getData(self):

        dataExport = []
        rowCount = self.ui.tableWidget.rowCount()
        for count in range(0, rowCount):
            data = {}
            data['folder'] = self.ui.tableWidget.item(count, 0).text()
            data['file'] = self.ui.tableWidget.item(count, 1).text()
            data['camera'] = self.ui.tableWidget.item(count, 2).text()
            dataExport.append(data)

        return dataExport

    def addRow(self, filePath, camera):

        folder = os.path.dirname(filePath)
        fileName = os.path.basename(filePath)

        rowCount = self.ui.tableWidget.rowCount() + 1
        self.ui.tableWidget.setRowCount(rowCount)

        item = QtWidgets.QTableWidgetItem(folder)
        self.ui.tableWidget.setItem(rowCount - 1, 0, item)
        item = QtWidgets.QTableWidgetItem(fileName)
        self.ui.tableWidget.setItem(rowCount - 1, 1, item)
        item = QtWidgets.QTableWidgetItem(camera)
        self.ui.tableWidget.setItem(rowCount - 1, 2, item)

        self.ui.tableWidget.repaint()
