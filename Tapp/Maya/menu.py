import maya.cmds as cmds
import maya.mel as mel

#creating the Tapp menu
gMainWindow = mel.eval('$tmpVar=$gMainWindow')

menuList    = cmds.window(gMainWindow, query=True, menuArray=True)
if 'tappMenu' in menuList:
    cmds.deleteUI('tappMenu')

tappMenu=cmds.menu('tappMenu',label='Tapp',parent=gMainWindow,tearOff=True)

#tapp menu
cmd='import Tapp.Maya.window as win;reload(win);win.show()'
cmds.menuItem(label='Tapp Tools',parent=tappMenu,command=cmd)

#repository menu
subMenu=cmds.menuItem(label='repository',subMenu=True,parent=tappMenu)

cmd='import Tapp.Maya.utils.repository as mur;mur.Change()'
cmds.menuItem(label='Repository Change',parent=subMenu,command=cmd)
cmd='import Tapp.Maya.utils.repository as mur;mur.Read()'
cmds.menuItem(label='Repository Read',parent=subMenu,command=cmd)