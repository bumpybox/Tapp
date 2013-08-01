from maya import OpenMaya , cmds 

class MG_alignBones (object):
    '''
    @author             Marco Giordano
        
    @date               04.09.2013
    
    @version            1.0.0
        
    @brief              This class lets orient bones
    
    Usage : 
    
    \code{.py}
      
    \endcode 
    '''
    def __init__(self , bones = []):
        '''
        This is the constructor
        @param bones:this are the bones that are going to be aligned 
        '''
        #args
        
        self.bones = bones
        
        #vars 
        ##static value for converting from rad to deg
        self.toDeg = 57.295779513082320876798154814105;
        ##This var holds the parent of the root bones we use in the 3 chain
        self.rootParent = None
        ##This var hold the created plane if we use the geometry plane mode
        self.mesh = None

    def withVirtualPlane (self , hierarchy = 0 , reverseNormal = 0  ):
        '''
        This procedure use a virtual plane generate from points to orient the
        bones
        @param hierarchy : bool , orient all the child list not only the first three bones 
        @param reverseNormal:  bool ,whether to reverse or not the calculated normal
        '''
        
        #Check if we got at least 3 bones
        if len(self.bones) < 3 :
            OpenMaya.MGlobal.displayError("The procedure needs  3 bones as input , {number} given".format(number = len(self.bones)))
            return
        
        
        #get positions
        posArray = []
        for i in range (3):
            pos = cmds.xform(self.bones[i], ws =1 , q = 1 , t =1)
            posArray.append(pos)
            
        self._orientFromPosArray(posArray , hierarchy , reverseNormal)
        
    def withGeometryPlaneInit(self):
        '''
        This procedure creates the geometry plane , the operation is split in two so if we want
        we can tweak manually the generated plane
        '''
        #Check if we got at least 3 bones
        if len(self.bones) < 3 :
            OpenMaya.MGlobal.displayError("The procedure needs  3 bones as input , {number} given".format(number = len(self.bones)))
            return
        
        #get positions
        posArray = []
        for i in range (3):
            pos = cmds.xform(self.bones[i], ws =1 , q = 1 , t =1)
            posArray.append(pos)
        
        self.mesh = cmds.polyCreateFacet (ch = 0  ,tx= 1. , s =1 ,p = posArray)[0]
       
    def withGeometryPlaneDoit(self ,hierarchy = 0  , reverseNormal = 0 ):
        '''
        This procedure gets run after withGeometryPlaneInit()
        @param hierarchy : bool , orient all the child list not only the first three bones 
        @param reverseNormal:  bool ,whether to reverse or not the calculated normal
        '''
        
        if not self.mesh :
            OpenMaya.MGlobal.displayError("Initialized mesh not found in class")
            return

        #get the points from the geometry
        posArray = []
        vtx = cmds.ls(self.mesh + ".vtx[*]" , fl = 1)
        for i in range (len(vtx)):
            pos = cmds.xform(vtx[i], ws =1 , q = 1 , t =1)
            posArray.append(pos)

        self._orientFromPosArray(posArray , hierarchy , reverseNormal)

        cmds.delete(self.mesh)
        self.mesh = None
  
    def _orientFromPosArray (self , posArray ,hierarchy , reverseNormal):
        '''
        This procedure orients the bones once the posArray has been filled
        @param posArray :list , the ordered list of the position of the bones needed for orienting 
        @param hierarchy : bool , orient all the child list not only the first three bones 
        @param reverseNormal:  bool ,whether to reverse or not the calculated normal
        '''
        #Make vectors 
        vecA = OpenMaya.MVector(posArray[0][0] ,posArray[0][1],posArray[0][2])
        vecB = OpenMaya.MVector(posArray[1][0] ,posArray[1][1],posArray[1][2])
        vecC = OpenMaya.MVector(posArray[2][0] ,posArray[2][1],posArray[2][2])
        
        #generate the virtual plane and get the normal
        vecBA = vecB - vecA
        vecCA = vecC - vecA
        
        #normalize the vecs
        vecBA.normalize()
        vecCA.normalize()
        
        #check that vectors are not parallel
        
        if (vecBA * vecCA) == 1 :
            OpenMaya.MGlobal.displayError("Bones lie on a straight lines , this method wont work")
            return
            
        normal =    vecCA ^ vecBA
        normal.normalize()
        if reverseNormal == 1 :
            normal*= -1 

        print "-----> normal computed : " , normal.x , normal.y , normal.z
                
        #unparent the bones
        self._unparentBones()
        
        #compute a rotation matrix and set the value
        
        length = len(self.bones )
        if hierarchy == 0 :
            length = 3 
        
        for i in range(length):
            
            if i != (length -1 ):
                #get tangent vector 
                start = cmds.xform(self.bones[i] , q = 1 ,ws = 1 , t = 1 )
                end = cmds.xform(self.bones[i+1] , q = 1 , ws =1 , t =1 )
            else :
                start = cmds.xform(self.bones[i-1] , q = 1 ,ws = 1 , t = 1 )
                end = cmds.xform(self.bones[i] , q = 1 ,ws = 1 , t = 1 )
            
            
            #generate tangent vector
            startVec = OpenMaya.MVector(start[0] , start[1] , start[2])
            endVec = OpenMaya.MVector(end[0] , end[1] , end[2])
            tangent = endVec - startVec
            tangent.normalize()
            #find the third missing axis
            cross = normal ^ tangent
            cross.normalize()
            cross2 = cross ^ tangent;
            cross2.normalize()
            
            #generate a matrix with the data
            
            matrixList = [tangent.x , tangent.y , tangent.z , 0 ,
                          cross.x , cross.y , cross.z, 0,
                          cross2.x , cross2.y , cross2.z, 0,
                          0,0,0,1 ]
        
            rotMatrix = OpenMaya.MMatrix()
            OpenMaya.MScriptUtil.createMatrixFromList( matrixList, rotMatrix)
            
            
            matrixFn = OpenMaya.MTransformationMatrix(rotMatrix)
            rot = matrixFn.eulerRotation()
            
            cmds.setAttr(self.bones[i] +".jointOrient" ,
                         (rot.x * self.toDeg),
                         (rot.y * self.toDeg),
                         (rot.z * self.toDeg)  )
                
                
                
        #reparent the bones
        self._parentBones()
        
        #select the root
        cmds.select(cl = 1)
        cmds.select(self.bones[0])
        
        print "-----------> bones oriented correctly"
     
    def _unparentBones(self):
        '''
        This procedure un-parent the bones getting them ready to be oriented
        '''        
        self.rootParent = cmds.listRelatives(self.bones[0] , parent = 1)
        
        reversedBones = list(self.bones)
        reversedBones.reverse()
        #we remove the root from list no need to un-parent it and this way we 
        #still respect the hierarchy 
        if not self.rootParent :
            reversedBones.pop(-1)

        for r in reversedBones :
            cmds.parent(r , world = 1 )
            
    def _parentBones(self) :
        '''
        This procedure re-parent the bones after being 
        reoriented
        '''
        reversedBones = list(self.bones)
        reversedBones.reverse()

        for i in range(len (reversedBones )):
            if i != ((len (reversedBones )-1)):
                cmds.parent(reversedBones[i] , reversedBones[i+1] )

        if self.rootParent : 
            cmds.parent(self.bones[0] , self.rootParent)
        
        
        
        
        