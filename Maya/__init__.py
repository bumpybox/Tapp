import os
import sys

import maya.cmds as cmds

import shutil

#import statement
print 'Tapp.Maya imported!'

#creating menu
import menu

#launching window if preferred
cmds.evalDeferred('import Tapp.Maya.settings as ms;ms.startup()')

#adding plugins
cmds.evalDeferred('import Tapp.Maya.plugins')

#framerate prompting
import utils.framerate as uf

uf.FrameratePrompt()

#import Red9
cmds.evalDeferred('import sys;sys.path.append("%s")' % os.path.dirname(__file__))
cmds.evalDeferred('import Tapp.Maya.Red9;Tapp.Maya.Red9.start()')

#import custom Red9 meta
cmds.evalDeferred('import Tapp.Maya.rigging.meta')

#opening command port for Eclipse
try:
    if cmds.commandPort(':7721', q=True) !=1:
        cmds.commandPort(n=':7721', eo = False, nr = True)
except:
    pass

#opening command port for sIBL
try:
    if cmds.commandPort(':2048', q=True) !=1:
        cmds.commandPort(n=':2048', eo = False, nr = True)
except:
    pass