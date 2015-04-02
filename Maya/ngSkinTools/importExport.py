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

'''
Example export:

.. code-block:: python

    data = LayerData()
    data.loadFrom('skinnedMesh')
    exporter = XmlExporter()
    xml = exporter.process(data)
    saveXmlToFile(xml,'path/to/my.xml') # write contents to file here

Example import:

.. code-block:: python

    importer = XmlImporter()
    xml = loadFileData('path/to/my.xml') # read file contents here
    data = importer.process(xml)
    data.saveTo('skinnedMesh')

'''
from __future__ import with_statement
from ngSkinTools.mllInterface import MllInterface
from ngSkinTools.utils import Utils, MessageException
from maya import cmds
from maya import OpenMaya as om
from maya import OpenMayaAnim as oma
from ngSkinTools import utils
from ngSkinTools.skinClusterFn import SkinClusterFn
from ngSkinTools.meshDataExporter import MeshDataExporter
from itertools import izip

class Influence(object):
    '''
    Single influence in a layer
    '''
    
    def __init__(self):
        
        # influence logical index in a skin cluster
        self.logicalIndex = -1
        
        # full path of the influence in the scene
        self.influenceName = None
        
        # influence weights for each vertex (list of double)
        self.weights = []
        
    def __repr__(self):
        return "[Infl %r]" % (self.influenceName)
        

class Layer(object):
    '''
    Represents single layer; can contain any amount of influences.
    '''
    
    def __init__(self):
        # layer name
        self.name = None
        
        # layer opacity
        self.opacity = 0.0
        
        # layer on/off flag
        self.enabled = False
        
        # list of influences in this layer with their weights (list of Influence)
        self.influences = []
        
        # layer mask (could be None or list of double)
        self.mask = None
        
    def addInfluence(self, influence):
        '''
        Register :class:`Influence` for given layer
        '''
        
        assert isinstance(influence, Influence)
        self.influences.append(influence)
        
    def __repr__(self):
        return "[Layer %r %r %r %r]" % (self.name, self.opacity, self.enabled, self.influences)
    
class MeshInfo(object):
    def __init__(self):
        # vertex positions for each vertex, listing x y z for first vertex, then second, etc.
        # total 3*(number of vertices) values
        self.verts = []
        
        # vertex IDs for each triangle, listing three vertex indexes for first triangle, then second, etc
        # total 3*(number of triangles) values
        self.triangles = []
        

class InfluenceInfo(object):
    def __init__(self,pivot=None,path=None,logicalIndex=None):
        self.pivot = pivot
        self.path = path
        self.logicalIndex = logicalIndex
        
    def __repr__(self):
        return "[InflInfo %r %r %r]" % (self.logicalIndex,self.path,self.pivot)
         

