from shutil import move
import json
import glob
import os

import maya.cmds as cmds
import maya.mel as mel


def PlayblastScene(filePath, camera, width=640, height=360,
              exportType='movie', HUD=None):
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

    result = cmds.objExists(camera)

    if result:

        #string $visPanels[] = `getPanel -vis`; < for fail safe of active panel
        panel = "modelPanel4"
        prevcam = cmds.modelEditor(panel, q=True, camera=True)

        mel.eval("lookThroughModelPanel " + camera + " " + panel)

        #getting current settings
        currentTime = cmds.currentTime(q=True)
        displayFilmGate = cmds.camera(camera, q=True, displayFilmGate=True)
        displayResolution = cmds.camera(camera, q=True, displayResolution=True)
        overscan = cmds.camera(camera, q=True, overscan=True)
        grid = cmds.modelEditor(panel, q=True, grid=True)
        displayAppearance = cmds.modelEditor(panel, q=True,
                                             displayAppearance=True)
        nurbsCurves = cmds.modelEditor(panel, q=True, nurbsCurves=True)

        #prepping for playblast
        cmds.camera(camera, edit=True, displayFilmGate=False,
                    displayResolution=False, overscan=1)
        cmds.modelEditor(panel, e=True, grid=False,
                         displayAppearance='smoothShaded',
                         nurbsCurves=False)

        #query and hide previous huds
        prevHUD = {}
        for headsup in cmds.headsUpDisplay(listHeadsUpDisplays=True):

            vis = cmds.headsUpDisplay(headsup, q=True, vis=True)
            prevHUD[headsup] = vis

            cmds.headsUpDisplay(headsup, e=True, vis=False)

        #creating custom huds
        customHUD = []
        if HUD != None:
            itr = 1
            for headsup in HUD:

                cmd = 'cmds.headsUpDisplay(\'temp' + str(itr) + '\''
                for key in headsup:
                    if type(headsup[key]) == str:
                        cmd += ',' + key + '=\'' + str(headsup[key]) + '\''
                    else:
                        cmd += ',' + key + '=' + str(headsup[key])

                cmd += ')'
                eval(cmd)

                customHUD.append('temp' + str(itr))

                itr += 1

        #playblasting
        if exportType == 'movie':

            result = cmds.playblast(f=filePath, format='qt',
                                    forceOverwrite=True, offScreen=True,
                                    percent=100, compression='H.264',
                                    quality=100, width=width,
                                    height=height, viewer=False)
        elif exportType == 'still':

            startTime = cmds.playbackOptions(q=True, minTime=True)
            endTime = cmds.playbackOptions(q=True, maxTime=True)

            midTime = ((endTime - startTime) / 2) + startTime

            result = cmds.playblast(f=filePath, format='iff',
                                    forceOverwrite=True, offScreen=True,
                                    percent=100, compression='png',
                                    quality=100, startTime=midTime,
                                    endTime=midTime, width=width,
                                    height=height, viewer=False,
                                    showOrnaments=True)

            path = result.split('.')[0]
            ext = result.split('.')[-1]

            oldfile = filePath + '.' + str(int(midTime)).zfill(4) + '.' + ext
            newfile = path + '.' + ext

            move(oldfile, newfile)

            result = newfile
        elif exportType == 'sequence':

            startTime = cmds.playbackOptions(q=True, minTime=True)
            endTime = cmds.playbackOptions(q=True, maxTime=True)

            result = cmds.playblast(f=filePath, format='iff',
                                    forceOverwrite=True, offScreen=True,
                                    percent=100, compression='png',
                                    quality=100, startTime=startTime,
                                    endTime=endTime, width=width,
                                    height=height, viewer=False,
                                    showOrnaments=True)

        #revert to settings
        cmds.currentTime(currentTime)
        cmds.camera(camera, edit=True, displayFilmGate=displayFilmGate,
                    displayResolution=displayResolution,
                    overscan=overscan)
        cmds.modelEditor(panel, e=True, grid=grid,
                         displayAppearance=displayAppearance,
                         nurbsCurves=nurbsCurves)

        for headsup in prevHUD:

            cmds.headsUpDisplay(headsup, e=True, vis=prevHUD[headsup])

        for headsup in customHUD:

            cmds.headsUpDisplay(headsup, remove=True)

        mel.eval("lookThroughModelPanel " + prevcam + " " + panel)

        return result
    else:
        cmds.warning('Requested camera cant be found!')

        return None


def ExportData(data):
    multipleFilters = "JSON Files (*.json)"
    f = cmds.fileDialog2(fileMode=0, fileFilter=multipleFilters)
    if f:
        f = open(f[0], 'w')
        json.dump(data, f)
        f.close()


def ImportData(f=None):
    multipleFilters = "JSON Files (*.json)"
    if not f:
        f = cmds.fileDialog2(fileMode=1, fileFilter=multipleFilters)
    if f:
        if isinstance(f, list):
            f = f[0]
        f = open(f, 'r')
        data = json.load(f)
        return data
    else:
        return None


def try_int(s):
    "Convert to integer if possible."
    try:
        return int(s)
    except:
        return s


def natsort_key(s):
    "Used internally to get a tuple by which s is sorted."
    import re
    return map(try_int, re.findall(r'(\d+|\D+)', s))


def natcmp(a, b):
    "Natural string comparison, case sensitive."
    return cmp(natsort_key(a), natsort_key(b))


def natcasecmp(a, b):
    "Natural string comparison, ignores case."
    return natcmp(a.lower(), b.lower())


def natsort(seq, cmpl=natcmp):
    "In-place natural string sort."
    seq.sort(cmpl)


def natsorted(seq, cmpl=natcmp):
    "Returns a copy of seq, sorted by natural string sort."
    import copy
    temp = copy.copy(seq)
    natsort(temp, cmpl)
    return temp


def SavePrompt():
    #save current scene?
    msg = 'Do you want to save the current scene?'
    confirm = cmds.confirmDialog(title='Save Scene', message=msg,
                                 button=['Yes', 'No'], defaultButton='Yes',
                                 cancelButton='No', dismissString='No')
    if confirm == 'Yes':
        cmds.file(save=True)


def PlayblastData(data, output=None, width=1920, height=1080):

    #playblasting data
    for item in data:
        #finding latest file version
        f = item['file'].replace('#', '?')
        files = []
        for name in glob.glob(item['folder'] + '/' + f):
            files.append(name)
        mayaFile = natsorted(files)[-1]

        #playblast file
        cmds.file(mayaFile, open=True, force=True)
        filePath = mayaFile.replace('.ma', '.mov')

        if output:
            fileName = os.path.basename(filePath)
            filePath = os.path.join(output, fileName)

        PlayblastScene(filePath, item['camera'], width, height)

    cmds.file(newFile=True, force=True)
