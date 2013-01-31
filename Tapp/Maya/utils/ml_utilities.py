# 
#   -= ml_utilities.py =-
#                __   by Morgan Loomis
#     ____ ___  / /  http://morganloomis.com
#    / __ `__ \/ /  Licensed under Creative Commons BY-SA
#   / / / / / / /  http://creativecommons.org/licenses/by-sa/3.0/
#  /_/ /_/ /_/_/  _________                                   
#               /_________/  Revision 7, 2012-08-07
#      _______________________________
# - -/__ Installing Python Scripts __/- - - - - - - - - - - - - - - - - - - - 
# 
# Copy this file into your maya scripts directory, for example:
#     C:/Documents and Settings/user/My Documents/maya/scripts/ml_utilities.py
# 
# Run the tool by importing the module, and then calling the primary function.
# From python, this looks like:
#     import ml_utilities
#     ml_utilities._showHelpCommand()
# From MEL, this looks like:
#     python("import ml_utilities;ml_utilities._showHelpCommand()");
#      _________________
# - -/__ Description __/- - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# ml_utilities isn't a stand alone tool, but rather it's a collection of support functions
# that are required by several of the tools in this library. The individual tools will tell
# you if this script is required.
#      ___________
# - -/__ Usage __/- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
# 
# ml_utilities isn't a stand alone tool, and so it isn't meant to be used directly.
# However, you can certainly call these functions if they seem useful in your own scripts.
#                                                             __________
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - /_ Enjoy! _/- - -

__author__ = 'Morgan Loomis'
__license__ = 'Creative Commons Attribution-ShareAlike'
__revision__ = 7

import maya.cmds as mc
import maya.mel as mm
from maya import OpenMaya
from functools import partial
import shutil, os, re, sys

#declare some variables
websiteURL = 'http://morganloomis.com'
wikiURL = websiteURL+'/wiki/tools.html'


def _showHelpCommand(url):
    '''
    This just returns the maya command for launching a wiki page, since that gets called a few times
    '''
    return 'import maya.cmds;maya.cmds.showHelp("'+url+'",absolute=True)'


def main():
    '''
    This just launches the online help and serves as a placeholder for the default function for this script.
    '''
    mc.showHelp(wikiURL+'#ml_utilities', absolute=True)
    

def upToDateCheck(revision, prompt=True):
    '''
    This is a check that can be run by scripts that import ml_utilities to make sure they
    have the correct version.
    '''
    
    if not '__revision__' in locals():
        return
    
    if revision > __revision__:
        if prompt and mc.optionVar(query='ml_utilities_revision') < revision:
            result = mc.confirmDialog( title='Module Out of Date', 
                        message='Your version of ml_utilities may be out of date for this tool. Without the latest file you may encounter errors.',
                        button=['Download Latest Revision','Ignore', "Don't Ask Again"], 
                        defaultButton='Download Latest Revision', cancelButton='Ignore', dismissString='Ignore' )
            
            if result == 'Download Latest Revision':
                mc.showHelp('http://morganloomis.com/download/ml_utilities.py', absolute=True)
            elif result == "Don't Ask Again":
                mc.optionVar(intValue=('ml_utilities_revision', revision))
        return False
    return True


def createHotkey(command, name, description=''):
    '''
    Open up the hotkey editor to create a hotkey from the specified command
    '''
    
    mm.eval('hotkeyEditor')
    mc.textScrollList('HotkeyEditorCategoryTextScrollList', edit=True, selectItem='User')
    mm.eval('hotkeyEditorCategoryTextScrollListSelect')
    mm.eval('hotkeyEditorCreateCommand')

    mc.textField('HotkeyEditorNameField', edit=True, text=name)
    mc.textField('HotkeyEditorDescriptionField', edit=True, text=description)
    mc.scrollField('HotkeyEditorCommandField', edit=True, text=command)


def createShelfButton(command, label='', name=None, description='', 
                       image=None, #the default image is a circle
                       labelColor=(1, 0.5, 0), 
                       labelBackgroundColor=(0, 0, 0, 0.5), 
                       backgroundColor=None
                       ):
    '''
    Create a shelf button for the command on the current shelf
    '''
    #some good default icons:
    #menuIconConstraints - !
    #render_useBackground - circle
    #render_volumeShader - black dot
    #menuIconShow - eye
    
    gShelfTopLevel = mm.eval('$temp=$gShelfTopLevel')
    if not mc.tabLayout(gShelfTopLevel, exists=True):
        OpenMaya.MGlobal.displayWarning('Shelf not visible.')
        return

    if not name:
        name = label
    
    if not image:
        image = getIcon(name)
    if not image:
        image = 'render_useBackground'
        
    shelfTab = mc.shelfTabLayout(gShelfTopLevel, query=True, selectTab=True)
    shelfTab = gShelfTopLevel+'|'+shelfTab
    
    #add additional args depending on what version of maya we're in
    kwargs = dict()
    if mm.eval('getApplicationVersionAsFloat') >= 2009:
        kwargs['commandRepeatable'] = True
    if mm.eval('getApplicationVersionAsFloat') >= 2011:
        kwargs['overlayLabelColor'] = labelColor
        kwargs['overlayLabelBackColor'] = labelBackgroundColor
        if backgroundColor:
            kwargs['enableBackground'] = bool(backgroundColor)
            kwargs['backgroundColor'] = backgroundColor
    
    return mc.shelfButton(parent=shelfTab, label=name, command=command,
                          imageOverlayLabel=label, image=image, annotation=description, 
                          width=32, height=32, align='center', **kwargs)


