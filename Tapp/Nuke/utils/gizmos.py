import os

import nuke

gizmosPath=r'Y:\resources\warehouse\Nuke Gizmos'

#add gizmosPath
nuke.pluginAddPath(gizmosPath)

#adding menu items
menubar = nuke.menu("Nuke")

for item in os.listdir(gizmosPath):
    name=item.split('.')[0]
    
    nuke.menu('Nuke').addCommand('Tapp/Gizmos/%s' % name,'nuke.createNode(\'%s\')' % name)