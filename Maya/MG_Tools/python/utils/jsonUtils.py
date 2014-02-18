import json

from maya import cmds


class jsonUtils ( object ):
    '''

    @author             Marco Giordano
        
    @date               03.16.2012
    
    @version            1.0.0
      
    
    @brief          This class saves json files 
    
   
        
    Usage : 
    \code{.py}
                

    \endcode
    
    '''

   
    def __init__(self ):
        
        '''
        This is the constructor
        '''
       

        #modules 
        
    

    def save (self , stuffToSave = None , path = None):
        
        '''
        This procedure saves given data in a json file
        @param[in] stuffToSave : this is the data you want to save , be sure it s json serializable
        @param path : where you want to save the file 

        '''
        if not path :
                path = cmds.fileDialog2(fileMode=0, dialogStyle=1)[0]
            
        toBeSaved = json.dumps(stuffToSave , sort_keys=True ,ensure_ascii=True ,indent=2)
        f = open(path, 'w')
        f.write(toBeSaved)
        f.close()
        
        print "------> file correctly saved here : " , path
        
        
       

    def load (self , path = None):
        
        '''
        This procedure loads and returns the content of a json file
        @param path:  what file you want to load          
        @return : the content of the file
        '''    
        if not path :
                path = cmds.fileDialog2(fileMode=1, dialogStyle=1)[0]
        f = open(path)
        dataFile  = json.load(f)
        
        return dataFile
        
        
        