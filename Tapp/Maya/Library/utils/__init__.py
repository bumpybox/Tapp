import os

import Tapp.Maya.Library.config as mLc


def ReadLibrary():
    
    #getting repository
    repo=mLc.config['repository']
    
    #traverse through directories and generate data
    items={}
    
    for category in os.listdir(repo):
        for group in os.listdir(repo+'/'+category):
            for f in os.listdir(repo+'/'+category+'/'+group):
                if f.endswith('.ml'):
                    
                    data={}
                    data['dir']=repo+'/'+category+'/'+group
                    
                    #user data
                    ml=open(data['dir']+'/'+f,'r')
                    userdata=ml.read()
                    
                    userdata=userdata.split('\n')
                    for d in userdata:
                        d=d.split('=')
                        
                        data[d[0]]=d[1]
                    
                    items[f.split('.')[0]]=data
    
    #return
    return items