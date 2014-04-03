import os

import maya.cmds as cmds
import yaml

cmds.loadPlugin('AbcExport.mll', quiet=True)
cmds.loadPlugin('AbcImport.mll', quiet=True)

#adding plugins path
path = os.path.dirname(yaml.__file__)
path = os.path.abspath(os.path.join(os.path.dirname(path),".."))
path = os.path.join(path, 'Maya', 'plugins')
os.environ['MAYA_PLUG_IN_PATH'] += ';%s' % path.replace('\\', '/')

#importing Tapp
cmds.evalDeferred('import Tapp')