def deselectChannels():
    '''
    Deselect selected channels in the channelBox
    by clearing selection and then re-selecting
    '''
    
    if not getSelectedChannels():
        return
    sel = mc.ls(sl=True)
    mc.select(clear=True)
    mc.evalDeferred(partial(mc.select,sel))


def formLayoutGrid(form, controls, offset=1):
    '''
    Controls should be a list of lists, and this will arrange them in a grid
    '''

    kwargs = {'edit':True, 'attachPosition':list()}
    rowInc = 100/len(controls)
    colInc = 100/len(controls[0])
    position = {'left':0,'right':100,'top':0,'bottom':100}
    
    for r,row in enumerate(controls):
        position['top'] = r*rowInc
        position['bottom'] = (r+1)*rowInc
        for c,ctrl in enumerate(row):
            position['left'] = c*colInc
            position['right'] = (c+1)*colInc
            for k in position.keys():
                kwargs['attachPosition'].append((ctrl, k, offset, position[k]))

    mc.formLayout(form, **kwargs)


def frameRange(start=None, end=None):
    '''
    Returns the frame range based on the highlighted timeslider,
    or otherwise the playback range.
    '''
    
    if not start and not end:
        gPlayBackSlider = mm.eval('$temp=$gPlayBackSlider')
        if mc.timeControl(gPlayBackSlider, query=True, rangeVisible=True):
            frameRange = mc.timeControl(gPlayBackSlider, query=True, rangeArray=True)
            return frameRange
        else:
            start = mc.playbackOptions(query=True, min=True)
            end = mc.playbackOptions(query=True, max=True)
    
    return start,end
    

def getChannelFromAnimCurve(curve):
    '''
    Finding the channel associated with a curve has gotten really complicated since animation layers.
    This is a recursive function which walks connections from a curve until an animated channel is found.
    '''

    #we need to save the attribute for later.
    attr = ''
    if '.' in curve:
        curve, attr = curve.split('.')
        
    nodeType = mc.nodeType(curve)
    if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
        source = mc.listConnections(curve+'.output', source=False, plugs=True)
        if not source and nodeType=='animBlendNodeAdditiveRotation':
            #if we haven't found a connection from .output, then it may be a node that uses outputX, outputY, etc.
            #get the proper attribute by using the last letter of the input attribute, which should be X, Y, etc.
            source = mc.listConnections(curve+'.output'+attr[-1], source=False, plugs=True)
        if source:
            nodeType = mc.nodeType(source[0])
            if nodeType.startswith('animCurveT') or nodeType.startswith('animBlendNode'):
                return getChannelFromAnimCurve(source[0])
            return source[0]


def getCurrentCamera():
    '''
    Returns the camera that you're currently looking through.
    If the current highlighted panel isn't a modelPanel, 
    '''
    
    panel = mc.getPanel(withFocus=True)
    
    if mc.getPanel(typeOf=panel) != 'modelPanel':
        #just get the first visible model panel we find, hopefully the correct one.
        for p in mc.getPanel(visiblePanels=True):
            if mc.getPanel(typeOf=p) == 'modelPanel':
                panel = p
                mc.setFocus(panel)
                break
    
    if mc.getPanel(typeOf=panel) != 'modelPanel':
        OpenMaya.MGlobal.displayWarning('Please highlight a camera viewport.')
        return False
    
    camShape = mc.modelEditor(panel, query=True, camera=True)

    if not camShape:
        return False
    
    if mc.nodeType(camShape) == 'transform':
        return camShape
    elif mc.nodeType(camShape) == 'camera':
        return mc.listRelatives(camShape, parent=True)[0]


def getFrameRate():
    '''
    Return an int of the current frame rate
    '''
    currentUnit = mc.currentUnit(query=True, time=True)
    if currentUnit == 'film':
        return 24
    if currentUnit == 'show':
        return 48
    if currentUnit == 'pal':
        return 25
    if currentUnit == 'ntsc':
        return 30
    if currentUnit == 'palf':
        return 50
    if currentUnit == 'ntscf':
        return 60
    if 'fps' in currentUnit:
        return int(currentUnit.substitute('fps',''))
    
    return 1


def getIcon(name):
    '''
    Check if an icon name exists, and return with proper extension.
    Otherwise return standard warning icon.
    '''
    
    ext = '.png'
    if mm.eval('getApplicationVersionAsFloat') < 2011:
        ext = '.xpm'
    
    if not name.endswith('.png') and not name.endswith('.xpm'):
        name+=ext
    
    for each in os.environ['XBMLANGPATH'].split(':'):
        #on some linux systems each path ends with %B, for some reason
        iconPath = os.path.abspath(each.replace('%B',''))
        iconPath = os.path.join(iconPath,name)
        if os.path.exists(iconPath):        
            return name
    
    return None       
    return 'menuIconConstraints'+ext


def getIconPath():
    '''
    Find the icon path
    '''
    
    appDir = os.environ['MAYA_APP_DIR']
    for each in os.environ['XBMLANGPATH'].split(':'):
        #on some linux systems each path ends with %B, for some reason
        iconPath = each.replace('%B','')
        if iconPath.startswith(appDir):
            iconPath = os.path.abspath(iconPath)
            if os.path.exists(iconPath):
                return iconPath


