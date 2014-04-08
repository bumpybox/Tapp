import os
import sys

try:
    from PySide import QtGui
    import pysideuic
except:
    raw_input('PySide not found!')
    sys.exit(0)


class Window(QtGui.QWidget):

    def __init__(self):
        super(Window, self).__init__()

        self.initUI()

    def initUI(self):

        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open UI File',
                                                     '../..', 'UI File (*.ui)')
        if fileName:
            uiFile = open(fileName[0], 'r')

            parentdir = os.path.abspath(os.path.join(fileName[0], os.pardir))
            filename = os.path.basename(os.path.splitext(fileName[0])[0])

            pyFile = open(os.path.join(parentdir, filename) + '.py', 'w')

            pysideuic.compileUi(uiFile, pyFile)

            uiFile.close()
            pyFile.close()

        sys.exit(0)

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())