class LayerData(object):
    '''
    Intermediate data object between ngSkinTools core and importers/exporters,
    representing all layers info in one skin cluster. 
    '''
    
    def __init__(self):
        #: layers list
        self.layers = []
        self.mll = MllInterface()

        self.meshInfo = MeshInfo()
        
        self.influences = []
        
        # a map [sourceInfluenceName] -> [destinationInfluenceName]
        self.mirrorInfluenceAssociationOverrides = None
        
        self.skinClusterFn = None
        
    def addMirrorInfluenceAssociationOverride(self,sourceInfluence,destinationInfluence=None,selfReference=False,bidirectional=True):
        '''
        Adds mirror influence association override, similar to UI of "Add influences association".
        Self reference creates a source<->source association, bidirectional means that destination->source 
        link is added as well
        '''
        
        if self.mirrorInfluenceAssociationOverrides is None:
            self.mirrorInfluenceAssociationOverrides = {}
        
        if selfReference:
            self.mirrorInfluenceAssociationOverrides[sourceInfluence] = sourceInfluence
            return
        
        if destinationInfluence is None:
            raise MessageException("destination influence must be specified")
        
        self.mirrorInfluenceAssociationOverrides[sourceInfluence] = destinationInfluence
        
        if bidirectional:
            self.mirrorInfluenceAssociationOverrides[destinationInfluence] = sourceInfluence 
        

    def addLayer(self, layer):
        '''
        register new layer into this data object
        '''
        assert isinstance(layer, Layer)
        self.layers.append(layer)
       
    @staticmethod 
    def getFullNodePath(nodeName):
        result = cmds.ls(nodeName,l=True)
        if result is None or len(result)==0:
            raise MessageException("node %s was not found" % nodeName)
        
        return result[0]
    
    def loadInfluenceInfo(self):    
        self.influences = self.mll.listInfluenceInfo()
    
    def loadFrom(self, mesh):
        '''
        loads data from actual skin cluster and prepares it for exporting.
        supply skin cluster or skinned mesh as an argument
        '''
        
        self.mll.setCurrentMesh(mesh)
        
        meshExporter = MeshDataExporter()
        self.meshInfo = MeshInfo()
        if mesh!=MllInterface.TARGET_REFERENCE_MESH:
            mesh,skinCluster = self.mll.getTargetInfo()
            meshExporter.setTransformMatrixFromNode(mesh)
            meshExporter.useSkinClusterInputMesh(skinCluster)
            self.meshInfo.verts,self.meshInfo.triangles = meshExporter.export()
        else:
            self.meshInfo.verts = self.mll.getReferenceMeshVerts()
            self.meshInfo.triangles = self.mll.getReferenceMeshTriangles()

        self.loadInfluenceInfo()
        
        for layerID, layerName in self.mll.listLayers():
            self.mirrorInfluenceAssociationOverrides = self.mll.getManualMirrorInfluences()
            if len(self.mirrorInfluenceAssociationOverrides)==0:
                self.mirrorInfluenceAssociationOverrides = None
            
            layer = Layer()
            layer.name = layerName
            self.addLayer(layer)
            
            
            layer.opacity = self.mll.getLayerOpacity(layerID)
            layer.enabled = self.mll.isLayerEnabled(layerID)
            
            layer.mask = self.mll.getLayerMask(layerID)
            
            for inflName, logicalIndex in self.mll.listLayerInfluences(layerID,activeInfluences=True):
                if inflName=='':
                    inflName = None
                influence = Influence()
                if inflName is not None:
                    influence.influenceName = self.getFullNodePath(inflName)
                influence.logicalIndex = logicalIndex
                layer.addInfluence(influence)
                
                influence.weights = self.mll.getInfluenceWeights(layerID, logicalIndex)
                
    def __validate(self):
        
        numVerts = self.mll.getVertCount()
        
        def validateVertCount(count,message):
                if count!=numVerts:
                    raise Exception(message) 
        
        for layer in self.layers:
            maskLen = len(layer.mask)
            if maskLen != 0:
                validateVertCount(maskLen, "Invalid vertex count for mask in layer '%s': expected size is %d" % (layer.name, numVerts))
            
            for influence in layer.influences:
                validateVertCount(len(influence.weights), "Invalid weights count for influence '%s' in layer '%s': expected size is %d" % (influence.influenceName, layer.name, numVerts))
                
                if self.skinClusterFn:
                    influence.logicalIndex = self.skinClusterFn.getLogicalInfluenceIndex(influence.influenceName)
                
        
    @Utils.undoable        
    def saveTo(self, mesh):
        '''
        saves data to actual skin cluster
        '''
        
        # set target to whatever was provided
        self.mll.setCurrentMesh(mesh)

        if mesh==MllInterface.TARGET_REFERENCE_MESH:
            self.mll.setWeightsReferenceMesh(self.meshInfo.verts, self.meshInfo.triangles)
            
        
        if not self.mll.getLayersAvailable():
            self.mll.initLayers()
            
        if not self.mll.getLayersAvailable():
            raise Exception("could not initialize layers")
        

        # is skin cluster available?
        if mesh!=MllInterface.TARGET_REFERENCE_MESH:
            mesh, self.skinCluster = self.mll.getTargetInfo()
            self.skinClusterFn = SkinClusterFn()
            self.skinClusterFn.setSkinCluster(self.skinCluster)
        
        self.__validate()
        
        # set target to actual mesh
        self.mll.setCurrentMesh(mesh)
            
        with self.mll.batchUpdateContext():
            if self.mirrorInfluenceAssociationOverrides:
                self.mll.setManualMirrorInfluences(self.mirrorInfluenceAssociationOverrides)
            
            for layer in reversed(self.layers):
                layerId = self.mll.createLayer(name=layer.name, forceEmpty=True)
                self.mll.setCurrentLayer(layerId)
                if layerId is None:
                    raise Exception("import failed: could not create layer '%s'" % (layer.name))
                
                self.mll.setLayerOpacity(layerId, layer.opacity)
                self.mll.setLayerEnabled(layerId, layer.enabled)
                self.mll.setLayerMask(layerId, layer.mask)
                
                for influence in layer.influences:
                    self.mll.setInfluenceWeights(layerId, influence.logicalIndex, influence.weights)
        
                
    def __repr__(self):
        return "[LayerDataModel(%r)]" % self.layers
    
    def getAllInfluences(self):
        '''
        a convenience method to retrieve a list of names of all influences used in this layer data object
        '''
        
        result = set()
        
        for layer in self.layers:
            for influence in layer.influences:
                result.add(influence.influenceName)
                
        return tuple(result)
    
    
