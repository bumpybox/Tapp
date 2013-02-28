import os
import sys

from PyQt4 import QtGui
from PyQt4 import uic

import setup.config as sc
import setup.utils as su

uiPath=os.path.dirname(sc.__file__)+'/ui.ui'
form,base=uic.loadUiType(uiPath)

class Form(base,form):
    def __init__(self, parent=None):
        super(base,self).__init__(parent)
        self.setupUi(self)
        
    def on_installButton_clicked(self):
        
        if self.mayaCheckbox.checkState():
            su.InstallMaya()
        
        if self.nukeCheckbox.checkState():
            su.InstallNuke()
        
        sys.exit()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = Form()
    myapp.show()
    sys.exit(app.exec_())