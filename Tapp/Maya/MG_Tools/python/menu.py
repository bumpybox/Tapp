import os

import maya.cmds as cmds
import maya.mel as mel

#creating the MG_Tools menu
gMainWindow = mel.eval('$tmpVar=$gMainWindow')

menuList    = cmds.window(gMainWindow, query=True, menuArray=True)
if 'MG_Tools_Menu' in menuList:
    cmds.deleteUI('MG_Tools_Menu')

MG_Tools_Menu=cmds.menu('MG_Tools_Menu',label='MG_Tools',parent=gMainWindow,tearOff=True)

#building cmd for menus
fileDir=os.path.dirname(__file__)

commands={}
for subdir in os.listdir(fileDir):
    
    #traverse into sub folders 
    if os.path.isdir(os.path.join(fileDir, subdir)):
        for submenuDir in os.listdir(os.path.join(fileDir, subdir)):
            
            #checking if there is a folder called 'GUI'
            if submenuDir=='GUI':
                
                #create submenu
                subMenu=cmds.menuItem(label=subdir,subMenu=True,parent=MG_Tools_Menu)
                
                #create menu items
                for item in os.listdir(os.path.join(fileDir, subdir,submenuDir)):               

                    if item.split('.')[-1]=='py' and item.split('.')[0]!='__init__':
                        
                        cmd='import MG_Tools.python.%s.GUI.%s as gui;reload(gui);gui.show()' % (subdir,item.split('.')[0])
                        cmds.menuItem(label=item.split('.')[0],parent=subMenu,command=cmd)