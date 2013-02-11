import maya.cmds as cmds
import maya.mel as mel

#creating the Tapp menu
gMainWindow = mel.eval('$tmpVar=$gMainWindow')

menuList    = cmds.window(gMainWindow, query=True, menuArray=True)
if 'tappMenu' in menuList:
    cmds.deleteUI('tappMenu')

tappMenu=cmds.menu('tappMenu',label='Tapp',parent=gMainWindow,tearOff=True)

#rigging menu
subMenu=cmds.menuItem(label='rigging',subMenu=True,parent=tappMenu)

cmd='import Tapp.Maya.rigging.gui as mrg;mrg.show()'
cmds.menuItem(label='Tapp Maya Rigging',parent=subMenu,command=cmd)

#repository menu
subMenu=cmds.menuItem(label='repository',subMenu=True,parent=tappMenu)

cmd='import Tapp.Maya.utils.repository as mur;mur.Change()'
cmds.menuItem(label='Repository Change',parent=subMenu,command=cmd)
cmd='import Tapp.Maya.utils.repository as mur;mur.Read()'
cmds.menuItem(label='Repository Read',parent=subMenu,command=cmd)