class XmlExporter:
    def __init__(self):
        from xml.dom import minidom
        
        self.document = minidom.Document()
        self.baseElement = None
        self.layerElement = None
        self.influenceElement = None
        
    def processLayerInfluence(self, influence):
        self.influenceElement = self.document.createElement("influence")
        self.layerElement.appendChild(self.influenceElement)
        
        self.influenceElement.setAttribute("index", str(influence.logicalIndex))
        if influence.influenceName is not None:
            self.influenceElement.setAttribute("name", str(influence.influenceName))
        self.floatArrayToAttribute(self.influenceElement, "weights", influence.weights)
        
    def processLayer(self, layer):
        self.layerElement = self.document.createElement("layer")
        self.baseElement.appendChild(self.layerElement)
        
        self.layerElement.setAttribute("name", str(layer.name))
        self.layerElement.setAttribute("enabled", "yes" if layer.enabled else "no")
        self.layerElement.setAttribute("opacity", self.formatFloat(layer.opacity))
        self.floatArrayToAttribute(self.layerElement, "mask", layer.mask)
        
        for influence in layer.influences:
            self.processLayerInfluence(influence)
            
    def processInfluences(self, influences):
        root = self.document.createElement("influences")
        self.baseElement.appendChild(root)
        for i in influences:
            influenceElement = self.document.createElement("influence")
            root.appendChild(influenceElement)
            influenceElement.setAttribute("index", str(i.logicalIndex))
            influenceElement.setAttribute("path", str(i.path))
            self.floatArrayToAttribute(influenceElement, "pivot", i.pivot)
    
    def process(self, layerDataModel):
        '''
        transforms LayerDataModel to UTF-8 xml
        '''
        self.baseElement = self.document.createElement("ngstLayerData")
        self.baseElement.setAttribute("version", "1.0")
        self.document.appendChild(self.baseElement)
        
        if layerDataModel.influences!=None and len(layerDataModel.influences)>0:
            self.processInfluences(layerDataModel.influences)
        
        if layerDataModel.meshInfo is not None and len(layerDataModel.meshInfo.verts)>0:
            meshInfoElement = self.document.createElement("meshInfo")
            self.baseElement.appendChild(meshInfoElement)
            self.floatArrayToAttribute(meshInfoElement, "vertices", layerDataModel.meshInfo.verts)
            self.arrayToAttribute(meshInfoElement, "triangles", layerDataModel.meshInfo.triangles,str)

        if layerDataModel.mirrorInfluenceAssociationOverrides:
            for source,destination in layerDataModel.mirrorInfluenceAssociationOverrides.items():
                assoc = self.document.createElement("mirrorInfluenceAssociation")
                self.baseElement.appendChild(assoc)
                assoc.setAttribute("source",source)
                assoc.setAttribute("destination",destination)
        
        for layer in layerDataModel.layers:
            self.processLayer(layer)
            
        return self.document.toprettyxml(encoding="UTF-8")
            
    def floatArrayToAttribute(self, node, attrName, values):
        self.arrayToAttribute(node, attrName, values, self.formatFloat)

    def arrayToAttribute(self, node, attrName, values, itemCallable):
        node.setAttribute(attrName, " ".join(map(itemCallable, values)))
            
    def formatFloat(self, value):
        # up to 15 digits after comma, no trailing zeros if present
        return "%.15g" % value
    
    
class XmlImporter:
    
    def iterateChildren(self, node, name):
        for i in node.childNodes:
            if i.nodeName == name:
                yield i
                
    def attributeToList(self, node, attribute, itemCallable):
        value = node.getAttribute(attribute).strip()
        if len(value) == 0:
            return []
        
        return map(itemCallable, value.split(" "))

    def attributeToFloatList(self, node, attribute):
        return self.attributeToList(node, attribute, float)
    
    def process(self, xml):
        'transforms XML to LayerDataModel'
        self.model = LayerData()
        
        from xml.dom import minidom
        self.dom = minidom.parseString(xml)
        
       
        for layersNode in self.iterateChildren(self.dom, "ngstLayerData"):
            for meshData in self.iterateChildren(layersNode, "meshInfo"):
                self.model.meshInfo.verts = self.attributeToFloatList(meshData, "vertices")
                self.model.meshInfo.triangles = self.attributeToList(meshData, "triangles",int)

            for node in self.iterateChildren(layersNode, "mirrorInfluenceAssociation"):
                self.model.addMirrorInfluenceAssociationOverride(node.getAttribute("source"), node.getAttribute("destination"), selfReference=False, bidirectional=False)
            
            for layerNode in self.iterateChildren(layersNode, "layer"):
                layer = Layer()
                self.model.addLayer(layer)
                layer.name = layerNode.getAttribute("name")
                layer.enabled = layerNode.getAttribute("enabled") in ["yes", "true", "1"]
                layer.opacity = float(layerNode.getAttribute("opacity"))
                layer.mask = self.attributeToFloatList(layerNode, "mask")
                
                for influenceNode in self.iterateChildren(layerNode, "influence"):
                    influence = Influence()
                    influence.influenceName = influenceNode.getAttribute("name")
                    influence.logicalIndex = int(influenceNode.getAttribute("index"))
                    influence.weights = self.attributeToFloatList(influenceNode, "weights")
                    layer.addInfluence(influence)
                
        
        return self.model
        
