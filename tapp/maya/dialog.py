from Qt import QtWidgets

import animation.dialog as animation
import Red9

# Initialize Red9
Red9.start()


class Dialog(QtWidgets.QDialog):

    def __init__(self):
        super(Dialog, self).__init__()

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 10, 0, 0)
        self.setLayout(self.main_layout)

        self.main_tabs = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.main_tabs)

        self.main_tabs.addTab(animation.Dialog(), "Animation")
