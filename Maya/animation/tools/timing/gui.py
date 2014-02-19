'''
modify timeline checkbox

possibly something is wrong with duration calculation
forward only mode
    if previous key is lower than currentkey > record
copy from clipboard into key class >< paste from key class to clipboard
accuracy mode
    does not bake to the keys, but copy only the existing keys and times them out
accuracy
    subframes
copy a keyframe range always
store original animation
    store when pressing the slider
multiple objects
'''

import time

from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

#from .resources import dialog

import sys
sys.path.append(r'C:\Users\toke.jepsen\Documents\GitHub')
from Tapp.Maya.animation.tools.timing.resources import dialog

'''
import os
import Tapp.utils.pyside.compileUi as upc

uiPath=os.path.dirname(__file__)+'/resources/timing.ui'
uiPath=r'C:\Users\tokejepsen\Documents\GitHub\Tapp\Tapp\Maya\animation\utils\timing\resources\timing.ui'
upc.compileUi(uiPath)

'''


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class key():

    def __init__(self, time, keyIndex):

        self.time = time
        self.keyIndex = keyIndex
        self.previous = None
        self.next = None


class Window(QtGui.QMainWindow, dialog.Ui_MainWindow):

    def __init__(self, parent=maya_main_window()):
        super(Window, self).__init__(parent)
        self.setupUi(self)

        #self.retranslateUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.loadedStyleSheet = 'QPushButton {color: white;background-color: green}'
        self.unloadedStyleSheet = 'QPushButton {color: white;background-color: red}'

        self.mod_layout()

        self.create_connections()

    def mod_layout(self):

        self.startFrame = cmds.playbackOptions(min=True, q=True)
        self.endFrame = cmds.playbackOptions(max=True, q=True)

        self.horizontalSlider.setTickPosition(
                                      QtGui.QSlider.TickPosition.TicksBelow)
        self.horizontalSlider.setTickInterval(1)
        self.horizontalSlider.setRange(self.startFrame, self.endFrame)
        self.horizontalSlider.setValue(cmds.currentTime(q=True))

        self.accurracy_doubleSpinBox.setValue(1.0)

        self.restoreAnimation_pushButton.setStyleSheet(self.unloadedStyleSheet)

    def create_connections(self):

        self.horizontalSlider.valueChanged.connect(
                                               self.on_slider_value_changed)
        self.horizontalSlider.sliderPressed.connect(self.on_slider_pressed)
        self.horizontalSlider.sliderReleased.connect(self.on_slider_released)

    def on_slider_pressed(self):

        sel = cmds.ls(selection=True)

        #checking selection
        if sel:
            #storing animation
            cmds.copyKey(sel, time=(self.startFrame, self.endFrame))

            #start recording keys
            k = key(time.time(), int(cmds.currentTime(q=True)))
            self.currentKey = k

        else:

            cmds.warning('No nodes selected!')

    def _findStart(self, key):

        if key.previous:
            return self._findStart(key.previous)
        else:
            return key

    def _printDownstream(self, key):

        print '---'
        print 'keyIndex:%s' % key.keyIndex
        print 'time:%s' % key.time
        if key.next:
            print 'duration:%s f' % str((key.next.time - key.time) * 25)

        if key.next:
            self._printDownstream(key.next)

    def _pasteTiming(self, source, target, key):

        if key.next:
            cmds.copyKey(source, time=(key.keyIndex, key.keyIndex))

            cmds.pasteKey(target, time=(self.currentTime, self.currentTime))

            self.currentTime = self.currentTime + ((key.next.time
                                                     - key.time) * 25)

            self._pasteTiming(source, target, key.next)
        else:
            return

    def on_slider_released(self):

        #checking selection
        if cmds.ls(selection=True):

            start = self._findStart(self.currentKey)
            #self._printDownstream(start)

            #undo enable
            cmds.undoInfo(openChunk=True)

            obj = cmds.ls(selection=True)[0]
            for t in range(int(self.startFrame), int(self.endFrame) + 1):

                cmds.currentTime(t)
                cmds.setKeyframe(obj)

            #transfer original animation to temp transform
            loc = cmds.spaceLocator()[0]
            cmds.cutKey(obj, time=(self.startFrame, self.endFrame))
            cmds.pasteKey(loc)

            #paste timing
            self.currentTime = self.startFrame
            self._pasteTiming(loc, obj, start)

            #cleanup
            cmds.delete(loc)
            cmds.keyTangent(obj, itt='auto', ott='auto')
            cmds.delete(staticChannels=True)

            cmds.undoInfo(closeChunk=True)

        else:

            cmds.warning('No nodes selected!')

    def on_slider_value_changed(self, val):

        #checking selection
        if cmds.ls(selection=True):

            #recording key
            cmds.currentTime(val)

            k = key(time.time(), val)
            self.currentKey.next = k
            k.previous = self.currentKey

            self.currentKey = k

        else:

            cmds.warning('No nodes selected!')


def show():

    win = Window()
    win.show()

show()
