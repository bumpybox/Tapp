import maya.cmds as cmds

def ExportPlayblast():
    
    #getting file path and name
    basicFilter = "Playblast (*.mov)"
    filePath=cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=1,
                              caption='Export Playblast')
    
    #exporting playblast
    __exportPlayblast__(filePath[0])

def __exportPlayblast__(filePath,width=640,height=360):
    ''' Exports playblast to filePath
    '''
    
    panel=cmds.getPanel(wf=True)
    panelType=cmds.getPanel(typeOf=panel)
    
    if panelType=='modelPanel':
        cam=cmds.modelEditor(panel, q=True,camera=True)
        
        #getting current settings
        currentTime=cmds.currentTime(q=True)
        displayFilmGate=cmds.camera(cam,q=True,displayFilmGate=True)
        displayResolution=cmds.camera(cam,q=True,displayResolution=True)
        overscan=cmds.camera(cam,q=True,overscan=True)
        grid=cmds.modelEditor(panel,q=True,grid=True)
        displayAppearance=cmds.modelEditor(panel,q=True,displayAppearance=True)
        headsUpDisplay=cmds.modelEditor(panel,q=True,headsUpDisplay=True)
        nurbsCurves=cmds.modelEditor(panel,q=True,nurbsCurves=True)
        
        #prepping for playblast
        cmds.camera(cam,edit=True,displayFilmGate=False,displayResolution=False,overscan=1)
        cmds.modelEditor(panel,e=True,grid=False,
                         displayAppearance='flatShaded',headsUpDisplay=False,
                         nurbsCurves=False)
        
        #playblasting
        cmds.playblast(f=filePath,format='qt',forceOverwrite=True,offScreen=True,percent=100,
                       compression='H.264',quality=100,widthHeight=(width,height))
        
        #revert to settings
        cmds.currentTime(currentTime)
        cmds.camera(cam,edit=True,displayFilmGate=displayFilmGate,
                    displayResolution=displayResolution,
                    overscan=overscan)
        cmds.modelEditor(panel,e=True,grid=grid,
                         displayAppearance=displayAppearance,
                         headsUpDisplay=headsUpDisplay,
                         nurbsCurves=nurbsCurves)
    else:
        cmds.warning('Current view is not a camera view! Please select correct view.')
        
        return None