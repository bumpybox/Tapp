from PyQt4 import QtCore, QtGui
import maya.cmds as cmds
import maya.OpenMayaUI as omu
import sip

from bbt_maya.brt.joysticker import utils

# MQtUtil class exists in Maya 2011 and up
def maya_main_window():
    ptr = omu.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

class joystickDialog(QtGui.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        QtGui.QDialog.__init__(self, parent)
        
        self.setObjectName('joystickDialog')
        self.setWindowTitle('Joysticker')
        
        self.createLayout()
        self.createConnections()
    
    def createLayout(self):
        ''' Creates initial layout '''
        
        mainLayout=QtGui.QVBoxLayout()
        self.setLayout(mainLayout)
        
        # getting file directory ############### needs revising #############################
        fDir='Y:/tools/bumpyboxTools/bbt_maya/brt/joysticker'
        fDir+='/icons'
        
        # Prefix line edit
        layout=QtGui.QHBoxLayout()
        mainLayout.addLayout(layout)
        
        label=QtGui.QLabel('Prefix:')
        layout.addWidget(label)
        
        self.prefix=QtGui.QLineEdit()
        layout.addWidget(self.prefix)
        
        # buttons layout
        buttonsLayout=QtGui.QGridLayout()
        mainLayout.addLayout(buttonsLayout)
        
        # slider A
        self.sliderA=QtGui.QPushButton()
        self.sliderA.setIcon(QtGui.QIcon(fDir+'/sliderA.png'))
        self.sliderA.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderA,0,0)
        
        # slider B
        self.sliderB_east=QtGui.QPushButton()
        self.sliderB_east.setIcon(QtGui.QIcon(fDir+'/sliderB_east.png'))
        self.sliderB_east.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderB_east,1,0)
        
        self.sliderB_north=QtGui.QPushButton()
        self.sliderB_north.setIcon(QtGui.QIcon(fDir+'/sliderB_north.png'))
        self.sliderB_north.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderB_north,1,1)
        
        self.sliderB_south=QtGui.QPushButton()
        self.sliderB_south.setIcon(QtGui.QIcon(fDir+'/sliderB_south.png'))
        self.sliderB_south.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderB_south,1,2)
        
        self.sliderB_west=QtGui.QPushButton()
        self.sliderB_west.setIcon(QtGui.QIcon(fDir+'/sliderB_west.png'))
        self.sliderB_west.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderB_west,1,3)
        
        # slider C
        self.sliderC_east=QtGui.QPushButton()
        self.sliderC_east.setIcon(QtGui.QIcon(fDir+'/sliderC_east.png'))
        self.sliderC_east.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderC_east,2,0)
        
        self.sliderC_horizontal=QtGui.QPushButton()
        self.sliderC_horizontal.setIcon(QtGui.QIcon(fDir+'/sliderC_horizontal.png'))
        self.sliderC_horizontal.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderC_horizontal,2,1)
        
        self.sliderC_north=QtGui.QPushButton()
        self.sliderC_north.setIcon(QtGui.QIcon(fDir+'/sliderC_north.png'))
        self.sliderC_north.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderC_north,2,2)
        
        self.sliderC_south=QtGui.QPushButton()
        self.sliderC_south.setIcon(QtGui.QIcon(fDir+'/sliderC_south.png'))
        self.sliderC_south.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderC_south,2,3)
        
        self.sliderC_vertical=QtGui.QPushButton()
        self.sliderC_vertical.setIcon(QtGui.QIcon(fDir+'/sliderC_vertical.png'))
        self.sliderC_vertical.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderC_vertical,2,4)
        
        self.sliderC_west=QtGui.QPushButton()
        self.sliderC_west.setIcon(QtGui.QIcon(fDir+'/sliderC_west.png'))
        self.sliderC_west.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderC_west,2,5)
        
        # slider D
        self.sliderD_northeast=QtGui.QPushButton()
        self.sliderD_northeast.setIcon(QtGui.QIcon(fDir+'/sliderD_northeast.png'))
        self.sliderD_northeast.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderD_northeast,3,0)
        
        self.sliderD_northwest=QtGui.QPushButton()
        self.sliderD_northwest.setIcon(QtGui.QIcon(fDir+'/sliderD_northwest.png'))
        self.sliderD_northwest.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderD_northwest,3,1)
        
        self.sliderD_southeast=QtGui.QPushButton()
        self.sliderD_southeast.setIcon(QtGui.QIcon(fDir+'/sliderD_southeast.png'))
        self.sliderD_southeast.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderD_southeast,3,2)
        
        self.sliderD_southwest=QtGui.QPushButton()
        self.sliderD_southwest.setIcon(QtGui.QIcon(fDir+'/sliderD_southwest.png'))
        self.sliderD_southwest.setIconSize(QtCore.QSize(75,75))
        buttonsLayout.addWidget(self.sliderD_southwest,3,3)
        
        # combile setups
        self.eyeSetup=QtGui.QPushButton('Eye')
        buttonsLayout.addWidget(self.eyeSetup,4,0)
        
        self.eyesSetup=QtGui.QPushButton('Eyes')
        buttonsLayout.addWidget(self.eyesSetup,4,1)
        
        self.jawSkullSetup=QtGui.QPushButton('Jaw/Skull')
        buttonsLayout.addWidget(self.jawSkullSetup,4,2)
        
        self.mouthSetup=QtGui.QPushButton('Mouth')
        buttonsLayout.addWidget(self.mouthSetup,4,3)
        
    def createConnections(self):
        self.connect(self.sliderA, QtCore.SIGNAL('clicked()'),lambda: utils.sliderA(str(self.prefix.text())))
        
        self.connect(self.sliderB_east, QtCore.SIGNAL('clicked()'),lambda: utils.sliderB_east(str(self.prefix.text())))
        self.connect(self.sliderB_north, QtCore.SIGNAL('clicked()'),lambda: utils.sliderB_north(str(self.prefix.text())))
        self.connect(self.sliderB_south, QtCore.SIGNAL('clicked()'),lambda: utils.sliderB_south(str(self.prefix.text())))
        self.connect(self.sliderB_west, QtCore.SIGNAL('clicked()'),lambda: utils.sliderB_west(str(self.prefix.text())))
        
        self.connect(self.sliderC_east, QtCore.SIGNAL('clicked()'),lambda: utils.sliderC_east(str(self.prefix.text())))
        self.connect(self.sliderC_horizontal, QtCore.SIGNAL('clicked()'),lambda: utils.sliderC_horizontal(str(self.prefix.text())))
        self.connect(self.sliderC_north, QtCore.SIGNAL('clicked()'),lambda: utils.sliderC_north(str(self.prefix.text())))
        self.connect(self.sliderC_south, QtCore.SIGNAL('clicked()'),lambda: utils.sliderC_south(str(self.prefix.text())))
        self.connect(self.sliderC_vertical, QtCore.SIGNAL('clicked()'),lambda: utils.sliderC_vertical(str(self.prefix.text())))
        self.connect(self.sliderC_west, QtCore.SIGNAL('clicked()'),lambda: utils.sliderC_west(str(self.prefix.text())))
        
        self.connect(self.sliderD_northeast, QtCore.SIGNAL('clicked()'),lambda: utils.sliderD_northeast(str(self.prefix.text())))
        self.connect(self.sliderD_northwest, QtCore.SIGNAL('clicked()'),lambda: utils.sliderD_northwest(str(self.prefix.text())))
        self.connect(self.sliderD_southeast, QtCore.SIGNAL('clicked()'),lambda: utils.sliderD_southeast(str(self.prefix.text())))
        self.connect(self.sliderD_southwest, QtCore.SIGNAL('clicked()'),lambda: utils.sliderD_southwest(str(self.prefix.text())))
        
        self.connect(self.eyeSetup, QtCore.SIGNAL('clicked()'),self.eyeCreate)
        self.connect(self.eyesSetup, QtCore.SIGNAL('clicked()'),self.eyesCreate)
        self.connect(self.jawSkullSetup, QtCore.SIGNAL('clicked()'),self.jawSkullCreate)
        self.connect(self.mouthSetup, QtCore.SIGNAL('clicked()'),self.mouthCornerCreate)
        
    def eyeCreate(self,side=''):
        
        topLid=utils.sliderB_south(side+'topLid')
        botLid=utils.sliderB_north(side+'botLid')
        
        cmds.move( 0, 1.125, 0, topLid)
        cmds.move( 0, -1.125, 0, botLid)
        
        grp=cmds.group(topLid,botLid,name=(side+'eye_ui_grp'))
        
        return grp

    def eyesCreate(self):
        
        right=self.eyeCreate('r_')
        left=self.eyeCreate('l_')
        
        cmds.move(-1.125,0,0,right)
        cmds.move(1.125,0,0,left)
        
        cmds.rotate(0,180,0,left)
        
        grp=cmds.group(right,left,name='eyes_ui_grp')
        
        return grp
    
    def jawSkullCreate(self):
        
        jaw=utils.sliderA('jaw_ui')
        skull=utils.sliderA('skull_ui')
        
        cmds.move( 0, -1.125, 0, jaw)
        cmds.move( 0, 1.125, 0, skull)
        
        grp=cmds.group(jaw,skull,name=('jawSkull_ui_grp'))
        
        return grp
    
    def mouthCornerCreate(self):
        
        right=utils.sliderA('r_mouth_ui')
        left=utils.sliderA('l_mouth_ui')
        
        cmds.move(-1.125,0,0,right)
        cmds.move(1.125,0,0,left)
        
        grp=cmds.group(right,left,name=('mouth_ui_grp'))
        
        return grp

def show():
    #closing previous dialog
    for widget in QtGui.qApp.allWidgets():
        if widget.objectName()=='joystickDialog':
            widget.close()
    
    #showing new dialog
    win=joystickDialog()
    win.show()

show()