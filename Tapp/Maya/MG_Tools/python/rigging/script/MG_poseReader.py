from maya  import OpenMaya ,cmds 

class MG_poseReader (object):
    '''
    
    @author             Marco Giordano
     
    @date               04.05.2013
    
    @version            1.0.0

        
    @brief              This class creates an MG_poseReder node
    
    Usage : 
    
    \code{.py}
    
    import sys
    sys.path.append("C:/Users/giordi/Desktop/PROGETTI_IN_CORSO/C")
    
    from MG_Tools.python.rigging.script import MG_poseReader
    reload(MG_poseReader)
    
    ps = MG_poseReader.MG_poseReader(baseName = "reader",
                                     side = "C",
                                     poseInput = "locator1" ,
                                     aimAxis = 0 ,
                                     size  = 1 ,
                                     visible = 1,
                                     
                                     )
                                     
                                     
    ps.create()
   
    \endcode
    
    

    
    '''
    def __init__(self, baseName = None , 
                 side = None , 
                 poseInput = None ,
                 aimAxis = 0 ,
                 size  = 1 
                 ):
        

        
      

        
        '''
        This is the constructor
        
        @param[in] baseName :  this is the name that will be used as a base for all the names
        @param[in] side :  this is the side that will be used as a base for all the names
        @param[in] poseInput : string , this is the name of the object you want to read the position of
        @param[in] size : float , this is the size of the poseReader
        @param[in] aimAxis : string , the axis you want to spin on :
                        accepted axis value : 0 =  "x" 
                                              1 =  "y"
                                              2 =  "z"                
        @param[in] visible : bool , if to make the reader visible or not
     
        '''
        #args
        ## the baseName of the node
        self.baseName           = baseName
        ## the side of the node
        self.side               = side
        ##this is the name of the object you want to read the position of
        self.poseInput        = poseInput
        ##this is the size of the poseReader
        self.size        = size
        ##the axis you want to spin on
        self.aimAxis          = aimAxis


        

        #Vars
        #THis attribute holds the pose reader transform class
        self.poseReaderTransform = None
        ## The basic node of the class
        self.node               = None
        ##The suffix of the object for generating unique names
        self.nodeSuffix         = "POSR"

        





        
        
    def __prepare ( self ):
        '''
        This procedure check that all the arguments are passed and performs some checks
        '''
        
#        if self.__pluginUtil.checkAndLoad("MG_ToolsLite") == 0 and self.__pluginUtil.checkAndLoad("MG_ToolsPro") == 0  :
#            return
        
        if not self.baseName :
            OpenMaya.MGlobal.displayError ("nMG_poseReader prepare :  baseName has not been set ")   
            return
        
        if not self.side :
            OpenMaya.MGlobal.displayError ("nMG_poseReader prepare :  side has not been set ") 
            return
        
        if not self.poseInput :
            OpenMaya.MGlobal.displayError ("nMG_poseReader prepare :  pose input has not been set ") 
            return
        
        if type(self.aimAxis).__name__ != "int" :
            OpenMaya.MGlobal.displayError ("nMG_poseReader prepare :  aim axis value has to be int ") 
            return
       
        if self.aimAxis < 0 or self.aimAxis > 2 :
            OpenMaya.MGlobal.displayError ("nMG_poseReader prepare :  aim axis value error , accepted value are 0 , 1 or 2 ") 
            return
          

        return 1
         
    
    def create( self ) :
        '''
        This procedure creates and setup the the node 
        '''
        prep =self.__prepare()
        if not prep :
            return

        nodeName = self.side + "_" + self.baseName + "_READER"
        node = cmds.createNode("MG_poseReader" , n = nodeName )
        
        
        self.poseReaderTransform =  cmds.listRelatives(node , parent =1)[0]
        
        
        cmds.connectAttr(self.poseInput + ".wm" , node + '.poseMatrix')
        cmds.connectAttr(self.poseReaderTransform + ".wm" ,
                          node + '.readerMatrix')
        
        
        cmds.setAttr(node + ".aimAxis" , self.aimAxis)
        cmds.setAttr(node + ".size" , self.size)        
 
        pos = cmds.xform(self.poseInput ,q = 1, t =1, ws =1 )
        cmds.setAttr(self.poseReaderTransform + '.t' , pos[0] ,pos[1],pos[2])
            

