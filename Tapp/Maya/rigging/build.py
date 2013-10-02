import Tapp.Maya.rigging.guide as mrg
import Tapp.Maya.rigging.meta as meta

def constructor(points):
    
    #build system
    def createPoint(point,parent=None):
        if parent:
            metaNode=parent.addPoint(name=point.name)
        else:
            metaNode=meta.MetaPoint(name='meta_'+point.name)
        
        point.meta=metaNode
        
        if point.children:
            for child in point.children:
                createPoint(child,parent=metaNode)
    
    for point in points:
        createPoint(point)
    
    #build solvers
        #breakdown data to chunks
    
        #pass on chunks to solvers
    
    #build blend
    
    
    
    pass

def destructor():
    
    pass

nodes=mrg.destructor()
constructor(nodes)