def getKeyedFromHierarchy(objs, includeRoot=True):
    '''
    This will return all keyed objects within the hierarchy.
    If the selected object has a namespace, only nodes within that namespace will be returned.
    '''
    
    objs = mc.ls(objs, long=True)
    tops = list()
    namespaces = list()
    for obj in objs:
        namespace = getNamespace(obj)
        if namespace in namespaces:
            #we've already done this one
            continue
        
        hier = obj.split('|')
        
        if not namespace:
            #if there's no namespace, just grab the top of the hierarchy
            if len(hier) > 1:
                tops.append(hier[1])
            else:
                tops.append(obj)
        
        else:
            #otherwise look through the hierarchy until you find the first node with the same namespace
            namespaces.append(namespace)
            for each in hier:
                if namespace in each:
                    tops.append(each)
                    break
    
    if not tops:
        #if we haven't been sucessful, we're done
        return
    
    nodes = mc.listRelatives(tops, pa=True, type='transform', ad=True)
    if includeRoot:
        nodes.extend(tops)
    
    #now that we've determined the hierarchy, lets find keyed nodes
    keyedNodes = list()
    
    for node in nodes:
        # this will only return time based keyframes, not driven keys
        curves = mc.keyframe(node, time=(':',), query=True, name=True)
        if curves:
            keyedNodes.append(node)
    
    return keyedNodes

    
def getNamespace(node):
    '''Returns the namespace of a node with simple string parsing'''
    
    namespace = ''
    
    if node and ':' in node:
        namespace = node.partition(':')[0]
        namespace+=':'
    return namespace


def getSelectedChannels():
    '''
    Return channels that are selected in the channelbox
    '''
    
    if not mc.ls(sl=True):
        return
    gChannelBoxName = mm.eval('$temp=$gChannelBoxName')
    sma = mc.channelBox(gChannelBoxName, query=True, sma=True)
    ssa = mc.channelBox(gChannelBoxName, query=True, ssa=True)
    sha = mc.channelBox(gChannelBoxName, query=True, sha=True)
                
    channels = list()
    if sma:
        channels.extend(sma)
    if ssa:
        channels.extend(ssa)
    if sha:
        channels.extend(sha)

    return channels


def listAnimCurves(objOrAttrs):
    '''
    This lists connections to all types of animNodes
    '''
    
    animNodes = list()
    
    tl = mc.listConnections(objOrAttr, s=True, d=False, type='animCurveTL')
    ta = mc.listConnections(objOrAttr, s=True, d=False, type='animCurveTA')
    tu = mc.listConnections(objOrAttr, s=True, d=False, type='animCurveTU')
    
    if tl:
        animNodes.extend(tl)
    if ta:
        animNodes.extend(ta)
    if tu:
        animNodes.extend(tu)
    
    return animNodes


def renderShelfIcon(name='tmp', width=32, height=32):
    '''
    This renders a shelf-sized icon and hopefully places it in your icon directory
    '''
    imageName=name

    #getCamera
    cam = getCurrentCamera()
    
    #save these values for resetting
    currentRenderer = mc.getAttr('defaultRenderGlobals.currentRenderer')
    imageFormat = mc.getAttr('defaultRenderGlobals.imageFormat')

    mc.setAttr('defaultRenderGlobals.currentRenderer', 'mayaSoftware', type='string')

    mayaVersion = mm.eval('getApplicationVersionAsFloat')
    
    imageFormat = 50 #XPM
    if mayaVersion >= 2011:
        imageFormat = 32 #PNG

    mc.setAttr('defaultRenderGlobals.imageFormat', imageFormat)
    mc.setAttr('defaultRenderGlobals.imfkey', 'xpm', type='string')
    #here's the imageName
    mc.setAttr('defaultRenderGlobals.imageFilePrefix', imageName, type='string')

    mc.setAttr(cam+'.backgroundColor', 0.8,0.8,0.8, type='double3')
    #need to reset this afterward
    
    image = mc.render(cam, xresolution=width, yresolution=height)
    base = os.path.basename(image)

    #here we attempt to move the rendered icon to a more generalized icon location
    newPath = getIconPath()
    newPath = os.path.join((newPath, base))
    shutil.move(image, newPath)
    image = newPath
            
    #reset
    mc.setAttr('defaultRenderGlobals.currentRenderer', currentRenderer, type='string')
    mc.setAttr('defaultRenderGlobals.imageFormat', imageFormat)
    
    return image
    
    
