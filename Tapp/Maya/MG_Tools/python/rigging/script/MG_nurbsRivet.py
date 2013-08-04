from maya import cmds , OpenMaya

def MG_nurbsRivet (baseName = "nurbsRivet", surface = None , target = None, mo = 1):
    '''
    This procedure is used to hook up an MG_nurbsRivet
    @param baseName : this is the name used for the node
    @param surface : string ,the surface we want to rivet on 
    @param mo : bool , if to maintain the offset or not
    @param target : stirng ,the name of the object we want to rivet
    ''' 
    
    #undo start
    cmds.undoInfo(openChunk=True)
    
    #Checkign the given data
    
    val = cmds.pluginInfo ( "MG_rigToolsPro" , q=1 ,loaded = 1 )
    val2 = cmds.pluginInfo ( "MG_toolsLite" , q=1 ,loaded = 1 )
    
    if val == 0 and val2 == 0 :
        OpenMaya.MGlobal.displayError("You need the MG_toolsPro or MG_toolsLite plugin , none was found")
        return
    
    if val == 1 :
        cmds.loadPlugin("MG_rigToolsPro")
    elif val2 == 1 :
        cmds.loadPlugin("MG_toolsLite") 
        
    shape = cmds.listRelatives(surface , shapes =  1)[0]
    if cmds.nodeType(shape) != "nurbsSurface" :
        OpenMaya.MGlobal.displayError("you need to provide a nurbsSurface transform got {wrong} instead".format(wrong = cmds.nodeType(shape)))
        return 
    
    if not target :
        OpenMaya.MGlobal.displayError("You need to provide a target")
        return 
    
    #Get the pre matrix , used to calculate offset matrix
    preMatrix = cmds.getAttr(target +'.wm')
    
    rivet = cmds.createNode("MG_nurbsRivet" , n = baseName)
    
    sourcePoint     = cmds.xform(target , ws =1 , q =1 , t = 1)
    
    #set and connect the various attribute
    cmds.setAttr(rivet + ".inputPoint" , sourcePoint [ 0 ] , sourcePoint [ 1 ] , sourcePoint [ 2 ] , type = "double3" )
    cmds.connectAttr(shape+'.worldSpace',rivet + ".inputNurbsSurface" )
    
    
    #Fake get attr to force the node to compute
    cmds.getAttr(rivet + '.outputTranslate')
    cmds.getAttr(rivet + '.outputRotate')
    
    
    cmds.connectAttr(rivet + '.outputTranslate' , target + '.t' )
    cmds.connectAttr(rivet + '.outputRotate' , target + '.r' )
    if (mo == 1) : 
        
        #Compute the offset matrix for the target
        postMatrix = cmds.getAttr(target +'.worldInverseMatrix' )         
        preMatrixM = OpenMaya.MMatrix();
        postMatrixM = OpenMaya.MMatrix();
        OpenMaya.MScriptUtil.createMatrixFromList( preMatrix, preMatrixM)
        OpenMaya.MScriptUtil.createMatrixFromList( postMatrix, postMatrixM)
    
        resultMatrixM = preMatrixM*postMatrixM
        resultMatrix=[]
        for i in range(4):
            for y in range(4):
                resultMatrix.append(resultMatrixM(i,y))
    
    
    
        cmds.setAttr(rivet + '.offsetMatrix' , resultMatrix , type = "matrix" ) 
    
    
    cmds.setAttr ( rivet+ '.recompute' , 0 )
    
    #undo end
    cmds.undoInfo(closeChunk=True)