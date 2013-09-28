import operator

import Tapp.Maya.rigging.builds as mrb
reload(mrb)
import Tapp.Maya.rigging.system_utils as mrs
reload(mrs)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)
handler=logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(funcName)s - LINE: %(lineno)d - %(message)s'))
log.addHandler(handler)

class system(object):
    
    def __init__(self,obj,methods=['default']):
        
        self.chain=mrs.buildChain(obj,log)
        
        self.methods=methods
        self.builds=self.getBuilds()
    
    def __repr__(self):
        
        result=''
        
        for build in self.builds:
                
            result+=build.__str__()
        
        return result
    
    def getBuilds(self):
        
        result=[]
        
        subclasses=mrb.base.__subclasses__()
        
        #if methods is a string
        if isinstance(self.methods,str):
            
            checklist=[]
            for cls in subclasses:
                checklist.append(cls.__name__)
            
            if not self.methods in checklist:
                log.error('build: methods input string invalid!')
                return
            else:
                self.methods=[self.methods]

        
        for cls in subclasses:
            temp=cls(self.chain,log)
            
            #adding dependencies
            for dependent in temp.dependencies:
                
                result.append(dependent(self.chain,log))
            
            #comparing builds to input builds
            for method in self.methods:
                
                if method=='default':
                    if temp.executeDefault:
                        
                        result.append(temp)
                else:
                    if method==str(temp.__class__.__name__):
                        
                        result.append(temp)
        
        #getting rid of duplicate builds
        seen_builds=set()
        new_result=[]
        for build in result:
            if build.__class__.__name__ not in seen_builds:
                new_result.append(build)
                seen_builds.add(build.__class__.__name__)
        
        #sort builds by executeOrder attribute
        result = sorted(new_result, key=operator.attrgetter('executeOrder'))
        
        return result
    
    def build(self,deleteSource=True):
        
        #delete source
        if deleteSource:
            
            mrs.deleteSource(self.chain)
        
        #build methods
        for build in self.builds:
            
            build.build()

#chain=mrs.buildChain('MetaSystem',log)
#print mrs.dictToChain(chain)

system('|clavicle',methods='ik').build()
#system('MetaSystem').build()

'''
parent constraints mess with the hierarchy, fix it!

by default have extra control on start, if not specified
used parent constraints to build static parenting

revise system to guide

hook up controls visibility to blend control
build spline
place guides like clusters tool
    if multiple verts, use one of them to align the guide towards
'''