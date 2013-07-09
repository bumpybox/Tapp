import maya.cmds as cmds

import Tapp.Maya.rigging.meta as meta
reload(meta)

system=meta.MetaSystem()

node=cmds.spaceLocator()[0]
system.addPlug(node)

node=cmds.spaceLocator()[0]
system.addSocket(node)

node=cmds.spaceLocator()[0]
system.addControl(node)