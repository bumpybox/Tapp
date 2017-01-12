'''

polish and add to tapp

'''
import os
import tempfile

import maya.cmds as cmds
import maya.mel as mel

def sourceDora():
    #sourcing dora util
    path=os.path.dirname(__file__)
    
    melPath=path+'/DoraSkinWeightImpExp.mel'
    melPath=melPath.replace('\\','/')
    mel.eval('source "%s"' % melPath)

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

def propagateWeightChangesToReference( meshes ):
    '''
    Given a list of meshes to act on, this function will store the skin weights, remove any
    edits from the skin clusters that affect them, open the scene file the meshes come from
    and apply the weights to the geometry in that scene.

    This makes it possible to fix skinning problems while animating with minimal workflow
    changes
    '''
    curFile = cmds.file( q=True, sn=True )
    
    #failsafe for untitled file
    if curFile=='':
        
        cmds.warning('Current file is not saved. Please save file and try again!')
        
        return
    
    #getting skin cluster nodes from meshes
    skinClusters=[]
    for mesh in meshes:
        sc=mel.eval('findRelatedSkinCluster("%s");' % mesh)
        
        skinClusters.append(sc)
    
    referencedSkins=getRefFilepathDictForNodes(skinClusters)
    
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
        
        #now we want to store out the weighting from the referenced meshes
        weightFiles = []
        for mesh, meshNamespace in meshesToUpdateWeightsOn_withNS:
            
            nodesToCleanRefEditsFrom.append(mesh)
            
            m=cmds.listConnections(mesh+'.outputGeometry')[0]
            mStrip=stripNamespaceFromNamePath(m,meshNamespace)
            
            #export dora skin
            tempDir=tempfile.gettempdir()
            filepath=tempDir.replace('\\','/')+'/'+mStrip.replace(':','_-_')+'.dsw'
            weightFiles.append(filepath)
            
            sourceDora()
            
            cmds.select(m)
            mel.eval('DoraSkinWeightExport_mod("%s")' % filepath)
            
            #modify dora skin
            f=open(filepath,'r')
            data=f.readlines()
            
            jntData=''
            for jnt in data[1].split(','):
                
                jnt=jnt.replace('\n','')
                
                jnt=stripNamespaceFromNamePath(jnt,meshNamespace)
                
                jntData+=jnt+','
            
            jntData=jntData[0:-1]+'\n'
            
            data[1]=jntData
            
            newData=''
            
            for line in data:
                
                newData+=line
            
            f.close()
            
            #writing new dora skin
            f=open(filepath,'w')
            f.write(newData)
            f.close()
            
            #also lets remove any ref edits from the mesh and all of its shape nodes - this isn't strictly nessecary, but I can't think of a reason to make edits to these nodes outside of their native file
            nodesToCleanRefEditsFrom.append( m )
            nodesToCleanRefEditsFrom += cmds.listRelatives( m, s=True, pa=True )
        
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
        
        for f in weightFiles:
            
            mesh=f.split('/')[-1].replace('_-_',':').split('.')[0]
            
            cmds.select(mesh)
            
            mel.eval('DoraSkinWeightImport_mod("%s",0,0,1,0.001);' % f)
            
            os.remove(f)
        
        #save the referenced scene now that we've applied the weights to it
        cmds.file( save=True, f=True )
    
    #reload the original file
    cmds.file( curFile, o=True, f=True )
    
    #informing user of edited files and printing
    cmd='\nFiles updated:\n'
    
    for f in referencedSkins:
        
        cmd+=f+'\n'
    
    cmds.confirmDialog(title='Skin Propagation complete!',message=cmd)
    
    print cmd

sel=cmds.ls(selection=True)

propagateWeightChangesToReference(sel)