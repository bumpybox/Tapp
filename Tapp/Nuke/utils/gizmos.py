import os

import nuke

gizmosPath=None

if gizmosPath:
    #add gizmosPath
    nuke.pluginAddPath(gizmosPath)
    
    #adding menu items
    menubar = nuke.menu("Nuke")
    
    for item in os.listdir(gizmosPath):
        name=item.split('.')[0]
        
        nuke.menu('Nuke').addCommand('Tapp/Gizmos/%s' % name,'nuke.createNode(\'%s\')' % name)