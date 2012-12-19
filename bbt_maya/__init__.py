import os

import maya.mel as mel
import maya.cmds as cmds

#//////////////Setup Maya////////////////////////////
print 'Importing Bumpybox Maya Tools'

#Building Bumpybox menu
import menu
'''
#Showing BAT
import bat
from bat import gui

gui.show()
'''
#Modifying Maya File Menu to use auto project setup
import bgt
from bgt import utils

project=utils.project()
project.setup()

#Sourcing Mel Scripts
def sourceMelScripts():
        tempDir = os.path.dirname(__file__)+'/mel'
        scriptsFolder=tempDir.replace('\\','/')
        for root, dirs, files in os.walk(scriptsFolder):
            for x in files:
                if x.endswith('.mel'):
                    try:
                        mel.eval('source "'+scriptsFolder+'/'+x+'"')
                    except:
                        cmds.warning('Sourcing of '+x+' failed.')

sourceMelScripts()

#opening for command port for Eclipse
if cmds.commandPort(':7720', q=True) !=1:

    cmds.commandPort(n=':7720', eo = False, nr = True)