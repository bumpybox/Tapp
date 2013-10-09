'''
- destructor method
- test switching
- test leg build
- better namespaces
- organize code better
- scaling feature
- build spline solver
'''

import Tapp.Maya.rigging.guide as mrg
reload(mrg)
import Tapp.Maya.rigging.solvers as mrs
reload(mrs)
import Tapp.Maya.rigging.meta as meta
reload(meta)

def constructor(points):
    
    #build system
    def getSolverPoints(point,ik=[],fk=[],points=[]):
        
        #adding to fk list
        if point.solverData['FK_solver'] or point.controlData['FK_control']!='None':
            fk.append(point)
        
        #adding to ik list
        if point.solverData['IK_solver'] or point.controlData['IK_control']!='None':
            ik.append(point)
        
        #adding to all list
        points.append(point)
        
        if point.children:
            for child in point.children:
                return getSolverPoints(child,ik=ik,fk=fk,points=points)
        else:
            return {'IK':ik,'FK':fk,'points':points}
    
    for point in points:
        mrs.system(point)
        
        chains=getSolverPoints(point,ik=[],fk=[],points=[])
        
        index=points.index(point)
        
        if chains['IK']:
            mrs.IK(chains['IK'],'ik_%s_' % index)
        
        if chains['FK']:
            mrs.FK(chains['FK'],'fk_%s_' % index)
    
        #build blend
        mrs.blend(chains['points'], 'bld_%s_' % index)
    
    #static parenting
    for point in points:
        mrs.parent(point)

import maya.mel as mel
import maya.cmds as cmds

def destructor():
    
    nodes=meta.r9Meta.getMetaNodes(mTypes=['MetaPoint'])
    
    for node in nodes:
        meta.r9Meta.deleteEntireMetaRigStructure(node[0].mNode)
    
    '''
    roots=[]    
    for node in nodes:
        
        metaNodes=meta.r9Meta.getConnectedMetaNodes(node.mNode,mTypes=['MetaPlug','MetaSocket','MetaControl'])
        
        if metaNodes:
            roots.append(mel.eval('rootOf("%s");' % metaNodes[0].getChildren(cAttrs='node')[0]))
        else:
            roots.append(mel.eval('rootOf("%s");' % node.getChildren(cAttrs='node')[0]))
    
    roots=list(set(roots))
    for root in roots:
        cmds.delete(root)
        '''

#destructor()
points=mrg.destructor()
constructor(points)