'''
slider that is connected to the timeslider
when scrubbing the slider, record time spend on a frame, ripple scale frame
bake animation to every keyframe
    get the scale comparison between original keyframe length (would be contant) and new keyframe length
    used scale to moved key, 0-1 range is previous key to current key
    ripple effect the start point for next key
'''

from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

def maya_main_window():
    main_window_ptr=omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

class Window(QtGui.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super(Window,self).__init__(parent)
        
        self.setWindowTitle('Timing Tool')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

win=Window()
win.show()