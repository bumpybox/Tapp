import maya.cmds as cmds
import maya.mel as mel

#creating the Glapp menu
gMainWindow = mel.eval('$tmpVar=$gMainWindow')

menuList    = cmds.window(gMainWindow, query=True, menuArray=True)
if 'tappMenu' in menuList:
    cmds.deleteUI('tappMenu')

cmds.menu('tappMenu',label='Tapp',parent=gMainWindow,tearOff=True)