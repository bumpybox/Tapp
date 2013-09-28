class point():
    '''
    classdocs
    '''

    def __init__(self):
        
        #base attributes
        self.name=''
        self.children=[]
        self.parent=None
        self.translation=self.transform()
        self.rotation=self.transform()
        self.scale=self.transform()
        
        #guide attributes
        self.solverData={}
        self.controlData={}
        self.staticParent=None
        
        #builds attributes
        self.socket={}
        self.control={}
        self.plug={}
    
    class transform(list):
        '''
        Adding custom attributes to built-in list
        '''
        
        def __init__(self):
            
            self.x=None
            self.y=None
            self.z=None
        
        def set(self,*args):
            '''
            Can pass in list or int array (x,y,z)
            '''
            
            #flusing the existing list
            del self[:]
            
            #iter through args
            for arg in args:
                
                print type(arg)
                
                #if passed in a list
                if isinstance(arg,list):
                    
                    self.x=arg[0]
                    self.y=arg[1]
                    self.z=arg[2]
                    
                    self.append(arg[0])
                    self.append(arg[1])
                    self.append(arg[2])
                    
                    return
                
                #if passed in a int
                if isinstance(arg,int):
                    
                    self.x=args[0]
                    self.y=args[1]
                    self.z=args[2]
                    
                    self.append(args[0])
                    self.append(args[1])
                    self.append(args[2])
                    
                    return

p=point()
