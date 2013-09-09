from maya  import OpenMaya ,cmds ,mel


class MG_splinePath (object):
    '''
    
    @author             Marco Giordano
     
    @date               1.25.2012
    
    @version            1.0.0

        
    @brief              This class creates an MG_splinePath node
    
    Usage : 
    
    \code{.py}

  
    \endcode
    
    

    
    '''
    def __init__(self, baseName = None , side = None , numberOfSamples = 40 , numberOfOutputs = 30 
                 , inputCurve = None , targets = [] , offset = 0 , createTargets = 0 , firstUpVec = [0,1,0] ,
                 connectParentMatrix = 1 , makeLiveUpVector = 1):
        
        
        '''
        This is the constructor
        
        @param[in] baseName :  this is the name that will be used as a base for all the names
        @param[in] side :  this is the side that will be used as a base for all the names
        @param[in] numberOfSamples : int , How many sample along the curve to compute
        @param[in] numberOfOutputs :  int ,number of outputs to be generated
        @param[in] inputCurve :  string , the curve transform to work on ,
        @param[in] targets :  list of targets to attach on the curve
        @param[in] offset :  flot , offset value for the targets
        @param[in] createTargets : bool , if this flag is set to true will create locators and hook them to the curve
        @param[in] firstUpVec : float[3] , this is the first upVector to calculate the normals
        @param[in] connectParentMatrix : bool , if set to true the matrix of the curve transform will be connected
        @param[in] makeLiveUpVector : bool , if set to true the up vector will be created live with a MG_vector
        
        
        '''
        #args
        ## the baseName of the node
        self.baseName           = baseName
        ## the side of the node
        self.side               = side
        ##This is the value of How many sample along the curve to compute
        self.numberOfSamples                = numberOfSamples
        ##This is the value of How many outputs to be generated
        self.numberOfOutputs             = numberOfOutputs
        ##If ot not set the orientation as rotation or joint orient
        self.inputCurve     = inputCurve
        ##list of targets to attach on the curve
        self.targets            = targets
        ##offset value for the targets
        self.offset            = offset
        ##The first upVector to calculate the normals
        self.firstUpVec        = firstUpVec
        ##If this flag is set to true will create locators and hook them to the curve
        self.createTargets     = createTargets
        ##if set to true the matrix of the curve transform will be connected
        self.connectParentMatrix = connectParentMatrix
        ##if set to true the up vector will be created live with a MG_vector
        self.makeLiveUpVector        = makeLiveUpVector


        #Vars
        ## The basic node of the class
        self.node               = None
        ##The shape of the curve
        self.inputCurveShape    = None
        ##This is where the group class gets stored if the method groupTargets is called
        self.targetsGrp         = None
        ##The suffix of the object for generating unique names
        self.nodeSuffix         = "SPLPH"
        ##This is the base loc for the live vector if created
        self.baseVec            = None
        ##This is the end loc for the live vector if created
        self.endVec             = None
        
        
        #modules 
        




        
        
    def __prepare ( self ):
        '''
        This procedure check that all the arguments are passed and performs some checks
        '''
        
#        if self.__pluginUtil.checkAndLoad("MG_tools") == 0 :
#            return
#        
        if not self.baseName :
            OpenMaya.MGlobal.displayError ("MG_splinePath prepare :  baseName has not been set ")   
            return
        
        if not self.side :
            OpenMaya.MGlobal.displayError ("MG_splinePath prepare :  side has not been set ") 
            return
        
        if not self.inputCurve :
            OpenMaya.MGlobal.displayError ("MG_splinePath prepare :  inputCurve has not been set ") 
            return
        
        if  len(self.targets) == 0 and self.createTargets == 0 :
            OpenMaya.MGlobal.displayError ("MG_splinePath prepare :  targets has not been set , if you wish to create automatically the targest use the createTargets flag ") 
            return
        
        if (self.numberOfOutputs < len(self.targets) ) and self.createTargets == 0 :
           
            OpenMaya.MGlobal.displayWarning ("MG_splinePath prepare : number of outputs is lower then targets number") 
                
        
        self.inputCurveShape = cmds.listRelatives(self.inputCurve , shapes = 1)[0]

        return 1
         
    
    def create( self ) :
        '''
        This procedure creates and setup the the node 
        '''
        

        
        prep =self.__prepare()
        if not prep :
            return
        
        node = cmds.createNode("MG_splinePath")
        if not node :
            OpenMaya.MGlobal.displayError ("nMG_splinePath create :  error creating the MG_splinePath ") 
            return
        
        
        
        cmds.setAttr(node + '.numberOfSamples' , self.numberOfSamples)
        cmds.setAttr(node + '.numberOfOutput' , self.numberOfOutputs)
        cmds.setAttr(node + '.firstUpVec' , self.firstUpVec[0] , self.firstUpVec[1] ,
                     self.firstUpVec[2] , type ="double3" )
        cmds.setAttr(node + '.offset' , self.offset )
        
        
        cmds.connectAttr(self.inputCurveShape + '.worldSpace' , node +'.inputCurve')
        

        if len(self.targets) == 0 and self.createTargets == 1 :
            self.targets = []
            
            for i in range(self.numberOfOutputs) :
                locName = self.side + "_" + self.baseName + str(i) + "_LOC"
                loc = cmds.spaceLocator(n= locName )[0]
                self.targets.append(loc)
            
            
        
        for i in range(len(self.targets)) :
            cmds.connectAttr(node + '.outputTranslate[{i}]'.format(i=i) , 
                             self.targets[i] +'.t')
            
            cmds.connectAttr(node + '.outputRotate[{i}]'.format(i=i) , 
                             self.targets[i] +'.r')
        
        
        if self.connectParentMatrix == 1 :
            cmds.connectAttr(self.inputCurve + '.wm' , node + '.parentMatrix')
        
        self.node = node
        
        if self.makeLiveUpVector == 1 :
            self.makeLiveVector()
            
            
        

    def makeLiveVector(self):
        '''
        this fucntion creates a live vector for the MG_splinePath
        '''
           
        if not self.inputCurve :
            OpenMaya.MGlobal.displayError ("MG_splinePath prepare :  inputCurve has not been set ") 
            return    
            
            
        #Create the two locators for the vectors
        basName = self.side + "_" + self.baseName + "Base_LOC"
        tipName = self.side + "_" + self.baseName + "Tip_LOC"
        self.baseVec = cmds.spaceLocator(n = basName)[0]
        self.endVec = cmds.spaceLocator(n = tipName)[0]

        cmds.setAttr(self.endVec + '.ty' , 1)
        
        #Create the vector node
        
        self.MGvectorNode = cmds.createNode("MG_vector")
        
        #Do the neede connection
        
        cmds.connectAttr(self.baseVec + '.wm' , self.MGvectorNode + '.inputMatrix1')
        cmds.connectAttr(self.endVec + '.wm' , self.MGvectorNode+ '.inputMatrix2')
        
        cmds.connectAttr(self.MGvectorNode +'.outputVector' , self.node+'.firstUpVec')
        
        
        
        cmds.parent(self.endVec , self.baseVec)
        
        cmds.select(cl =1 )
        cmds.select(self.baseVec)
        
        
    