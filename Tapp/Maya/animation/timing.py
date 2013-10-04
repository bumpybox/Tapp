'''
something is wrong with duration calculation
'''

import os
import time

from PySide import QtGui
from PySide import QtCore
from shiboken import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

import Tapp.Maya.animation.utils as mau

def maya_main_window():
    main_window_ptr=omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)

class key():
    
    def __init__(self,time,keyIndex):
        
        self.time=time
        self.keyIndex=keyIndex
        self.previous=None
        self.next=None

class Window(QtGui.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super(Window,self).__init__(parent)
        
        self.setWindowTitle('Timing Tool')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.create_layout()
        
        self.create_connections()
    
    def create_layout(self):
        
        self.startFrame=cmds.playbackOptions(min=True,q=True)
        self.endFrame=cmds.playbackOptions(max=True,q=True)
        
        self.slider=QtGui.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setTickPosition(QtGui.QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setRange(self.startFrame,self.endFrame)
        self.slider.setValue(cmds.currentTime(q=True))
        
        main_layout=QtGui.QVBoxLayout()
        main_layout.addWidget(self.slider)
        
        self.setLayout(main_layout)
    
    def create_connections(self):
        
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderReleased.connect(self.on_slider_released)
    
    def on_slider_pressed(self):
        
        k=key(time.time(),int(cmds.currentTime(q=True)))
        self.currentKey=k
    
    def _findStart(self,key):
        
        if key.previous:
            return self._findStart(key.previous)
        else:
            return key
    
    def _printDownstream(self,key):
        
        print '---'
        print 'keyIndex:%s' % key.keyIndex
        print 'time:%s' % key.time
        if key.next:
            print 'duration:%s f' % str((key.next.time - key.time)*25)
        
        if key.next:
            self._printDownstream(key.next)
    
    def _pasteTiming(self,source,target,key):
        
        if key.next:
            cmds.copyKey(source,time=(key.keyIndex,key.keyIndex))
            
            cmds.pasteKey(target,time=(self.currentTime,self.currentTime))
            
            self.currentTime=self.currentTime+((key.next.time - key.time)*25)
            
            self._pasteTiming(source, target, key.next)
        else:
            return
    
    def on_slider_released(self):
        
        start=self._findStart(self.currentKey)
        #self._printDownstream(start)
        
        #undo enable
        cmds.undoInfo(openChunk=True)
        
        obj=cmds.ls(selection=True)[0]
        for t in range(int(self.startFrame),int(self.endFrame)+1):
            
            cmds.currentTime(t)
            cmds.setKeyframe(obj)
        
        #transfer original animation to temp transform
        loc=cmds.spaceLocator()[0]
        cmds.cutKey(obj,time=(self.startFrame,self.endFrame) )
        cmds.pasteKey(loc)
         
        #paste timing
        self.currentTime=self.startFrame
        self._pasteTiming(loc, obj, start)
        
        #cleanup
        cmds.delete(loc)
        cmds.keyTangent(obj,itt='auto',ott='auto')
        cmds.delete(staticChannels=True)
        
        cmds.undoInfo(closeChunk=True)
    
    def on_slider_value_changed(self,val):
        
        cmds.currentTime(val)
        
        k=key(time.time(),val)
        self.currentKey.next=k
        k.previous=self.currentKey
        
        self.currentKey=k

win=Window()
win.show()