import maya.cmds as cmds
import maya.mel as mel

#creating the Tapp menu
gMainWindow = mel.eval('$tmpVar=$gMainWindow')

menuList = cmds.window(gMainWindow, query=True, menuArray=True)
if 'tappMenu' in menuList:
    cmds.deleteUI('tappMenu')

tappMenu = cmds.menu('tappMenu', label='Tapp', parent=gMainWindow,
                     tearOff=True)

#tapp menu
cmd = 'import Tapp.Maya.gui as gui;reload(gui);win=gui.Window();win.show()'
cmds.menuItem(label='Tapp Tools', parent=tappMenu, command=cmd)
