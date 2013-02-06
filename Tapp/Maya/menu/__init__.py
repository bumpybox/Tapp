import maya.cmds as cmds
import maya.mel as mel

#creating the Glapp menu
gMainWindow = mel.eval('$tmpVar=$gMainWindow')

menuList    = cmds.window(gMainWindow, query=True, menuArray=True)
if 'tappMenu' in menuList:
    cmds.deleteUI('tappMenu')

tappMenu=cmds.menu('tappMenu',label='Tapp',parent=gMainWindow,tearOff=True)

#repository menu
cmd='import Tapp.Maya.utils.repository as mur;repo=mur.Repository();repo.Change()'
cmds.menuItem(label='Repository Change',parent=tappMenu,command=cmd)