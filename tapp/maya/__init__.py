import os
import sys

import maya.cmds as cmds
import maya.mel as mel

# Creating menu
gMainWindow = mel.eval('$tmpVar=$gMainWindow')

menuList = cmds.window(gMainWindow, query=True, menuArray=True)
if 'tappMenu' in menuList:
    cmds.deleteUI('tappMenu')

tappMenu = cmds.menu('tappMenu', label='Tapp', parent=gMainWindow,
                     tearOff=True)

cmd = 'import tapp.maya.gui as gui;reload(gui);win=gui.Window();win.show()'
cmds.menuItem(label='Tapp Tools', parent=tappMenu, command=cmd)

# Setup Red9
sys.path.append(os.path.dirname(__file__))
cmds.evalDeferred('import tapp.maya.Red9;tapp.maya.Red9.start()')
