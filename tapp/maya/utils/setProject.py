import os

import maya.cmds as cmds

path = os.path.dirname(cmds.file(q=True, sn=True))

cmds.workspace(fileRule=['scenes', path])

cmds.workspace(path, openWorkspace=True)
