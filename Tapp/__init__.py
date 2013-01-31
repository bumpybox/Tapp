import sys
import os

#import statement
print 'Tapp imported!'

#determine interpreter
interpreterPath=sys.executable

[filepath,filename]=os.path.split(interpreterPath)

appname=filename.split('.')[0]

#importing relevant app module
if appname=='maya':
    import Tapp.Maya

if appname=='Nuke6':
    import Tapp.Nuke