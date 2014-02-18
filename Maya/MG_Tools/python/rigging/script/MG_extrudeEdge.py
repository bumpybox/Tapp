import maya.cmds as cmds
import maya.mel as mel

def MG_extrudeEdge(inputMesh,verts):
    ''' Creates a basic setup of MG_extrudeEdge on input mesh
        
        input description:
        
        inputMesh (node) = mesh
        verts (list) = list of vertex indices
        
        returns:
        
        (dict) Dicationary with all created nodes,
                categorized by function type
        
        usage:
        
        verts=[100,101,102,103,104]
        MG_extrudeEdge('pShpere1',verts)
    '''
    
    #return variable
    result={}
    
    #undo start
    cmds.undoInfo(openChunk=True)
    
    #loading plugin
    cmds.loadPlugin('MG_rigToolsPro.mll',quiet=True)
    
    #create MG_pathSpine
    extrudeNode=mel.eval('createNode MG_extrudeEdge;')
    
    #create output mesh
    outputMesh=cmds.nurbsPlane(ch=False)
    outputShape=cmds.listRelatives(outputMesh,shapes=True)[0]
    
    result['outputMesh']=outputMesh
    
    #setup extrudeNode
    inputShape=cmds.listRelatives(inputMesh,shapes=True)[0]
    
    cmds.connectAttr(inputShape+'.worldMesh[0]',extrudeNode+'.inputMesh')
    
    cmds.connectAttr(extrudeNode+'.outSurface',outputShape+'.create')
    
    #setup vertArray
    for vert in verts:
        
        count=verts.index(vert)
        
        cmds.setAttr(extrudeNode+'.vtxArray['+str(count)+']',vert)
    
    #return ---
    #undo end
    cmds.undoInfo(closeChunk=True)
    
    #return
    return result

'''
#getting verts
sel=cmds.ls(selection=True,flatten=True)

verts=[]
for vert in sel:
    
    verts.append(int(vert.split('[')[-1].split(']')[0]))

inputMesh='pSphere1'

MG_extrudeEdge(inputMesh,verts)
'''