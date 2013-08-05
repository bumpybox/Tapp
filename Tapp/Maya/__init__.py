import os
import sys

import maya.cmds as cmds

#import statement
print 'Tapp.Maya imported!'

#creating menu
import menu

#launching window if preferred
cmds.evalDeferred('import Tapp.Maya.settings as ms;ms.startup()')

#framerate prompting
import utils.framerate as uf

uf.FrameratePrompt()

#import Red9
cmds.evalDeferred('import Tapp.Maya.Red9;Tapp.Maya.Red9.start()')

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