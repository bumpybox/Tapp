from shutil import move

import maya.cmds as cmds
import maya.mel as mel

def ExportPlayblast():
    
    #getting file path and name
    basicFilter = "Playblast (*.mov)"
    filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                              caption='Export Playblast')
    
    #exporting playblast
    __exportPlayblast__(filePath[0])

def __exportPlayblast__(filePath,camera,width=640,height=360,exportType='movie',HUD=None):
    ''' Exports playblast to filePath
        
        filePath=path to file with no extension
                    eg. c:/temp
        
        camera=camera to generate playblast from
        
        type=['movie','still','sequence']
            movie = exports video
            still = exports image from middle of timeline
            sequence = exports image sequence
        
        HUD is a list of dictionaries following this format.
        
        usage:
        HUD=[]
        time=time.time()
        timestamp=str(datetime.datetime.fromtimestamp(time).strftime('%d-%m-%Y %H:%M:%S'))
        HUD.append({'label':timestamp,
                    'block':0,
                    'section':1})
        HUD.append({'label':'Bait Studio',
                    'block':0,
                    'section':2})
        username = str(getpass.getuser())
        HUD.append({'label':username,
                    'block':0,
                    'section':3})
        filePath='c:/temp.ext'
        HUD.append({'label':filePath,
                    'block':1,
                    'section':7})
        
        __exportPlayblast__('c:/temp', 'shotCam', HUD=HUD,exportType='still')
    '''
    
    result=cmds.objExists(camera)
    
    if result:
        
        #string $visPanels[] = `getPanel -vis`; < for fail safe of active panel
        panel = "modelPanel4"
        prevcam=cmds.modelEditor(panel, q=True,camera=True)
        
        mel.eval("lookThroughModelPanel "+camera+" "+panel)
        
        #getting current settings
        currentTime=cmds.currentTime(q=True)
        displayFilmGate=cmds.camera(camera,q=True,displayFilmGate=True)
        displayResolution=cmds.camera(camera,q=True,displayResolution=True)
        overscan=cmds.camera(camera,q=True,overscan=True)
        grid=cmds.modelEditor(panel,q=True,grid=True)
        displayAppearance=cmds.modelEditor(panel,q=True,displayAppearance=True)
        nurbsCurves=cmds.modelEditor(panel,q=True,nurbsCurves=True)
        
        #prepping for playblast
        cmds.camera(camera,edit=True,displayFilmGate=False,displayResolution=False,overscan=1)
        cmds.modelEditor(panel,e=True,grid=False,
                         displayAppearance='smoothShaded',
                         nurbsCurves=False)
        
        #query and hide previous huds
        prevHUD={}
        for headsup in cmds.headsUpDisplay(listHeadsUpDisplays=True):
            
            vis=cmds.headsUpDisplay(headsup,q=True,vis=True)
            prevHUD[headsup]=vis
            
            cmds.headsUpDisplay(headsup,e=True,vis=False)
        
        #creating custom huds
        customHUD=[]
        if HUD!=None:
            itr=1
            for headsup in HUD:
                
                cmd='cmds.headsUpDisplay(\'temp'+str(itr)+'\''
                for key in headsup:
                    if type(headsup[key])==str:
                        cmd+=','+key+'=\''+str(headsup[key])+'\''
                    else:
                        cmd+=','+key+'='+str(headsup[key])
                
                cmd+=')'
                eval(cmd)
                
                customHUD.append('temp'+str(itr))
                
                itr+=1
        
        #playblasting
        if exportType=='movie':
            
            result=cmds.playblast(f=filePath,format='qt',forceOverwrite=True,offScreen=True,percent=100,
                                   compression='H.264',quality=100,width=width,height=height,
                                   viewer=False)
        elif exportType=='still':
            
            startTime=cmds.playbackOptions(q=True,minTime=True)
            endTime=cmds.playbackOptions(q=True,maxTime=True)
            
            midTime=((endTime-startTime)/2)+startTime
            
            result=cmds.playblast(f=filePath,format='iff',forceOverwrite=True,offScreen=True,percent=100,
                                   compression='png',quality=100,startTime=midTime,endTime=midTime,
                                   width=width,height=height,viewer=False,showOrnaments=True)
            
            path=result.split('.')[0]
            ext=result.split('.')[-1]
            
            oldfile=filePath+'.'+str(int(midTime)).zfill(4)+'.'+ext
            newfile=path+'.'+ext
            
            move(oldfile,newfile)
            
            result=newfile
        elif exportType=='sequence':
            
            startTime=cmds.playbackOptions(q=True,minTime=True)
            endTime=cmds.playbackOptions(q=True,maxTime=True)
            
            result=cmds.playblast(f=filePath,format='iff',forceOverwrite=True,offScreen=True,percent=100,
                                   compression='png',quality=100,startTime=startTime,endTime=endTime,
                                   width=width,height=height,viewer=False,showOrnaments=True)
        
        #revert to settings
        cmds.currentTime(currentTime)
        cmds.camera(camera,edit=True,displayFilmGate=displayFilmGate,
                    displayResolution=displayResolution,
                    overscan=overscan)
        cmds.modelEditor(panel,e=True,grid=grid,
                         displayAppearance=displayAppearance,
                         nurbsCurves=nurbsCurves)
        
        for headsup in prevHUD:
            
            cmds.headsUpDisplay(headsup,e=True,vis=prevHUD[headsup])
        
        for headsup in customHUD:
            
            cmds.headsUpDisplay(headsup,remove=True)
        
        mel.eval("lookThroughModelPanel "+prevcam+" "+panel)
        
        return result
    else:
        cmds.warning('Requested camera cant be found!')
        
        return None