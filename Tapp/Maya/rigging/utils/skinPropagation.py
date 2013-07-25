import os

import maya.cmds as cmds
import maya.mel as mel

'''
#sourcing dora util
path=os.path.dirname(__file__)

melPath=path+'/DoraSkinWeightImpExp.mel'
melPath=melPath.replace('\\','/')
mel.eval('source "%s"' % melPath)
'''

def stripNamespaceFromNamePath( name, namespace ):
    '''
    strips out the given namespace from a given name path.

    example:
    stripNamespaceFromNamePath( 'moar:ns:wow:some|moar:ns:wow:name|moar:ns:wow:path', 'ns' )

    returns:
    'wow:some|wow:name|wow:path'
    '''
    if namespace.endswith( ':' ):
        namespace = namespace[ :-1 ]

    cleanPathToks = []
    for pathTok in name.split( '|' ):
        namespaceToks = pathTok.split( ':' )
        if namespace in namespaceToks:
            idx = namespaceToks.index( namespace )
            namespaceToks = namespaceToks[ idx+1: ]

        cleanPathToks.append( ':'.join( namespaceToks ) )

    return '|'.join( cleanPathToks )

def getRefFilepathDictForNodes( nodes ):
    '''
    returns a dictionary keyed by the referenced filename.  Key values are dictionaries which are
    keyed by reference node (any file can be referenced multiple times) the value of which are the
    given nodes that are referenced.

    example:
    we have a scene with three references:
    refA comes from c:/someFile.ma
    refB comes from c:/someFile.ma
    refC comes from c:/anotherFile.ma

    we have 3 nodes: nodeA, nodeB and nodeC.

    nodeA comes from refA
    nodeB comes from refB
    nodeA comes from refC

    in this example running getRefFilepathDictForNodes( ('nodeA', 'nodeB', 'nodeC') ) would return:

    { 'c:/someFile.ma': { 'refA': [ 'nodeA' ], 'refB': [ 'nodeB' ],
      'c:/anotherFile.ma': { 'refC': [ 'nodeC' ] }
    '''
    refFileDict = {}

    #find the referenced files for the given meshes
    for node in nodes:
        isReferenced = cmds.referenceQuery( node, inr=True )
        if isReferenced:
            refNode = cmds.referenceQuery( node, referenceNode=True )
            refFile = cmds.referenceQuery( node, filename=True, withoutCopyNumber=True )

            if refFile in refFileDict:
                refNodeDict = refFileDict[ refFile ]
            else:
                refNodeDict = refFileDict[ refFile ] = {}

            refNodeDict.setdefault( refNode, [] )
            refNodeDict[ refNode ].append( node )

    return refFileDict

def doraExportSkin():
    
    pass

def propagateWeightChangesToModel( meshes ):
    '''
    Given a list of meshes to act on, this function will store the skin weights, remove any
    edits from the skin clusters that affect them, open the scene file the meshes come from
    and apply the weights to the geometry in that scene.

    This makes it possible to fix skinning problems while animating with minimal workflow
    changes
    '''
    #curFile = Path( file( q=True, sn=True ) )
    curFile = cmds.file( q=True, sn=True )
    #referencedMeshes = getRefFilepathDictForNodes( meshes )
    
    #getting skin cluster nodes from meshes
    skinClusters=[]
    for mesh in meshes:
        sc=mel.eval('findRelatedSkinCluster("%s");' % mesh)
        
        skinClusters.append(sc)
    
    referencedSkins=getRefFilepathDictForNodes(skinClusters)
    
    '''
    if not curFile.name():
        printWarningStr( "The current scene isn't saved - please save the current scene first before proceeding!" )
        return
    '''

    for refFilepath, refNodeMeshDict in referencedSkins.iteritems():
        
        referencesToUnload = []

        #make sure we don't visit any of the meshes more than once
        meshesToUpdateWeightsOn = []
        meshesToUpdateWeightsOn_withNS = []
        for refNode, refMeshes in refNodeMeshDict.iteritems():

            #get the maya filepath for the reference (with the "copy number")
            mayaFilepathForRef = cmds.referenceQuery( refNode, f=True )

            #get the namespace for this reference
            refNodeNamespace = cmds.file( mayaFilepathForRef, q=True, namespace=True )

            #check to see if there are any meshes in this reference that we need to store weights for
            for mesh_withNS in refMeshes:
                mesh = stripNamespaceFromNamePath( mesh_withNS, refNodeNamespace )
                if mesh in meshesToUpdateWeightsOn:
                    continue

                meshesToUpdateWeightsOn.append( mesh )
                meshesToUpdateWeightsOn_withNS.append( (mesh_withNS, refNodeNamespace) )

            #append the file to the list of reference files that we need to unload
            referencesToUnload.append( mayaFilepathForRef )

        #get a list of skin cluster nodes - its actually the skin cluster nodes we want to remove edits from...
        nodesToCleanRefEditsFrom = []
        for m, ns in meshesToUpdateWeightsOn_withNS:
            nodesToCleanRefEditsFrom.append( mel.eval('findRelatedSkinCluster("%s");' % m) )
        
        #now we want to store out the weighting from the referenced meshes
        weights = []
        for mesh, meshNamespace in meshesToUpdateWeightsOn_withNS:
            #insert dora export skin weights here---
            #weights.append( storeWeightsById( mesh, meshNamespace ) )
            
            print mesh
            print meshNamespace

            #also lets remove any ref edits from the mesh and all of its shape nodes - this isn't strictly nessecary, but I can't think of a reason to make edits to these nodes outside of their native file
            nodesToCleanRefEditsFrom.append( mesh )
            nodesToCleanRefEditsFrom += cmds.listRelatives( mesh, s=True, pa=True ) or []
        
        '''
        #remove the skinweights reference edits from the meshes in the current scene
        for f in referencesToUnload:
            cmds.file( f, unloadReference=True )

        #remove ref edits from the shape node as well - this isn't strictly nessecary but there probably shouldn't be changes to the shape node anyway
        for node in nodesToCleanRefEditsFrom:
            cmds.referenceEdit( node, removeEdits=True, successfulEdits=True, failedEdits=True )

        #re-load references
        for f in referencesToUnload:
            cmds.file( f, loadReference=True )
        
        #save this scene now that we've removed ref edits
        cmds.file( save=True, f=True )
        
        #load up the referenced file and apply the weighting to the meshes in that scene
        cmds.file( refFilepath, open=True, f=True )
        
        for mesh, weightData in zip( meshesToUpdateWeightsOn, weights ):

            #if there is no weight data to store - keep loopin...
            if not weightData:
                continue

            skinCluster = mel.eval('findRelatedSkinCluster("%s");' % mesh)
            if not skinCluster:
                cmds.warning( "Couldn't find a skin cluster driving %s - skipping this mesh" % mesh )
                continue
            
            #insert dora import skin weights here---
            skinWeights.setSkinWeights( skinCluster, weightData )

        #save the referenced scene now that we've applied the weights to it
        file( save=True, f=True )

    #reload the original file
    file( curFile, o=True, f=True )
    '''

propagateWeightChangesToModel(['character:skin:geo:pSphere1'])