import Tapp.Maya.rigging.guide as mrg
reload(mrg)
import Tapp.Maya.rigging.solvers as mrs
reload(mrs)
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
    
    def getSolverPoints(point,ik=[],fk=[]):
        
        #adding to fk list
        if point.solverData['FK_solver'] or point.controlData['FK_control']!='None':
            fk.append(point)
        
        #adding to ik list
        if point.solverData['IK_solver'] or point.controlData['IK_control']!='None':
            ik.append(point)
        
        if point.children:
            for child in point.children:
                return getSolverPoints(child,ik=ik,fk=fk)
        else:
            return {'IK':ik,'FK':fk}
    
    for point in points:
        createPoint(point)
        
        chains=getSolverPoints(point,ik=[],fk=[])
        
        index=points.index(point)
        
        if chains['IK']:
            mrs.ik(chains['IK'],'ik_%s_' % index)
        
        if chains['FK']:
            mrs.fk(chains['FK'],'fk_%s_' % index)
    
    #build blend

def destructor():
    
    pass

points=mrg.destructor()
constructor(points)