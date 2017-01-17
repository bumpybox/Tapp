import sys
import contextlib

from Qt import QtWidgets

import tapp.maya.dialog


@contextlib.contextmanager
def application():

    app = QtWidgets.QApplication.instance()

    if not app:
        print("Starting new QApplication..")
        app = QtWidgets.QApplication(sys.argv)
        yield app
        app.exec_()
    else:
        print("Using existing QApplication..")
        yield app


def show(parent=None):

    import utils.docked_widget

    with application():

        dock = utils.docked_widget.get_docked_widget()
        win = tapp.maya.dialog.Dialog()

        if dock:
            dock.layout().addWidget(win)
        else:
            win.show()
            return win


if __name__ == "__main__":

    show()
