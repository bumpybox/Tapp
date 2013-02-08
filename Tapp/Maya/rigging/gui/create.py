import os
import sys

import Tapp.Maya.rigging.modules as modules

def Import(modulePath):
    f = os.path.basename( modulePath )
    d = os.path.dirname( modulePath )
 
    toks = f.split( '.' )
    modname = toks[0]
 
    # Check if dirrectory is really a directory
    if( os.path.exists( d ) ):
 
    # Check if the file directory already exists in the sys.path array
        paths = sys.path
        pathfound = 0
        for path in paths:
            if(d == path):
                pathfound = 1
 
    # If the dirrectory is not part of sys.path add it
        if not pathfound:
            sys.path.append( d )
 
    # exec works like MEL's eval but you need to add in globals() 
    # at the end to make sure the file is imported into the global 
    # namespace else it will only be in the scope of this function
    exec ('import ' + modname+' as modules') in globals()
    
    modules.Create()