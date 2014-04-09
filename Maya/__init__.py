import os
import sys

import maya.cmds as cmds

import shutil

#import statement
print 'Tapp.Maya imported!'

#creating menu
import menu

#framerate prompting
import utils.framerate as uf

uf.FrameratePrompt()

#setting project
cmds.evalDeferred('import Tapp.Maya.utils.setProject')

#load plugins
cmds.evalDeferred('import Tapp.Maya.plugins')

#import Red9
sys.path.append(os.path.dirname(__file__))
cmds.evalDeferred('import Tapp.Maya.Red9;Tapp.Maya.Red9.start()')

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