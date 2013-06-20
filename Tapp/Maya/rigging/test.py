import Tapp.Maya.rigging.builds as mrb
reload(mrb)

print mrb.mrs.system('|clavicle')

'''
need to have args* on all
need to treat chain as the data container it is! still need to be able to build a system directly from a node, instead of having to build the chain first
    chain should not container anything to do with the system or build
should treat the system as an overall system container, and have no operations specific to a build
plugs!
build spline
possibly need to not have one attr for activating systems, and go to each socket and activate the system if its present
hook up controls visibility to blend control
better inheritance model
place guides like clusters tool
    if multiple verts, use one of them to align the guide towards
'''