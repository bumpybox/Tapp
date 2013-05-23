import maya.cmds as cmds
import maya.mel as mel

#creating the Tapp menu
gMainWindow = mel.eval('$tmpVar=$gMainWindow')

menuList    = cmds.window(gMainWindow, query=True, menuArray=True)
if 'tappMenu' in menuList:
    cmds.deleteUI('tappMenu')

tappMenu=cmds.menu('tappMenu',label='Tapp',parent=gMainWindow,tearOff=True)

#modelling menu
subMenu=cmds.menuItem(label='modelling',subMenu=True,parent=tappMenu)

cmd='import Tapp.Maya.modelling.GUI.triangulatePivot as mmgt;reload(mmgt);mmgt.show()'
cmds.menuItem(label='Triangulate Pivot',parent=subMenu,command=cmd)

#rigging menu
subMenu=cmds.menuItem(label='rigging',subMenu=True,parent=tappMenu)

cmd='import Tapp.Maya.rigging.gui as mrg;reload(mrg);mrg.show()'
cmds.menuItem(label='Tapp Maya Rigging',parent=subMenu,command=cmd)

#animation menu
subMenu=cmds.menuItem(label='animation',subMenu=True,parent=tappMenu)

cmd='import Tapp.Maya.animation.gui as mag;reload(mag);mag.show()'
cmds.menuItem(label='Tapp Maya Animation',parent=subMenu,command=cmd)

#animation menu
subMenu=cmds.menuItem(label='lighting',subMenu=True,parent=tappMenu)

cmd='import Tapp.Maya.lighting.gui as mlg;reload(mlg);mlg.show()'
cmds.menuItem(label='Tapp Maya Lighting',parent=subMenu,command=cmd)

#repository menu
subMenu=cmds.menuItem(label='repository',subMenu=True,parent=tappMenu)

cmd='import Tapp.Maya.utils.repository as mur;mur.Change()'
cmds.menuItem(label='Repository Change',parent=subMenu,command=cmd)
cmd='import Tapp.Maya.utils.repository as mur;mur.Read()'
cmds.menuItem(label='Repository Read',parent=subMenu,command=cmd)