class Dragger(object):

    def __init__(self,
                name = 'mlDraggerContext',
                title = 'Dragger',
                defaultValue=0,
                minValue=None,
                maxValue=None,
                multiplier=0.01,
                cursor='hand'
                ):
        
        self.multiplier = multiplier
        self.defaultValue = defaultValue
        self.minValue = minValue
        self.maxValue = maxValue
        self.cycleCheck = mc.cycleCheck(query=True, evaluation=True)
        
        self.draggerContext = name
        if not mc.draggerContext(self.draggerContext, exists=True):
            self.draggerContext = mc.draggerContext(self.draggerContext)
                                                    
        mc.draggerContext(self.draggerContext, edit=True,
                        pressCommand=self.press, 
                        dragCommand=self.drag,
                        releaseCommand=self.release,
                        cursor=cursor,
                        drawString=title,
                        undoMode='all'
                        )
                                                    
    
    def press(self, *args):
        '''
        Be careful overwriting the press method in child classes, because of the undoInfo openChunk
        '''
        
        self.anchorPoint = mc.draggerContext(self.draggerContext, query=True, anchorPoint=True)
        self.button = mc.draggerContext(self.draggerContext, query=True, button=True)
        #dragString
        
        # This makes it so the script editor doesn't get spammed by a cycle in the puppet
        mc.cycleCheck(evaluation=False)
        
        # This turns off the undo queue until we're done dragging, so we can undo it.
        mc.undoInfo(openChunk=True)
        
    def drag(self, *args):
        
        self.dragPoint = mc.draggerContext(self.draggerContext, query=True, dragPoint=True)
        
        #if this doesn't work, try getmodifier
        self.modifier = mc.draggerContext(self.draggerContext, query=True, modifier=True)
        
        self.x = ((self.dragPoint[0] - self.anchorPoint[0]) * self.multiplier) + self.defaultValue
        self.y = ((self.dragPoint[1] - self.anchorPoint[1]) * self.multiplier) + self.defaultValue
        
        if self.minValue is not None and self.x < self.minValue:
            self.x = self.minValue
        if self.maxValue is not None and self.x > self.maxValue:
            self.x = self.maxValue
        
        #dragString
        if self.modifier == 'control':
            if self.button == 1:
                self.dragControlLeft(*args)
            elif self.button == 2:
                self.dragControlMiddle(*args)
        elif self.modifier == 'shift':
            if self.button == 1:
                self.dragShiftLeft(*args)
            elif self.button == 2:
                self.dragShiftMiddle(*args)
        else:
            if self.button == 1:
                self.dragLeft()
            elif self.button == 2:
                self.dragMiddle()
        
        mc.refresh()
    
    def release(self, *args):
        '''
        Be careful overwriting the release method in child classes. Not closing the undo chunk leaves maya in a sorry state.
        '''
        # close undo chunk and turn cycle check back on
        mc.undoInfo(closeChunk=True)
        mc.cycleCheck(evaluation=self.cycleCheck)
        mm.eval('SelectTool')
    
    def drawString(self, message):
        '''
        Creates a string message at the position of the pointer.
        '''
        mc.draggerContext(self.draggerContext, edit=True, drawString=message)
        
    def dragLeft(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
            
    def dragMiddle(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
        
    def dragControlLeft(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
            
    def dragControlMiddle(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
        
    def dragShiftLeft(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
            
    def dragShiftMiddle(self,*args):
        '''Placeholder for potential commands. This is meant to be overridden by a child class.'''
        pass
    
    #no drag right, because that is monopolized by the right click menu
    #no alt drag, because that is used for the camera
    
    def setTool(self):
        mc.setToolTo(self.draggerContext)


class IsolateViews():
    '''
    Isolates selection with nothing selected for all viewports
    This speeds up any process that causes the viewport to refresh,
    such as baking or changing time. 
    '''
    
    def __enter__(self):
    
        self.sel = mc.ls(sl=True)
        self.modelPanels = mc.getPanel(type='modelPanel')
        self.isolate(True)
        
        mc.select(clear=True)
        
        #save and turn off settings that might print to the script editor
        self.resetCycleCheck = mc.cycleCheck(query=True, evaluation=True)
        mc.cycleCheck(evaluation=False)
        
        self.resetAutoKey = mc.autoKeyframe(query=True, state=True)
        mc.autoKeyframe(state=False)
        
    
    def __exit__(self, *args):
            
        #reset settings
        mc.cycleCheck(evaluation=self.resetCycleCheck)
        mc.autoKeyframe(state=self.resetAutoKey)
        
        if self.sel:
            mc.select(self.sel)
            
        self.isolate(False)
        
    
    def isolate(self, state):
    
        mc.select(clear=True)
        for each in self.modelPanels:
            mc.isolateSelect(each, state=state)


class KeySelection(object):
    '''
    This class encapsulates a set of keys based on a selection order, which 
    is defined by a list of lists argument. Each item in the main list is a
    list of parameters that narrow down what keys should be included.
    
    Much of this code is still in progress
    
    The available arguments are:
    
        #the following determine specific curves or keys
        selectedObjects
        selectedChannels
        inGraphEditor
        selectedKey
        selectedCurve
        keyedChannels
        selectedNamespace
        scene
       
        setKey - special case arg, sets key on the current frame
        deleteSubFrames - if setting keys, should non-whole-number keys surrounding the set key be deleted?
        
        #the following determine specific times or ranges:
        range
        toEnd
        fromBeginning
        timeSlider
        selectedKeyRange
        previous - the key time before the specified keys
        next - the key time after the specified keys
        current
        
    
    After the object is created, the class methods either return those keys 
    directly, or can act on them with  
    '''
    def __init__(self, selectionOrder):
        
        allArgOptions = [
            'selectedObjects',
            'selectedChannels',
            'inGraphEditor',
            'selectedKey',
            'selectedCurve',
            'keyedChannels',
            'selectedNamespace',
            'scene',
            'setKey',
            'range',
            'toEnd',
            'fromBeginning',
            'timeSlider',
            'selectedKeyRange',
            'previous',
            'next',
            'current',
            'includeShapes'
            ]
        
        if not isinstance(selectionOrder, list) and not isinstance(selectionOrder, tuple):
            OpenMaya.MGlobal.displayWarning('selectionOrder argument should be a list of lists.')
            return
        
        for each in selectionOrder:
            if not isinstance(each, list) and not isinstance(each, tuple):
                OpenMaya.MGlobal.displayWarning('Each element in the selectionOrder argument should also be a list.')
        
        shortestTime = getFrameRate()/6000     
        
        self.curves = list()
        self.channels = list()
        self.args = dict()
        
        sel = mc.ls(sl=True)
        currentTime = mc.currentTime(query=True)
        time = currentTime
        
        self.time = None
        self.timeStart = None
        self.timeEnd = None
        self.timeRange = None
        self.selected = False

        #Is the graph editor open?
        graphEdExists = False
        if 'graphEditor1' in mc.getPanel(visiblePanels=True):
            graphEdExists = True
        
        #declare variable for the arg loop
        animNode = list()
        
        for arg in selectionOrder:

            holdChannels = list()

            if 'selectedObjects' in arg:
                #This argument acts on selected objects
                if not sel:
                    continue
                if 'setKey' in arg:
                    for obj in sel:
                        keyable = mc.listAttr(obj, keyable=True, unlocked=True)
                        for attr in keyable:
                            plug = '.'.join((obj, attr))
                            if mc.listConnections(plug, s=True, d=False, type='animCurve') or not mc.listConnections(plug, s=True, d=False):
                                holdChannels.append(plug)
                            elif mc.listConnections(plug, s=True, d=False, type='animBlendNodeAdditiveDL'):
                                OpenMaya.MGlobal.displayWarning('Warning, this might not work. channels are connected to an animBlend node')
                                holdChannels.append(plug)
                else:
                    holdChannels = sel
            
            elif 'selectedChannels' in arg:
                
                chanBoxChan = getSelectedChannels()
                
                if not chanBoxChan:
                    continue
                
                for obj in sel:
                    for attr in chanBoxChan:
                        if mc.attributeQuery(attr, node=obj, exists=True):
                            holdChannels.append('.'.join((obj,attr)))
                
            elif 'inGraphEditor' in arg:
                if not graphEdExists:
                    continue

                graphVis = mc.selectionConnection('graphEditor1FromOutliner', query=True, obj=True)
                
                if not graphVis:
                    continue
                
                for each in graphVis:
                    if 'setKey' in arg:
                        chan = getChannelFromAnimCurve(each)
                        if chan:
                            holdChannels.append(chan)
                        else:
                            holdChannels.append(each)
                    else:
                        try:
                            holdChannels.extend(mc.keyframe(each, query=True, name=True))
                        except StandardError:
                            pass

            elif 'selectedKey' in arg or 'selectedCurve' in arg:
                if not graphEdExists:
                    continue
                    
                animNode = mc.keyframe(query=True, name=True, selected=True)
                
                if not animNode:
                    continue
                
                if 'setKey' in arg:
                    for each in animNode:
                        holdChannels.append(getChannelFromAnimCurve(each))
                else:
                    self.selected = True
                    holdChannels.extend(animNode)
                    #need a way to store times here?
                    keyTimes = mc.keyframe(animNode, query=True, timeChange=True, selected=True)
                    self.time = keyTimes
                    keyTimes.sort()
                    self.timeStart = keyTimes[0]
                    self.timeEnd = keyTimes[-1]
                        

            elif 'keyedChannels' in arg:
                if not sel:
                    continue
                
                objs = sel
                if 'includeShapes' in arg:
                    shapes = mc.listRelatives(sel, shapes=True)
                    if shapes:
                        objs.extend(shapes)
                
                #this should skip driven keys
                tl = mc.listConnections(objs, s=True, d=False, type='animCurveTL')
                ta = mc.listConnections(objs, s=True, d=False, type='animCurveTA')
                tu = mc.listConnections(objs, s=True, d=False, type='animCurveTU')
                
                if tl:
                    animNode.extend(tl)
                if ta:
                    animNode.extend(ta)
                if tu:
                    animNode.extend(tu)
                
                if not animNode:
                    continue
                
                holdChannels.extend(animNode)

            elif 'selectedNamespace' in arg:
                pass

            elif 'scene' in arg:
            
                animNode = mc.ls(type='animCurveTL')
                animNode.extend(mc.ls(type='animCurveTA'))
                animNode.extend(mc.ls(type='animCurveTU'))
                if not animNode:
                    continue
                if 'setKey' in arg:
                    for each in animNode:
                        holdChannels.append(getChannelFromAnimCurve(each))
                else:
                    holdChannels.extend(animNode)

            else:
                argNotFound = False
                for each in arg:
                    if not each in allArgOptions:
                        OpenMaya.MGlobal.displayWarning('Argument not recognized: '+each)
                        argNotFound = True
                if argNotFound:
                    print '\nLegal arguments:'
                    for each in allArgOptions:
                        print '\t'+each
                    print ''
                    OpenMaya.MGlobal.displayWarning('One or more arguments not recognized, see script editor for argument list.')
                    return
                continue
            
            #if no channels, continue on to the next iteration
            if not holdChannels:
                continue
            
            self.channels = holdChannels

            if 'setKey' in arg:
                #this is a special arg, which creates keys on the attributes determined so far
                self.setKeyframe(insert=True)
                
                #not sure that this should be managed in KeySelection
#                 if 'deleteSubFrames' in arg:
#                     #remove nearby sub-frames
#                     #this breaks at higher frame ranges because maya doesn't keep enough digits
#                     #this value is also different for different frame rates
#                     time = mc.currentTime(query=True)
#                     if time % 1 == 0 and -9999 < time < 9999:
#                         #the distance that keys can be is independent of frame rate, so we have to convert based on the frame rate.
#                         tol = getFrameRate()/6000.0
#                         mc.cutKey(holdChannels, time=(time+tol,time+0.5))
#                         mc.cutKey(holdChannels, time=(time-0.5,time-tol))
                
                #self.flags['time'] = time
                self.time=(time,)

            #check that none of the animation curves are referenced and therefor uneditable
            #supposedly these are editable in 2013, so may have to update after I can test it.
            #in the future, it might be nice to have this culling happen before keys are set and cut.
            animCurves = mc.keyframe(self.channels, query=True, name=True)
            if animCurves:
                for curve in animCurves:
                    if mc.referenceQuery(curve, isNodeReferenced=True):
                        animCurves.remove(curve)
            
            #need to determine when it's ok to continue working on channels without curves
            if not animCurves and not 'selectedChannels' in arg and not 'selectedObjects' in arg:
                continue
        
            self.curves = animCurves
            
            if 'range' in arg:
                #this is selected range in the time slider
                self.timeStart, self.timeEnd = frameRange()
                break

            elif 'toEnd' in arg:
                if not 'current' in arg:
                    time+=shortestTime
                self.time = (str(time)+':',)
                self.timeStart = time
                break

            elif 'fromBeginning' in arg:
                if not 'current' in arg:
                    time-=shortestTime
                self.time = (':'+str(time),)
                self.timeEnd = time
                break

            elif 'selectedKeyRange' in arg:
                keyTimes = mc.keyframe(self.curves, query=True, timeChange=True, selected=True)
                if not keyTimes:
                    continue
                keyTimes.sort()
                
                if keyTimes[0] == keyTimes[-1]:
                    continue
                
                self.time = (keyTimes[0],keyTimes[-1])
                self.timeStart = keyTimes[0]
                self.timeEnd = keyTimes[-1]
                break

            else:
                if 'current' in arg:
                    self.time = (currentTime,)
                if 'previous' in arg:
                    frame = mc.findKeyframe(self.curves, time=(time,), which='previous')
                    self.timeStart = frame
                    if self.time:
                        self.time.append(self.timeStart)
                    else:
                        self.time = (self.timeStart,)
                if 'next' in arg:
                    frame = mc.findKeyframe(self.curves, time=(time,), which='next')
                    self.timeEnd = frame
                    if self.time:
                        self.time.append(self.timeEnd)
                    else:
                        self.time = (self.timeEnd,)
                        
                #finally, if no range arguments have been used, return all keys on the curve
                if not self.time:
                    self.time = (':',)
                break
    
    
    def setKeyframe(self,**kwargs):
        '''
        
        '''
        
        if self.time and not 'time' in kwargs:
            #still not sure about how I want to do this, but we need a discrete time.
            #if time is a string set to current time
            if isinstance(self.time, tuple) and isinstance(self.time[0], str):
                kwargs['time'] = mc.currentTime(query=True)
            else:
                kwargs['time'] = self.time
        
        if 'insert' in kwargs and kwargs['insert'] == True:
            #setKeyframe fails if insert option is used but there's no keyframes on the channels.
            #key any curves with insert, then key everything again without it
            curves = mc.keyframe(self.channels, query=True, name=True)
            if curves:
                mc.setKeyframe(curves, **kwargs)
            kwargs['insert'] = False
            
        mc.setKeyframe(self.channels, **kwargs)
        self.curves = mc.keyframe(self.channels, query=True, name=True)
        
    
    def keyframe(self,**kwargs):
        '''
        
        '''
        if self.time and not 'time' in kwargs:
            kwargs['time'] = self.time
        if self.selected:
            kwargs['sl'] = True
        
        return mc.keyframe(self.curves, **kwargs)
        
        
    def cutKey(self, includeSubFrames=False, **kwargs):
        '''
        
        '''
        if not 'includeUpperBound' in kwargs:
            kwargs['includeUpperBound'] = False
            
        if self.selected:
            mc.cutKey(sl=True, **kwargs)
            return
        
        if self.time and not 'time' in kwargs:
            if includeSubFrames:
                kwargs['time'] = (round(self.time[0])-0.5, round(self.time[-1])+0.5)
            else:
                kwargs['time'] = self.time
        mc.cutKey(self.curves, **kwargs)
        
        
    def selectKey(self,**kwargs):
    
        if self.time:
            kwargs['time'] = self.time
        mc.selectKey(self.curves, **kwargs)
        
        
    def scaleKey(self,**kwargs):
        pass
    
    def tangentType(self, **kwargs):
        pass
        
    def keyTangent(self, **kwargs):
        pass            
        
    def getSortedKeyTimes(self):
        '''
        Returns a list of the key times in order without duplicates.
        '''
        if self.selected:
            keyTimes = self.time
        else:
            keyTimes = self.keyframe(query=True, timeChange=True)
        if not keyTimes:
            return
        return sorted(list(set(keyTimes)))
        
    def expand(self):
        
        kwargs = {'query':True}
        self.keyTimes = dict()
        self.keyIndex = dict()
        self.keyValue = dict()

        if self.time:
            kwargs['time'] = self.time
        if self.selected:
            kwargs['sl'] = True
            
        for curve in self.curves:
            if not curve:
                continue
            self.keyIndex[curve] = mc.keyframe(curve, indexValue=True, **kwargs)
            self.keyTimes[curve] = mc.keyframe(curve, timeChange=True, **kwargs)
            self.keyValue[curve] = mc.keyframe(curve, valueChange=True, **kwargs)


class MlUi():
    '''
    Window template for consistency
    '''

    def __init__(self, name, title, width=400, height=200, info='', menu=True, module=None):
    
        self.name = name
        self.title = title
        self.width = width
        self.height = height
        self.info = info
        self.menu = menu
        
        self.module = module
        if not module or module == '__main__':
            self.module = self.name

        #look for icon
        self.icon = getIcon(name)
        

    def __enter__(self):
        '''
        Initialize the UI
        '''
        if mc.window(self.name, exists=True):
            mc.deleteUI(self.name)

        mc.window(self.name, title='ml :: '+self.title, iconName=self.title, width=self.width, height=self.height, menuBar=self.menu)
        
        
        if self.menu:
            self.createMenu()
        
        self.form = mc.formLayout()
        self.column = mc.columnLayout(adj=True)

        
        mc.rowLayout( numberOfColumns=2, columnWidth2=(34, self.width-34), adjustableColumn=2, 
                    columnAlign2=('right','left'),
                    columnAttach=[(1, 'both', 0), (2, 'both', 8)] )

        #if we can find an icon, use that, otherwise do the text version
        if self.icon:
            mc.iconTextStaticLabel(style='iconOnly', image1=self.icon)
        else:
            mc.text(label=' _ _ |\n| | | |')
            
        if not self.menu:
            mc.popupMenu(button=1)
            mc.menuItem(label='Help', command=(_showHelpCommand(wikiURL+'#'+self.name)))
        
        mc.text(label=self.info)
        mc.setParent('..')
        mc.separator(height=8, style='single')
        return self
    
    
    def __exit__(self, *args):
        '''
        Finalize the UI
        '''
        
        mc.setParent(self.form)

        frame = mc.frameLayout(labelVisible=False)
        mc.helpLine()
        
        mc.formLayout( self.form, edit=True,
                     attachForm=((self.column, 'top', 0), (self.column, 'left', 0),
                                 (self.column, 'right', 0), (frame, 'left', 0),
                                 (frame, 'bottom', 0), (frame, 'right', 0)),
                     attachNone=((self.column, 'bottom'), (frame, 'top')) )

        mc.showWindow(self.name)
        mc.window(self.name, edit=True, width=self.width, height=self.height)

        
    def createMenu(self, *args):
        '''
        Create the main menu for the UI
        '''
        
        #generate shelf label by removing ml_
        shelfLabel = self.name.replace('ml_','')
        module = self.module
        if not module:
            module = self.name
            
        #if icon exists, use that
        argString = ''
        if not self.icon:
            argString = ', label="'+shelfLabel+'"'
        
        mc.menu(label='Tools')
        mc.menuItem(label='Add to shelf', 
            command='import ml_utilities;ml_utilities.createShelfButton("import '+module+';'+module+'.ui()", name="'+self.name+'", description="Open the UI for '+self.name+'."'+argString+')')
        if not self.icon:
            mc.menuItem(label='Get Icon',
                command=(_showHelpCommand(websiteURL+'/wp-content/files/'+self.name+'.png')))
        mc.menuItem(label='Get More Tools!', 
            command=(_showHelpCommand(websiteURL+'/downloads')))
        mc.setParent( '..', menu=True )

        mc.menu(label='Help')
        mc.menuItem(label='About', command=self.about)
        mc.menuItem(label='Documentation', command=(_showHelpCommand(wikiURL+'#'+self.name)))
        mc.menuItem(label='Python Command Documentation', command=(_showHelpCommand(wikiURL+'#\%5B\%5B'+self.name+'\%20Python\%20Documentation\%5D\%5D')))
        mc.menuItem(label='Submit a Bug or Request', command=(_showHelpCommand(websiteURL+'/downloads/feedback-and-bug-reports/?1ex_field1='+self.name)))
        
        mc.setParent( '..', menu=True )
       
       
    def about(self, *args):
        '''
        This pops up a window which shows the revision number of the current script.
        '''
        
        text='by Morgan Loomis\n\n'
        try:
            __import__(self.module)
            module = sys.modules[self.module]
            text = text+'Revision: '+str(module.__revision__)+'\n'
        except StandardError:
            pass
        try:
            text = text+'ml_utilities Rev: '+str(__revision__)+'\n'
        except StandardError:
            pass
        
        mc.confirmDialog(title=self.name, message=text, button='Close')
    
    
    def buttonWithPopup(self, label=None, command=None, annotation='', shelfLabel='', shelfIcon='render_useBackground', readUI_toArgs=dict()):
        '''
        Create a button and attach a popup menu to a control with options to create a shelf button or a hotkey.
        The argCommand should return a kwargs dictionary that can be used as args for the main command.
        '''
        
        if self.icon:
            shelfIcon = self.icon
        
        if annotation and not annotation.endswith('.'):
            annotation+='.'
        
        button = mc.button(label=label, command=command, annotation=annotation+' Or right click for more options.')
        
        mc.popupMenu()
        self.shelfMenuItem(command=command, annotation=annotation, shelfLabel=shelfLabel, shelfIcon=shelfIcon)
        self.hotkeyMenuItem(command=command, annotation=annotation)
        return button
        

    def shelfMenuItem(self, command=None, annotation='', shelfLabel='', shelfIcon='menuIconConstraints', menuLabel='Create Shelf Button'):
        '''
        This creates a menuItem that can be attached to a control to create a shelf menu with the given command
        '''
        pythonCommand = 'import '+self.name+';'+self.name+'.'+command.__name__+'()'
        
        mc.menuItem(label=menuLabel,
                    command='import ml_utilities;ml_utilities.createShelfButton(\"'+pythonCommand+'\", \"'+shelfLabel+'\", \"'+self.name+'\", description=\"'+annotation+'\", image=\"'+shelfIcon+'\")',
                    enableCommandRepeat=True,
                    image=shelfIcon)

    
    def hotkeyMenuItem(self, command=None, annotation='', menuLabel='Create Hotkey'):
        '''
        This creates a menuItem that can be attached to a control to create a hotkey with the given command
        '''
        melCommand = 'python(\\\"import '+self.name+';'+self.name+'.'+command.__name__+'()'+'\\\");'
        mc.menuItem(label=menuLabel,
                    command='import ml_utilities;ml_utilities.createHotkey(\"'+melCommand+'\", \"'+self.name+'\", description=\"'+annotation+'\")',
                    enableCommandRepeat=True,
                    image='commandButton')
    
    
    class ButtonWithPopup():
        
        def __init__(self, label=None, name=None, command=None, annotation='', shelfLabel='', shelfIcon='render_useBackground', readUI_toArgs=dict(), **kwargs):
            '''
            The fancy part of this object is the readUI_toArgs argument.
            '''
            
            self.uiArgDict = readUI_toArgs
            self.name = name
            self.command = command
            self.kwargs = kwargs
            
            self.annotation = annotation
            self.shelfLabel = shelfLabel
            self.shelfIcon = shelfIcon

            if annotation and not annotation.endswith('.'):
                annotation+='.'

            button = mc.button(label=label, command=self.runCommand, annotation=annotation+' Or right click for more options.')

            mc.popupMenu()
            mc.menuItem(label='Create Shelf Button', command=self.createShelfButton, image=shelfIcon)

            mc.menuItem(label='Create Hotkey',
                        command=self.createHotkey, image='commandButton') 

        
        def readUI(self):
            '''
            This reads the UI elements and turns them into arguments saved in a kwargs style member variable
            '''
            
            if self.uiArgDict:
                #this is some fanciness to read the values of UI elements and generate or run the resulting command
                #keys represent the argument names, the values are UI elements
                
                for k in self.uiArgDict.keys():
                    
                    uiType = mc.objectTypeUI(self.uiArgDict[k])
                    value = None
                    if uiType == 'rowGroupLayout':
                        controls = mc.layout(self.uiArgDict[k], query=True, childArray=True)
                        if 'check1' in controls:
                            value = mc.checkBoxGrp(self.uiArgDict[k], query=True, value1=True)
                        elif 'radio1' in controls:
                            buttonNumber = mc.radioButtonGrp(self.uiArgDict[k], query=True, select=True)
                            #there should be a control for the label and each the buttons..I hope
                            labels = mc.radioButtonGrp(self.uiArgDict[k], query=True, **{'labelArray'+str(len(controls)-1):True})
                            value = labels[buttonNumber-1]
                    else:
                        OpenMaya.MGlobal.displayWarning('Cannot read '+uiType+' UI element: '+self.uiArgDict[k])
                        continue
                    
                    self.kwargs[k] = value
        
        
        def runCommand(self, *args):
            '''
            This compiles the kwargs and runs the command directly
            '''
            self.readUI()
            self.command(**self.kwargs)
            

        def stringCommand(self):
            '''
            This takes the command
            '''
            
            cmd = 'import '+self.name+';'+self.name+'.'+self.command.__name__+'('
            
            comma = False
            for k,v in self.kwargs.items():
                
                value = v
                if isinstance(v, str):
                    value = "'"+value+"'"
                elif v is True:
                    value = 'True'
                elif v is False:
                    value = 'False'
                elif not v:
                    value = 'None'
                
                if comma:
                    cmd+=', '
                cmd = cmd+k+'='+value
                
                comma = True
                
            cmd+=')'
            
            return cmd


        def createShelfButton(self,*args):
            '''
            Builds the command and creates a shelf button out of it
            '''
            self.readUI()
            pythonCommand = self.stringCommand()
            createShelfButton(pythonCommand, self.shelfLabel, self.name, description=self.annotation, image=self.shelfIcon)


        def createHotkey(self, annotation='', menuLabel='Create Hotkey'):
            '''
            Builds the command and prompts to create a hotkey.
            '''
            
            self.readUI()
            pythonCommand = self.stringCommand()
            melCommand = 'python("'+pythonCommand+'");'
            createHotkey(melCommand, self.name, description=self.annotation)

    
class SkipUndo():
    '''
    Skips adding the encapsulated commands to the undo queue, so that you 
    cannot undo them.
    '''
    
    def __enter__(self):
        '''
        Turn off undo
        '''
        mc.undoInfo(stateWithoutFlush=False)
        
    def __exit__(self,*args):
        '''
        Turn on undo
        '''
        mc.undoInfo(stateWithoutFlush=True)
        
        
class UndoChunk():
    '''
    In versions of maya before 2011, python doesn't always undo properly, so in 
    some cases we have to manage the undo queue ourselves.
    '''
    
    def __init__(self, force=False):
        self.force = force
        
    def __enter__(self):
        '''open the undo chunk'''
        if self.force or mm.eval('getApplicationVersionAsFloat') < 2011:
            self.force = True
            mc.undoInfo(openChunk=True)
            
    def __exit__(self, *args):
        '''close the undo chunk'''
        if self.force:
            mc.undoInfo(closeChunk=True)

    

if __name__ == '__main__':
    main()
    


#      ______________________
# - -/__ Revision History __/- - - - - - - - - - - - - - - - - - - - - - - - 
#
# Revision 1: : First publish
#
# Revision 2: 2011-05-04 : Fixed error in frameRange.
#
# Revision 3: 2012-05-31 : Adding Menu and Icon update to UI, adding KeyframeSelection object, and a few random utility functions.
#
# Revision 4: 2012-06-01 : Fixing bug with UI icons
#
# Revision 5: 2012-07-23 : Expanding and bug fixing Keyselection, added SkipUndo, minor bug fixes.
#
# Revision 6: 2012-07-23 : KeySelection bug fix
#
# Revision 7: 2012-08-07 : Minor bug with Keyselection, adding functions.
