import os

import maya.cmds as cmds

#import statement
print 'Tapp.Maya imported!'

#creating menu
import menu

#opening command port for Eclipse
if cmds.commandPort(':7720', q=True) !=1:
    cmds.commandPort(n=':7720', eo = False, nr = True)

#opening command port for sIBL
if cmds.commandPort(':2048', q=True) !=1:
    cmds.commandPort(n=':2048', eo = False, nr = True)