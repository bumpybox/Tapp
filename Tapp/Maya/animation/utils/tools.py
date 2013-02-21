import Tapp.Maya.utils.yaml as muy
import Tapp.Maya.utils.meta as mum

def exportData(module,outputFile):
    
    root=mum.UpStream(module, 'root')
    
    modules={}
    
    for module in mum.DownStream(root, 'module', allNodes=True):
        
        cnts=mum.DownStream(module, 'control')
        
        moduleData={}
        
        for cnt in cnts:
            
            data=mum.GetData(cnt)
            
            tn=mum.GetTransform(cnt)
            moduleData[str(tn)]=data
        
        modules[str(module)]=moduleData
    
    f=open(outputFile,'w')
    muy.dump(modules, f)
    f.close()

def importData(inputFile):
    
    f = open(inputFile)
    data = muy.safe_load(f)
    f.close()
    
    return data

#exportData('meta_l_joint1_cnt','c:/temp.yml')