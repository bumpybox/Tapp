import os

path=os.path.join(os.path.dirname(__file__),'plugins')
plugPaths=os.environ.get('MAYA_PLUG_IN_PATH')

if not path in plugPaths: 
    print 'Adding Tapp Plug-ins to Plugin Paths : %s' % path
    os.environ['MAYA_PLUG_IN_PATH']+='%s%s' % (os.pathsep,path)
else:
    print 'Tapp Plug-in Path already setup'