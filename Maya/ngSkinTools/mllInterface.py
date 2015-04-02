#
#    ngSkinTools
#    Copyright (c) 2009-2014 Viktoras Makauskas. 
#    All rights reserved.
#    
#    Get more information at 
#        http://www.ngskintools.com
#    
#    --------------------------------------------------------------------------
#
#    The coded instructions, statements, computer programs, and/or related
#    material (collectively the "Data") in these files are subject to the terms 
#    and conditions defined by
#    Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License:
#        http://creativecommons.org/licenses/by-nc-nd/3.0/
#        http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode
#        http://creativecommons.org/licenses/by-nc-nd/3.0/legalcode.txt
#         
#    A copy of the license can be found in file 'LICENSE.txt', which is part 
#    of this source code package.
#    

import maya.cmds as cmds
import maya.mel as mel
from ngSkinTools.log import LoggerFactory
from ngSkinTools.utils import MessageException
from ngSkinTools.layerUtils import LayerUtils
from itertools import izip

class MllInterface(object):
    '''
    
    A wrapper object to call functionality from ngSkinLayer command.
    Most operations operate on current selection, or on target mesh that
    was set in advance. All edit operations are undoable.
    
    Example usage:
    
    .. code-block:: python
        
        from ngSkinTools.mllInterface import MllInterface
    
        mll = MllInterface()
        mll.setCurrentMesh('myMesh')
        
        mll.initLayers()
        id = mll.createLayer('initial weights')
        mll.setInfluenceWeights(id,0,[0.0,0.0,1.0,1.0])
        
        ...
    
    '''
    
    log = LoggerFactory.getLogger("MllInterface")
    
    TARGET_REFERENCE_MESH = 'ngSkinTools#TargetRefMesh'


    def __init__(self,mesh=None):
        self.setCurrentMesh(mesh)
        
    def setCurrentMesh(self,mesh):
        '''
        Set mesh we'll be working on with in this wrapper. Use None to operate on current selection instead. 
        '''
        self.mesh = mesh
        
    def initLayers(self):
        '''
        initializes layer data node setup for target mesh
        '''
        self.ngSkinLayerCmd(lda=True)
        
    def getLayersAvailable(self):
        '''
        returns true if layer data is available for target mesh
        '''
        try:
            return self.ngSkinLayerCmd(q=True,lda=True)
        except Exception,err:
            self.log.error(err)
            import traceback;traceback.print_exc()
            return False 
        
    def getCurrentLayer(self):
        '''
        get layer that is marked as selected on MLL side; current layer is used for many things, for example, as a paint target.
        '''
        return self.ngSkinLayerCmd(q=True,cl=True)

    def getCurrentInfluence(self):
        '''
        returns a tuple, containing current influence logical index and DAG path
        '''
        return self.ngSkinLayerCmd(q=True,ci=True)
        
        
    def getTargetInfo(self):
        '''
        Returns a tuple with mesh and skin cluster node names where skinLayer data
        is (or can be) attached.
        
        If current mesh (or selection) is not suitable for attaching layers,
        returns None
        '''
        try:
            result = self.ngSkinLayerCmd(q=True,ldt=True)
            if len(result)==2:
                return result
        except MessageException,err:
            raise err
        except:
            return None
        
        return None
        
        
    def getVertCount(self):
        '''
        For initialized layer info, returns number of vertices layer manager sees in the mesh.
        This might be different to actual vertex count in the mesh, if mesh has post-skin cluster mesh
        modifiers (as vertex merge or smooth) 
        '''
        return self.ngSkinLayerCmd(q=True,vertexCount=True)
        
    
    def getLayerName(self,layerId):
        '''
        get layer name by ID
        '''
        return self.ngSkinLayerCmdMel("-id %d -q -name" % layerId)    
    
    def setLayerName(self,layerId,name):
        '''
        set layer name by ID
        '''
        self.ngSkinLayerCmd(e=True,id=layerId,name=name)
                
    def getLayerOpacity(self,layerId):
        '''
        Returns layer opacity as float between ``0.0`` and ``1.0``
        '''
        return float(self.ngSkinLayerCmdMel('-id %d -q -opacity' % layerId))

    def setLayerOpacity(self,layerId,opacity):
        '''
        Set opacity for given layer. Use values between ``0.0`` and ``1.0``
        '''
        self.ngSkinLayerCmd(e=True,id=layerId,opacity=opacity)
        
    def isLayerEnabled(self,layerId):
        '''
        Returns ``True``, if layer on/off flag is turned on
        '''
        return bool(self.ngSkinLayerCmdMel('-id %d -q -enabled' % layerId))

    def setLayerEnabled(self,layerId,enabled):
        '''
        Turn layer on/off. Use ``True`` / ``False`` for 'enabled' value.
        '''
        self.ngSkinLayerCmd(e=True,id=layerId,enabled=enabled)
    
    
    def listLayers(self):
        '''
        returns iterator to layer list; each element is a tuple: ``(layer ID, layer name)`` 
        '''
        layers = self.ngSkinLayerCmd(q=True,listLayers=True)
        argsPerLayer = 3
        for i in xrange(len(layers)/argsPerLayer):
            # layerID, layerName
            yield int(layers[i*argsPerLayer]),layers[i*argsPerLayer+1]
        
    
    def listLayerInfluences(self,layerId,activeInfluences=True):
        '''
        returns iterator to layer influences. each element is a tuple ``(influence name,influence logical index)``
        '''
        
        cmd = '-id %d -q -listLayerInfluences'
        if activeInfluences:
            cmd+= " -activeInfluences"
        influences = self.ngSkinLayerCmdMel(cmd % layerId)
        for j in xrange((len(influences)-1)/2):
            yield influences[j*2+1],int(influences[j*2+2])

    
    def __asTypeList(self,_type,result):
        if result is None:
            return []
        
        return map(_type,result)
    
    def __asFloatList(self,result):
        return self.__asTypeList(float, result)

    def __asIntList(self,result):
        return self.__asTypeList(int, result)
    
    def __floatListAsString(self,floatList):
        def formatFloat(value):
            return str(value)
        
        return ",".join(map(formatFloat, floatList))

    def __intListAsString(self,values):
        return ",".join(map(str,values))
        

    def getLayerMask(self,layerId):
        '''
        returns layer mask weights as float list. if mask is not initialized, returns empty list
        '''
        return self.__asFloatList(self.ngSkinLayerCmdMel('-id %d -paintTarget mask -q -w' % layerId))

    def setLayerMask(self,layerId,weights):
        '''
        Set mask for given layer. Supply float list for weights, e.g. ``[0.0,1.0,0.6]``.
        Supply empty list to set mask into uninitialized state.
        '''
        self.ngSkinLayerCmd(e=True,id=int(layerId),paintTarget='mask',w=self.__floatListAsString(weights))
        
    def getInfluenceWeights(self,layerId,influenceLogicalIndex):
        '''
        returns influence weights as float list. For influence, provide logical index in skinCluster.matrix[] this influence connects to. 
        '''
        return self.__asFloatList(self.ngSkinLayerCmdMel('-id %d -paintTarget influence -iid %d -q -w ' % (layerId,influenceLogicalIndex,)))


    def setInfluenceWeights(self,layerId,influenceLogicalIndex,weights):
        '''
        Set weights for given influence in a layer. Provide weights as float list; vertex count should match result of :py:meth:`~.getVertCount`
        '''
        self.ngSkinLayerCmd(e=True,id=int(layerId),paintTarget='influence',iid=int(influenceLogicalIndex),w=self.__floatListAsString(weights))
    
    def ngSkinLayerCmd(self,*args,**kwargs):
        if self.mesh is not None:
            if self.mesh==self.TARGET_REFERENCE_MESH:
                kwargs['targetReferenceMesh'] = True
            else:
                args = (self.mesh,)+args
        return cmds.ngSkinLayer(*args,**kwargs)
            
    
    def ngSkinLayerCmdMel(self,melCmd):
        melCmd = "ngSkinLayer "+melCmd
        if self.mesh is not None:
            if self.mesh==MllInterface.TARGET_REFERENCE_MESH:
                melCmd += " -targetReferenceMesh"
            else:  
                melCmd += " " + self.mesh
        
        self.log.info(melCmd)
        return mel.eval(melCmd)
    
    
    def createLayer(self,name,forceEmpty=False):
        '''
        creates new layer with given name and returns it's ID; when forceEmpty flag is set to true, 
        layer weights will not be populated from skin cluster.
        '''
        return self.ngSkinLayerCmd(name=name,add=True,forceEmpty=forceEmpty)
    
    def deleteLayer(self,layerId):
        '''
        Deletes given layer in target mesh
        '''
        self.ngSkinLayerCmd(rm=True,id=layerId)
    
    
    def setCurrentLayer(self,layerId):
        '''
        Set current layer to given value
        '''
        return self.ngSkinLayerCmd(cl=layerId)  
    
    def setCurrentPaintTarget(self,paintTarget):
        '''
        universal way to set current paint target. Paint target can be 
        LayerUtils.PAINT_TARGET_MASK or a layer id
        '''
        #if id>=0:
        self.ngSkinLayerCmd(ci=paintTarget)
        #elif id==LayerUtils.PAINT_TARGET_MASK:
        #    self.ngSkinLayerCmd(cpt="mask")
            
            
    def getCurrentPaintTarget(self):
        '''
        just an alias for getCurrentInfluence(); should be cleaned up once
        all paint targets start using unified API 
        '''
        return self.getCurrentInfluence()[0]
        
    
        
    def getMirrorAxis(self):
        '''
        Get axis that is used in the mirror operation. Can be one of: 'x', 'y', 'z', or 'undefined' 
        '''
        return self.ngSkinLayerCmd(q=True,mirrorAxis=True)
    
     
    def mirrorLayerWeights(self,layerId,mirrorWidth,mirrorLayerWeights,mirrorLayerMask,mirrorDirection):        
        self.ngSkinLayerCmd(
                id = layerId,
                mirrorWidth=mirrorWidth,
                mirrorLayerWeights=mirrorLayerWeights,
                mirrorLayerMask=mirrorLayerMask,
                mirrorDirection=mirrorDirection
            )
        
    
    def beginDataUpdate(self):
        '''
        starts batch data update mode, putting layer data into suspended state - certain 
        internal updates are switched off, making multiple layer data changes like setLayerWeights 
        or setLayerOpacity run faster; updates will take place when endDataUpdate is called.
        
        begin..endDataUpdate() pairs can be stacked (e.g. methods inside begin..end can call begin..end
        themselves) - updates will resume only when most outer pair finishes executing.
        '''
        self.ngSkinLayerCmd(beginDataUpdate=True)

    def endDataUpdate(self):
        '''
        end batch update.
        '''
        self.ngSkinLayerCmd(endDataUpdate=True)
        
    def batchUpdateContext(self):
        '''
        a helper method to use in a "with" statement, e.g.:

        .. code-block:: python
            
            with mll.batchUpdateContext():
                mll.setLayerWeights(...)
                mll.setLayerOpacity(...)
                
        this is the same as:
        
        .. code-block:: python
        
            mll.beginDataUpdate()
            try:
                mll.setLayerWeights(...)
                mll.setLayerOpacity(...)
            finally:
                mll.endDataUpdate()
        '''
        
        return BatchUpdateContext(self)
    
    def setWeightsReferenceMesh(self,vertices,triangles):
        '''
        create an in-memory reference mesh with layer manager initialized;
        this mesh and layer info can be accessed later by setting target mesh to 
        MllInterface.TARGET_REFERENCE_MESH.
        
        
        vertices is a float array, listing x y z for first vertex, then second, etc;
        triangles is an int array, listing vertex IDs for first triangle, then second, etc.
        '''
        
        self.ngSkinLayerCmd(e=True,
                    referenceMeshVertices=self.__floatListAsString(vertices),
                    referenceMeshTriangles=self.__intListAsString(triangles)
                    )
        
    def getReferenceMeshVerts(self):
        '''
        returns a list of floats, where each three values is a vertex XYZ for reference mesh vertices
        '''
        return self.ngSkinLayerCmd(q=True,
                    referenceMeshVertices=True)
        
    def getReferenceMeshTriangles(self):
        '''
        returns a list of ints, where each three values describe mesh vert IDs that make up a triangle in the reference mesh
        '''
        return self.ngSkinLayerCmd(q=True,
                    referenceMeshTriangles=True)
        

    def addManualMirrorInfluenceAssociation(self,source,destination):
        '''
        adds an override to mirror influence association, a rule specifying that "source" influence weights
        should be copied on to "destination" influence on another side. 
        for bidirectional (e.g. L_wrist<->R_wrist) relationships, call method twice for both directions;
        for self-reference (e.g., "hip mirrors onto itself"), specify source and destination as same influence
        '''
        self.ngSkinLayerCmd(mirrorInfluenceAssociation=source+","+destination)
        
    def removeManualMirrorInfluenceAssociation(self,source,destination):
        self.ngSkinLayerCmd(removeMirrorInfluenceAssociation=source+","+destination)
        
        
    def getInfluenceLimitPerVertex(self):
        return self.ngSkinLayerCmd(q=True,influenceLimitPerVertex=True)
    
    def setInfluenceLimitPerVertex(self,limit=None):
        if limit is None:
            limit=0
        self.ngSkinLayerCmd(e=True,influenceLimitPerVertex=limit)
        
    def listInfluenceIndexes(self):
        return self.ngSkinLayerCmd(q=True,influenceIndexes=True)

    def listInfluencePaths(self):
        return self.ngSkinLayerCmd(q=True,influencePaths=True)
    
    def listInfluencePivots(self):
        return self.ngSkinLayerCmd(q=True,influencePivots=True)
    
    def listInfluenceInfo(self):  
        from importExport import InfluenceInfo  

        influenceIndexes = self.listInfluenceIndexes()
        if not influenceIndexes:
            return [] 
        
        influences = []
        
        influencePaths = self.listInfluencePaths()
        influencePivots = self.listInfluencePivots()
        influencePivots = izip(influencePivots[0::3],influencePivots[1::3],influencePivots[2::3])
        for index,path,pivot in izip(influenceIndexes,influencePaths,influencePivots):
            influence = InfluenceInfo()
            influence.pivot = pivot
            influence.path = path
            influence.logicalIndex = index
            influences.append(influence)
        
        return influences

    @staticmethod
    def influencesMapToList(influencesMapping):
        return ','.join(str(k)+","+str(v) for (k,v) in influencesMapping.items())
    
    def transferWeights(self,targetMesh,influencesMapping):
        self.ngSkinLayerCmd(targetMesh,transferSkinData=True,influencesMapping=self.influencesMapToList(influencesMapping))
        
    def setManualMirrorInfluences(self,sourceDestinationMap):
        self.ngSkinLayerCmd(manualInfluenceMappings=self.influencesMapToList(sourceDestinationMap))
        
    def getManualMirrorInfluences(self):
        values = self.ngSkinLayerCmd(q=True,manualInfluenceMappings=True)
        if values is None:
            return {}
        return dict(zip(values[0::2],values[1::2]))
    
    def layerMergeDown(self,layerId):
        self.ngSkinLayerCmd(e=True,layerId=layerId,layerMergeDown=True)
        
    def getLayerIndex(self,layerId):
        return self.ngSkinLayerCmdMel("-id %d -q -layerIndex" % layerId)
    
    def pruneWeights(self,layerId=None,threshold=0.01):
        '''
        remove weights in influence weights lower than provided threshold;
        upscale remaining weights, preserving transparency of the layer. 
        '''
        self.ngSkinLayerCmd(e=True,layerId=layerId,pruneWeights=True,pruneWeightsThreshold=threshold)
    
    def pruneMask(self,layerId=None,threshold=0.01):
        '''
        remove weights in layer mask lower than provided threshold;
        '''
        self.ngSkinLayerCmd(e=True,layerId=layerId,pruneMask=True,pruneWeightsThreshold=threshold)
    
    def setPruneWeightsFilter(self,threshold):
        self.ngSkinLayerCmd(e=True,pruneWeightsFilterThreshold=threshold)

    def getPruneWeightsFilter(self):
        return self.ngSkinLayerCmd(q=True,pruneWeightsFilterThreshold=True)
        
        
        
class BatchUpdateContext:
    '''
    A helper class for MllInterface.batchUpdateContext() method, helping 
    implement "with" statement setup/teardown functionality
    '''
    def __init__(self,mll):
        self.mll = mll
        
    def __enter__(self):
        self.mll.beginDataUpdate()
        return self.mll
    
    def __exit__(self, _type, value, traceback):
        self.mll.endDataUpdate()
