import os

import maya.cmds as cmds

#import statement
print 'Tapp.Maya imported!'

#creating menu
import menu

#framerate prompting
import utils.framerate as uf

uf.FrameratePrompt()

#opening command port for Eclipse
try:
    if cmds.commandPort(':7720', q=True) !=1:
        cmds.commandPort(n=':7720', eo = False, nr = True)
except:
    pass

#opening command port for sIBL
try:
    if cmds.commandPort(':2048', q=True) !=1:
        cmds.commandPort(n=':2048', eo = False, nr = True)
except:
    pass