class JsonExporter:
    def __influenceToDictionary(self, influence):
        result = {}
        result['name'] = influence.influenceName
        result['index'] = influence.logicalIndex
        result['weights'] = influence.weights
        return result
    
    def __layerToDictionary(self, layer):
        result = {}
        result['name'] = layer.name
        result['opacity'] = layer.opacity
        result['enabled'] = layer.enabled
        result['mask'] = layer.mask
        result['influences'] = []
        for infl in layer.influences:
            result['influences'].append(self.__influenceToDictionary(infl))
            
        return result

    def __meshInfoToDictionary(self,meshInfo):
        result = {}
        result['verts'] = meshInfo.verts
        result['triangles'] = meshInfo.triangles
        return result
    
    def __modelToDictionary(self, model):
        result = {}
        result['meshInfo'] = self.__meshInfoToDictionary(model.meshInfo)
        if model.mirrorInfluenceAssociationOverrides:
            result['manualInfluenceOverrides'] = dict(model.mirrorInfluenceAssociationOverrides.items())
        result['layers'] = []
        for layer in model.layers:
            result['layers'].append(self.__layerToDictionary(layer))
            
        if model.influences:
            result['influences'] = self.__serializeInfluences(model.influences)
            
        return result
    
    def __serializeInfluences(self, influences):
        result = {}
        for i in influences:
            result[i.logicalIndex] = {'path':i.path,'index':i.logicalIndex,'pivot': i.pivot}
        return result
    
    def process(self, layerDataModel):
        '''
        transforms LayerDataModel to JSON
        '''
        modelDictionary = self.__modelToDictionary(layerDataModel);
        import json    
        import re
        exportOutput = json.dumps(modelDictionary,indent=2)
        # remove line break if next line is "whitespace + closing bracket or positive/negative number"
        exportOutput = re.sub(r'\n\s+(\]|\-?\d)',r"\1",exportOutput)
        return exportOutput    
    
    
class JsonImporter:
    
    def process(self, jsonDocument):
        '''
        transform JSON document (provided as valid json string) into layerDataModel
        '''
        import json
        self.document = json.loads(jsonDocument)
        
        model = LayerData()
        
        meshInfo = self.document.get('meshInfo')
        if meshInfo:
            model.meshInfo.verts = meshInfo['verts']
            model.meshInfo.triangles = meshInfo['triangles']
        
        model.mirrorInfluenceAssociationOverrides = self.document.get("manualInfluenceOverrides")
        
        influences = self.document.get('influences')
        if influences:
            model.influences = []
            for i in influences.values():
                model.influences.append(InfluenceInfo(pivot=i['pivot'], path=i['path'], logicalIndex=i['index'])) 
        
        for layerData in self.document["layers"]:
            layer = Layer()
            model.addLayer(layer)        
            layer.enabled = layerData['enabled']
            layer.mask = layerData.get('mask')
            layer.name = layerData['name']
            layer.opacity = layerData['opacity']
            layer.influences = []

            for influenceData in layerData['influences']:
                influence = Influence()
                layer.addInfluence(influence)
                influence.weights = influenceData['weights']
                influence.logicalIndex = influenceData['index']
                influence.influenceName = influenceData['name']

        return model
    
class Format:
    def __init__(self):
        self.title = ""
        self.exporterClass = None
        self.importerClass = None
        
        # recommended file extensions for UI, e.g. file dialog
        self.recommendedExtensions = ()    
        
    def export(self,mesh):
        '''
        returns file contents that was produced with 
        '''
        model = LayerData()
        model.loadFrom(mesh)
        return self.exporterClass().process(model)
    
    def import_(self,fileContents,mesh):
        '''
        parses fileContents with importerClass and loads data onto given mesh
        '''
        model = self.importerClass().process(fileContents)
        model.saveTo(mesh)
    
class Formats:
    
    
    @staticmethod
    def getXmlFormat():
        f = Format()
        f.title = "XML"
        f.exporterClass = XmlExporter
        f.importerClass = XmlImporter
        f.recommendedExtensions = ("xml",)
        return f
    
    @staticmethod
    def getJsonFormat():
        f = Format()
        f.title = "JSON"
        f.exporterClass = JsonExporter
        f.importerClass = JsonImporter
        f.recommendedExtensions = ("json", "txt")
        return f
    
    @staticmethod
    def getFormats():
        '''
        returns iterator to available exporters
        '''
        #yield Formats.getXmlFormat()
        yield Formats.getJsonFormat()
        
        
    
        
        

