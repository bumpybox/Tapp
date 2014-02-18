'''
================================================================================
dslSculptInbetweenEditor.py - Python Script
================================================================================


by Daniel S. Lima
www.danielslima.com

This tool is a collection of influences and personal desire to have this 
functionality inside Maya since Autodesk never provided it so far. Pose 
Space Deformation allows the user to SCULPT on POSE, this method has implemented 
in many other softwares packaged before and also presented on papers by 
J.P. Lewis, Matt Cordner and Nickson Fong in 2000 Article. I give all the 
credits for these authors for these particular influence.


ACM Digital Library
http://dl.acm.org/citation.cfm?id=344862
 
daniel3d@gmail.com

*** MODIFY THIS AT YOUR OWN RISK ***

DESCRIPTION: 
    UI TO MANAGE IBETWEENS AND CORRECTIVES DELTAS AND CALCULATE PSD WITH NO 
    USAGE OF ANY PLUGIN.

NOTES:
   
   NEXT VERSION:
        - update code to Maya API 2.0
        - Better support for combos
        - Mirror Corrective Weights
        - Nurbs Support
    
    LIMITATIONS:
        - If it's in sculpt mode addInbetween from another geometry does not work
        - After addInbetween the undo does not "delete" the respective position 
          from the ui but only the deltas, the user must delete the position 
          manually later
        - ( Warning during the usage of "interactive Mode" ) In interactive mode, 
          if the upper inbetween position getting moved crossing the lower 
          inbetween position this will result in deleting the delta of this 
          crossed ibetween. After refresh the UI this inbetween will no longer
          exist. Undo to perform the restoration works.
        - Polygons only
          
    
REQUIRES:
    dslReverseShape.py - For PSD calculation
    dslDeltaOptions.py - For All functions that manage the deltas
    Maya BlendShape Node
    Maya SkinCluster Node or Third Party linear SkinCluster

USAGE:
    Select any geometry that contains a blendShape or create a new blendShape 
    node through the dslTweenFix UI


DATE: OUT/2011
RELEASE DATE: 03/24/13
LAST UPDATE: 03/18/2013
VERSION: 1.0
MAYA: 2010 ABOVE

'''

from functools import partial

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.mel as mm
import dslReverseShape as dslRs
import dslDeltaOptions as dslDo
import webbrowser
import time
import sys
import re
reload(dslDo)
reload(dslRs)

#===============================================================================
# GLOBAL VARIABLES
#===============================================================================

undoState = None
crData = None
globalMirrorSubList = None
previousMirrorPlane = None
previousTolerance = None

# To be used with Delta Tools // Select Button from "Apply to" SubMenu
originalPointIndex = None

#===============================================================================

class SculptInbetweenEditor():
    
    def __init__(self):
        self.winName = str('Sculpt Inbetween Editor \a v1.0 \a\
                            danielSlima.com')
        self.displayInfo = 'Sculpt Inbetween Editor v1.00 by Daniel S. Lima 2013'
        self.offsetRestore = [0, 0, -2]
        self.size = [660, 750]
    
    def ui(self):
       
        # UI Creation
        if cmds.window('dsl_Sculpt_Inbetween_Editor', title=self.winName, ex=True):
            #cmds.window('dsl_Sculpt_Inbetween_Editor', title=self.winName, e=True, wh=self.size)
            cmds.showWindow('dsl_Sculpt_Inbetween_Editor')
      
        else:
            om.MGlobal.displayInfo(self.displayInfo)
            cmds.window('dsl_Sculpt_Inbetween_Editor', title=self.winName,
                        menuBar=True,
                        wh=self.size,
                        retain=True,
                        sizeable=True)
            cmds.menu(label='Options')
            cmds.menuItem(label='Reset',
                          c=partial(self.barMenuOptions, 1))
            #cmds.menuItem(label='Help',
            #            c=partial(self.barMenuOptions, 2))
            cmds.menuItem(divider=True)
            cmds.menuItem(label='Quit', c=partial(self.barMenuOptions, 3))
            
            cmds.menu(label='Help')
            cmds.menuItem(label='Documentation',
                          c=partial(self.barMenuOptions, 2))
            cmds.menuItem(label='About',
                          c=partial(self.barMenuOptions, 4))
            '''
            cmds.menu(label='Tools')
            cmds.menuItem(label='Check symmetry',
                          c=partial(self.barMenuOptionsTools, 1))
            '''
            
            #===================================================================
            # UI FORMS, BUTTONS, LAYOUTS...
            #===================================================================
            mainForm = cmds.formLayout()
            blendNodeFormLayout = cmds.formLayout(parent=mainForm)
            separatorTop = cmds.separator(style='in', parent=mainForm)
            selectRefreshButton = cmds.button(label='Refresh Select', width=145,
                                              c=partial(self.listBlendShapeNode, True))
            self.optionMenuGrpBlend = cmds.optionMenu(width=350,
                                                      parent=blendNodeFormLayout,
                                                      cc=self.refreshCrAndInbetweenList)
            
            cmds.popupMenu('popupSelectNode', parent=blendNodeFormLayout)
            cmds.menuItem(label='Select Node', parent='popupSelectNode',
                          c=self.popupBlendShapeSelect)
            
          
            #===================================================================
            # BLENDSHAPE NODES
            #===================================================================
            self.listBlendShapeNode()
            #===================================================================
          
            self.createBlendShapeNode = cmds.button(label='Create BlendShape',
                                                    c=self.addBlendShapeDef,
                                                    width=85)
            separatorTopB = cmds.separator(style='in', parent=mainForm)
            
            ######################## BASE MAIN LAYOUT ##########################
            self.mainPanelLayout = cmds.paneLayout(configuration='vertical2',
                                                   paneSize=[(1, 1, 0)],
                                                   st=5,
                                                   swp=1,
                                                   parent=mainForm)
            ####################################################################
            
            crFormLayout = cmds.formLayout(width=230, parent=self.mainPanelLayout)
            inbetweenFormLayout = cmds.formLayout(width=150, parent=self.mainPanelLayout)
            buttonCreateNewCr = cmds.button(label='New Corrective',
                                            parent=crFormLayout,
                                            c=self.addCorrective)
            self.scrollCrList = cmds.textScrollList(height=5,
                                                    allowMultiSelection=True,
                                                    dcc=self.renameCorrective,
                                                    sc=partial(self.listInbetween,
                                                               interactiveMode=True,
                                                               correctiveName=False,
                                                               resetDeltaTools=True),
                                                               parent=crFormLayout)
            #===================================================================
            # CORRECTIVE LIST
            #===================================================================
            blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                             q=True,
                                             value=True)
            try:
                gatherInfoFrom = '.weight'
                listAttrPath = str(blendShapeNode) + str(gatherInfoFrom)
                listCorrective = cmds.listAttr(listAttrPath, multi=True)
                #listCorrective = list(sorted(set(listCorrective)))
                listCorrective = sorted(listCorrective)
            except:
                listCorrective = ['None']
                pass
            
            cmds.textScrollList(self.scrollCrList, e=True, ra=True)
            cmds.textScrollList(self.scrollCrList,
                                e=True,
                                a=listCorrective,
                                si=listCorrective[0])
            #===================================================================
            def checkBoxDependecy(args):
                if cmds.checkBox(self.checkActivated, q=True, value=True) == True:
                    cmds.checkBox(self.checkNegValues, e=True, en=True)
                    self.listCorrective()
                else:
                    cmds.checkBox(self.checkNegValues, e=True, en=False)
                    self.listCorrective()
            
            self.checkActivated = cmds.checkBox(label='Activated List',
                                                align='center',
                                                h=30,
                                                onc=partial(checkBoxDependecy),
                                                ofc=partial(checkBoxDependecy),
                                                parent=crFormLayout)
            self.checkNegValues = cmds.checkBox(label='Negative Values',
                                                align='center',
                                                h=30,
                                                onc=partial(self.listCorrective, None),
                                                ofc=partial(self.listCorrective, None),
                                                en=False,
                                                parent=crFormLayout)
          
            self.filterField = cmds.textFieldGrp(label='Filter: ',
                                                 columnWidth=[(1,35), (2,35)],
                                                 adjustableColumn2=2,
                                                 cc=partial(self.listCorrective, None),
                                                 #cc=partial(self.refreshCrAndInbetweenList),
                                                 parent=crFormLayout)
            self.buttonRefresh = cmds.button('refreshButton', 
                                             label='Refresh',
                                             c=partial(self.listCorrective, None), 
                                             parent=crFormLayout)
            self.popupMenuCr(parentTo=self.scrollCrList) ## POP UP MENU CR
            buttonRefreshInbetween = cmds.button(label='Re-Order / Refresh List',
                                                 width=150,
                                                 c=self.listInbetween,
                                                 parent=inbetweenFormLayout)
            self.scrollInbetweenList = cmds.scrollLayout(height=5,
                                                         childResizable=True,
                                                         horizontalScrollBarThickness=16,
                                                         parent=inbetweenFormLayout)
            self.checkInteractive = cmds.checkBox(label='   Interactive Mode ',
                                                  onCommand=partial(self.listInbetween,
                                                                    interactiveMode=True),
                                                  offCommand=partial(self.listInbetween,
                                                                     interactiveMode=False),
                                                  parent=inbetweenFormLayout)
            separatorInbOut = cmds.separator(style='in', parent=inbetweenFormLayout)
            textTypeRowLayout = cmds.rowLayout(numberOfColumns=5,
                                               adjustableColumn5=3,
                                               columnOffset5=[0,0,30,0,20],
                                               columnWidth5=[40,35,100,35,15],
                                               columnAlign5=['center',
                                                             'center',
                                                             'center',
                                                             'left',
                                                             'left'],
                                               parent=inbetweenFormLayout)
          
            cmds.text(label='Item', parent=textTypeRowLayout)
            cmds.text(label='Value', parent=textTypeRowLayout)
            cmds.text(label=' ', parent=textTypeRowLayout)
            cmds.text(label='Geo', parent=textTypeRowLayout)
            cmds.text(label='        ', parent=textTypeRowLayout)
          
            #===================================================================
            # ADDING IBETEWEENS SLIDERS
            #===================================================================
            self.listInbetween(parent=self.scrollInbetweenList)
            #===================================================================
          
            separatorBottom = cmds.separator(style='in', parent=mainForm)
            tabForm = cmds.formLayout (height=180, parent=mainForm)
            self.optionTabs = cmds.tabLayout(innerMarginWidth=5, 
                                             innerMarginHeight=5,
                                             parent=tabForm)
            
            self.addShapeColumnLayout = cmds.columnLayout('Add In-between',
                                                          columnAttach=('both', 1), 
                                                          rowSpacing=0,
                                                          adjustableColumn=True,
                                                          parent = self.optionTabs)
            firstFormLayout = cmds.formLayout(height = 40,
                                              bgc=[0.35, 0.35, 0.35])
            self.keepS = cmds.checkBox('checkBoxKeepSculpt', label=' Keep Sculpt Geometry ', 
                                   value=False, parent=firstFormLayout)
            #===================================================================
            # bCopyPose = cmds.button(label='Copy Pose', width = 415, 
            #                        c=partial(self.copyPose),
            #                         bgc=[0.23,0.33,0.39], 
            #                        parent=firstFormLayout)
            #===================================================================
            bCopyPose = cmds.button(label='Copy Pose', width = 120, 
                                    c=partial(self.copyPose),
                                     bgc=[0.23,0.33,0.39], 
                                    parent=firstFormLayout)
            
            def createSculptState(args):
                sculptModeSt = cmds.iconTextCheckBox(self.bCreateScultGeo, q=True, value=True)
                labelSt = cmds.iconTextCheckBox(self.bCreateScultGeo, q=True, label=True)
                colorSt = cmds.iconTextCheckBox(self.bCreateScultGeo, q=True, bgc=True)
                
                colorOn = [0.0,1.0,0.0]
                colorOff = [0.9,0.12,0.13]
                
                if sculptModeSt == True:
                    cmds.iconTextCheckBox(self.bCreateScultGeo, e=True, label='Sculpt ON')
                    cmds.iconTextCheckBox(self.bCreateScultGeo, e=True, bgc=colorOn)
                    
                    cmds.button(pSwitchGeo, e=True, enable=True)
                    cmds.button(pBothGeo, e=True, enable=True)
                    cmds.button(pResetSculpt, e=True, enable=True)
                    
                    self.createSculptGeo(self)
                else:
                    cmds.iconTextCheckBox(self.bCreateScultGeo, e=True, label='Sculpt OFF')
                    cmds.iconTextCheckBox(self.bCreateScultGeo, e=True, bgc=colorOff)
                    
                    cmds.button(pSwitchGeo, e=True, enable=False)
                    cmds.button(pBothGeo, e=True, enable=False)
                    cmds.button(pResetSculpt, e=True, enable=False)
                    
                    self.deleteSculptGeo(self)
                
                
                #print 'sculptModeSt: ',sculptModeSt
                #print 'labelSt: ',labelSt
                #print 'colorSt: ',colorSt
                
            self.bCreateScultGeo = cmds.iconTextCheckBox('createSculptGeo', 
                                                    label='Sculpt OFF',
                                                    style='textOnly',
                                                    bgc=[0.9,0.12,0.13],
                                                    width = 115,
                                                    cc=createSculptState,
                                                    parent=firstFormLayout)
            
            
            pSwitchGeo = cmds.button(label='Switch',
                                     w=42,
                                     enable=False,
                                     c=partial(self.switchBetween),
                                     parent=firstFormLayout)
            pBothGeo = cmds.button(label='Both',
                                   w=43,
                                   enable=False,
                                   c=partial(self.switchBetween, True),
                                   parent=firstFormLayout)
            pResetSculpt = cmds.button(label='Reset',
                                       w=50,
                                       enable=False,
                                       c=self.resetSculpt,
                                       parent=firstFormLayout)
            
            cmds.formLayout(firstFormLayout, e=True, af=[(self.keepS, 'left', 35),
                                                         (self.keepS, 'top', 8),
                                                         (self.keepS, 'bottom', 8),
                                                         (bCopyPose, 'top', 8),
                                                         (bCopyPose, 'bottom', 8),
                                                         (self.bCreateScultGeo, 'top', 8),
                                                         (self.bCreateScultGeo, 'bottom', 8),
                                                         #(self.bCreateScultGeo, 'right', 30),
                                                         (pSwitchGeo, 'top', 8),
                                                         (pSwitchGeo, 'bottom', 8),
                                                         (pBothGeo, 'top', 8),
                                                         (pBothGeo, 'bottom', 8),
                                                         (pResetSculpt, 'top', 8),
                                                         (pResetSculpt, 'bottom', 8),
                                                         (pResetSculpt, 'left', 30)],
                                                      ac=[(bCopyPose, 'left',
                                                           15, self.keepS),
                                                          (self.bCreateScultGeo, 'left',
                                                           30, bCopyPose),
                                                          
                                                          (pSwitchGeo, 'left',
                                                           5, self.bCreateScultGeo),
                                                          
                                                          (pBothGeo, 'left',
                                                           5, pSwitchGeo),
                                                          
                                                          (pResetSculpt, 'left',
                                                           5, pBothGeo)])
            #===================================================================
            # FORMS FROM TAB LAYOUT
            #===================================================================
            self.addShapeFormLayout = cmds.formLayout(height = 110,
                                                      parent=self.addShapeColumnLayout)
            #===================================================================
            # ADD IN-BETWEEN - ON
            #===================================================================
            addButton1 = cmds.iconTextButton('addInbetween',
                                             style='iconAndTextVertical',
                                             image1='dslCmBasicInbetween.xpm',
                                             label='Inbetween-R',
                                             c=partial(self.addShape, mode='Inbetween'),
                                             parent=self.addShapeFormLayout)
            addButton2 = cmds.iconTextButton('addProjection',
                                             style='iconAndTextVertical',
                                             image1='dslCmProjection.xpm',
                                             c=partial(self.addShape, mode='Projection'),
                                             label='Projection-R',
                                             parent=self.addShapeFormLayout)
            addButton3 = cmds.iconTextButton('addFlatten',
                                             style='iconAndTextVertical',
                                             image1='dslCmFlatten.xpm',
                                             c=partial(self.addShape, mode='Flatten'),
                                             label='Flatten-R',
                                             parent=self.addShapeFormLayout)
            addButton4 = cmds.iconTextButton('abbBasic',
                                             style='iconAndTextVertical',
                                             image1='dslCmBasic.xpm',
                                             c=partial(self.addShape, mode='Basic'),
                                             label='Basic',
                                             parent=self.addShapeFormLayout)
            cmds.formLayout(self.addShapeFormLayout, e=True, af=[(addButton1, 'left', 35),
                                                                 (addButton1, 'top', 15),
                                                                 (addButton1, 'bottom', 10),
                                                                 (addButton2, 'top', 15),
                                                                 (addButton2, 'bottom', 10),
                                                                 (addButton3, 'top', 15),
                                                                 (addButton3, 'bottom', 10),
                                                                 (addButton4, 'top', 15),
                                                                 (addButton4, 'bottom', 10)],
                                                             ac=[(addButton2, 'left',
                                                                  25, addButton1),
                                                                 (addButton3, 'left',
                                                                  25, addButton2),
                                                                 (addButton4, 'left',
                                                                  25, addButton3)])

            #===================================================================
            # MIRROR DATA - ON
            #===================================================================
            def textMirrorChange(axis):
                if cmds.radioButtonGrp('radioGroup', q=True, select=True) == 1:
                    posToNeg = cmds.checkBox(checkBoxDirection, q=True, value=True)
                    cmds.checkBox('checkBox', 
                                  e=True, 
                                  label=' Positive to negative ( +Z to -Z ) ')
                    '''
                    cmds.button(buttonMirrorData, 
                                e=True, 
                                c=partial(self.mirrorCrIndices, False, 'XY', posToNeg))
                    cmds.button(buttonFlipData, 
                                e=True, 
                                c=partial(self.mirrorCrIndices, True, 'XY', posToNeg))
                    '''
                    cmds.radioButtonGrp('radioGrpPlaneSel', 
                                        e=True, 
                                        select=1)
                    cmds.radioButtonGrp('radioGrpSideSel', 
                                        e=True,
                                        labelArray4=['Z Pos', 'Z Neg', ' All', 'User'])
                elif cmds.radioButtonGrp('radioGroup', q=True, select=True) == 2:
                    posToNeg = cmds.checkBox(checkBoxDirection, 
                                             q=True, 
                                             value=True)
                    cmds.checkBox('checkBox', 
                                  e=True, 
                                  label=' Positive to negative ( +X to -X ) ')
                    '''
                    cmds.button(buttonMirrorData, 
                                e=True, 
                                c=partial(self.mirrorCrIndices, 
                                          False, 
                                          'YZ', 
                                          posToNeg))
                    cmds.button(buttonFlipData, 
                                e=True, 
                                c=partial(self.mirrorCrIndices, 
                                          True, 
                                          'YZ', 
                                          posToNeg))
                    '''
                    cmds.radioButtonGrp('radioGrpPlaneSel', 
                                        e=True, select=2)
                    cmds.radioButtonGrp('radioGrpSideSel', 
                                        e=True,
                                        labelArray4=['X Pos', 'X Neg', ' All', 'User'])
                else:
                    posToNeg = cmds.checkBox(checkBoxDirection, 
                                             q=True, 
                                             value=True)
                    cmds.checkBox('checkBox', 
                                  e=True, 
                                  label=' Positive to negative ( +Y to -Y ) ')
                    '''
                    cmds.button(buttonMirrorData, 
                                e=True, 
                                c=partial(self.mirrorCrIndices, 
                                          False, 
                                          'XZ', 
                                          posToNeg))
                    cmds.button(buttonFlipData, 
                                e=True, 
                                c=partial(self.mirrorCrIndices, 
                                          True, 
                                          'XZ', 
                                          posToNeg))
                    '''
                    cmds.radioButtonGrp('radioGrpPlaneSel', 
                                        e=True, 
                                        select=3)
                    cmds.radioButtonGrp('radioGrpSideSel', 
                                        e=True,
                                        labelArray4=['Y Pos', 'Y Neg', ' All', 'User'])
            #===================================================================       
            def textDataTypeChange(type):
                if cmds.radioButtonGrp('radioGrpDataOption', q=True, select=True) == 1:
                    cmds.button(buttonMirrorData, e=True, label=' Mirror Delta ')
                    cmds.button(buttonFlipData, e=True, label=' Flip Delta ')
                    cmds.button(buttonCopyData, e=True, label=' Copy Delta ')
                    cmds.button(buttonCopyData, e=True, enable=True)
                    cmds.formLayout('fieldApply', e=True, enable=True)
                    
                if cmds.radioButtonGrp('radioGrpDataOption', q=True, select=True) == 2:
                    cmds.button(buttonMirrorData, e=True, label=' Mirror Weights ')
                    cmds.button(buttonFlipData, e=True, label=' Flip Weights ')
                    cmds.button(buttonCopyData, e=True, label=' Copy Weights ')
                    cmds.button(buttonCopyData, e=True, enable=True)
                    cmds.formLayout('fieldApply', e=True, enable=True)
                    
                if cmds.radioButtonGrp('radioGrpDataOption', q=True, select=True) == 3:
                    cmds.button(buttonMirrorData, e=True, label=' Mirror Weights ')
                    cmds.button(buttonFlipData, e=True, label=' Flip Weights ')
                    cmds.button(buttonCopyData, e=True, label=' Copy Weights ')
                    cmds.button(buttonCopyData, e=True, enable=False)
                    cmds.formLayout('fieldApply', e=True, enable=False)
            #=================================================================== 
            def uiChangefromToClear(button, arg=None):
                #print 'def uiChangefromToClear'
                correctiveSelected = cmds.textScrollList(self.scrollCrList,
                                                     q=True,
                                                     si=True)[0]
                if button == 'fromSelect':
                    cmds.textFieldButtonGrp('fromCr', e=True, text=correctiveSelected)
                    
                elif button == 'toSelect':
                    cmds.textFieldButtonGrp('toCr', e=True, text=correctiveSelected)
                    
                elif button == 'clearSelect':
                    cmds.textFieldButtonGrp('fromCr', e=True, text='')
                    cmds.textFieldButtonGrp('toCr', e=True, text='')
                elif button == 'selectBase':
                    selectGeo = cmds.ls(sl=True)
                    if selectGeo:
                        cmds.textFieldButtonGrp('BaseGeo', e=True, text=selectGeo[0])
                    else:
                        om.MGlobal.displayInfo('Select Symmetrical Base Geometry')
                
                # Enable Copy Data to User depending if have From and To with something
                if (cmds.textFieldButtonGrp(fieldFrom, q=True, text=True) != 
                    cmds.textFieldButtonGrp(fieldTo, q=True, text=True)):
                    if (cmds.textFieldButtonGrp(fieldFrom, q=True, text=True) == '' or 
                        cmds.textFieldButtonGrp(fieldTo, q=True, text=True) == ''):
                            cmds.button(buttonCopyData, e=True, enable=False)
                    else:
                        cmds.button(buttonCopyData, e=True, enable=True)
                else:
                    cmds.button(buttonCopyData, e=True, enable=False)
                    
                       
            self.mirrorData = cmds.rowLayout('Mirror Data',
                                              numberOfColumns=2, 
                                              columnWidth2=(280, 340), 
                                              height=50,
                                              adjustableColumn=2, 
                                              columnAlign=(1, 'right'), 
                                              columnAttach=[(1, 'both', 2), 
                                                            (2, 'both', 2),
                                                            #(3, 'both', 2), 
                                                            ],
                                              parent=self.optionTabs)
            
            #cmds.frameLayout( 'dataOptionFrame', label='Data Option', borderStyle='in', 
            #                  height=145, parent=self.mirrorData )
            cmds.frameLayout('mirrorPlane', 
                             label='Mirror Options', 
                             borderStyle='in', 
                             height=145, 
                             parent=self.mirrorData )
            self.mirrorShapeFormLayout = cmds.formLayout('mirrorData', 
                                                         parent='mirrorPlane')
            cmds.frameLayout('applyFrameData', 
                             label='Apply', 
                             borderStyle='in', 
                             height=145, 
                             parent=self.mirrorData )
            radioGroupMirrorPlanes = cmds.radioButtonGrp('radioGroup', 
                                                         label='Mirror across: ', 
                                                         labelArray3=['XY', 'YZ', 'XZ'],
                                                         numberOfRadioButtons=3,
                                                         columnWidth4 = [70,60,60,60],
                                                         select=2,
                                                         cc=textMirrorChange,
                                                         parent=self.mirrorShapeFormLayout)
            
            textMirrorPlane = cmds.text(label='Direction:', 
                                        parent=self.mirrorShapeFormLayout)
            checkBoxDirection = cmds.checkBox('checkBox', 
                                              label=' Positive to negative ( +X to -X ) ', 
                                              value=True, cc=textMirrorChange, 
                                              parent=self.mirrorShapeFormLayout)
            
            cmds.separator('separatorMPlane', 
                           st='in',
                           parent=self.mirrorShapeFormLayout)
            
            cmds.radioButtonGrp('radioGrpDataOption', 
                                labelArray3=['Delta', 'crWeight', 'bsWeight'],
                                numberOfRadioButtons=3,
                                columnWidth3 = [75, 75, 75],
                                select=1,
                                enable=False,
                                cc=textDataTypeChange,
                                parent=self.mirrorShapeFormLayout)
            
            cmds.formLayout(self.mirrorShapeFormLayout, 
                            e=True, 
                            af=[(radioGroupMirrorPlanes, 'left', 20),
                                (radioGroupMirrorPlanes, 'top', 10),
                                (textMirrorPlane, 'left', 20),
                                ('separatorMPlane', 'left', 20),
                                ('separatorMPlane', 'right', 20),
                                ('radioGrpDataOption', 'left', 20),
                                ('radioGrpDataOption', 'right', 20),
                                ('radioGrpDataOption', 'bottom', 20),
                                ],
                            ac=[(textMirrorPlane, 'top', 11, radioGroupMirrorPlanes),
                                (checkBoxDirection, 'top', 10, radioGroupMirrorPlanes),
                                (checkBoxDirection, 'left', 8, textMirrorPlane),
                                ('separatorMPlane', 'top', 15, textMirrorPlane)
                                ])
            
            
            colorBgc = 0.25
            cmds.rowLayout('actionRow',
                           numberOfColumns=2, 
                           columnWidth2=(250, 100), 
                           height=120,
                           adjustableColumn=1, 
                           columnAlign=(1, 'right'), 
                           columnAttach=[(1, 'both', 2), 
                                         (2, 'both', 2),
                                         ],
                           parent='applyFrameData')
            
            cmds.formLayout('fieldApply', 
                            height=110,
                            parent='actionRow')
            cmds.formLayout('fieldApplyTo', 
                            bgc=[0.35, 0.35, 0.35],
                            height=110,
                            ebg=True,
                            parent='actionRow')
            
            fieldFrom = cmds.textFieldButtonGrp('fromCr', label='From: ', 
                                                #text='Selected',
                                                #height=20,
                                                editable=True,
                                                buttonLabel='Select',
                                                cw3=[35,100,25],
                                                adj=2,
                                                bc=partial(uiChangefromToClear, 'fromSelect'),
                                                parent='fieldApply')
            fieldTo = cmds.textFieldButtonGrp('toCr', label='To: ', 
                                              #text='Selected',
                                              editable=True,
                                              buttonLabel='Select',
                                              cw3=[35,100,25],
                                              adj=2,
                                              bc=partial(uiChangefromToClear, 'toSelect'),
                                              parent='fieldApply')
            fieldBase = cmds.textFieldButtonGrp('BaseGeo', label='Base: ', 
                                                #text='Automatic',
                                                en=False,
                                                editable=True,
                                                buttonLabel='Select',
                                                cw3=[30,20,20],
                                                adj=2,
                                                bc=partial(uiChangefromToClear, 'selectBase'),
                                                ann='Add Symmetrical Base Geometry',
                                                parent='fieldApply')
            
            
            
            buttonClear = cmds.button('Clear Selection', 
                                      #width=110, 
                                      bgc=[colorBgc, colorBgc, colorBgc],
                                      c=partial(uiChangefromToClear, 'clearSelect'),
                                      parent='fieldApply',
                                      #c=partial(self.mirrorDataActionUi)
                                      )
            toleranceText = cmds.text('TolText', label='Tolerance',parent='fieldApply')
            toleranceFactor = cmds.floatField('tolField', 
                                              value=0.00001, 
                                              minValue=0.00001,
                                              maxValue=0.9,
                                              precision=5,
                                              step=.00001,
                                              parent='fieldApply')
            
            buttonMirrorData = cmds.button(' Mirror Delta ', 
                                           label=' Mirror Delta ',
                                           #width=110, 
                                           #bgc=[colorBgc, colorBgc, colorBgc],
                                           parent='fieldApplyTo',
                                           c=partial(self.applyMirrorOptionData, flipModel=False)
                                           )
            buttonFlipData = cmds.button(' Flip Delta ', 
                                         label=' Flip Delta ',
                                         #width=110,
                                         parent='fieldApplyTo',
                                         #c=partial(self.mirrorCrIndices, True, 'YZ', True))
                                         c=partial(self.applyMirrorOptionData, flipModel=True)
                                         )
            buttonCopyData = cmds.button(' Copy Delta ', 
                                         parent='fieldApplyTo',
                                         bgc=[colorBgc, colorBgc, colorBgc],
                                         enable=False,
                                         #bgc=[0.68, 0.88, 0.68],
                                         c=partial(self.applyMirrorOptionData, copyMode=True),
                                         )
            
            editWeights = cmds.button(' Paint Weights ', 
                                      parent='fieldApplyTo',
                                      bgc=[0.58, 0.58, 0.28],
                                      enable=False,
                                      c=partial(self.applyMirrorOptionData),
                                      )
             
            cmds.formLayout('fieldApply', 
                            e=True, 
                            af=[('fromCr', 'left', 0),
                                ('fromCr', 'top', 0),
                                ('fromCr', 'right', 5),
                                ('toCr', 'left', 0),
                                ('toCr', 'right', 5),
                                (buttonClear, 'right', 10),
                                (toleranceText, 'left', 5),
                                ('BaseGeo', 'right', 5),
                                ('BaseGeo', 'left', 5),
                                ('BaseGeo', 'bottom', 0)
                                ],
                            ac=[
                                ('toCr', 'top', 5, 'fromCr'),
                                (toleranceText, 'top', 9, 'toCr'),
                                (toleranceFactor, 'top', 6, 'toCr'),
                                (toleranceFactor, 'left', 5, toleranceText),
                                (toleranceFactor, 'right', 5, buttonClear),
                                (buttonClear, 'top', 5, 'toCr'),
                                ('BaseGeo', 'top', 8, toleranceText)
                                ])
            
            cmds.formLayout('fieldApplyTo', 
                            e=True, 
                            af=[(buttonMirrorData, 'left', 4),
                                (buttonMirrorData, 'top', 4),
                                (buttonMirrorData, 'right', 4),
                                (buttonFlipData, 'left', 4),
                                (buttonFlipData, 'right', 4),
                                (buttonCopyData, 'left', 4),
                                (buttonCopyData, 'right', 4),
                                (editWeights, 'left', 4),
                                (editWeights, 'right', 4),
                                (editWeights, 'bottom', 4),
                                ],
                            ac=[
                                (buttonFlipData, 'top', 2, buttonMirrorData),
                                (buttonCopyData, 'top', 2, buttonFlipData),
                                (editWeights, 'top', 2, buttonCopyData),
                                ])
            
            
                
            #===================================================================
            # DELTA TOOLS
            #===================================================================
            def deltaToolsActions(args):
                #print 'def deltaToolsActions'

                blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                                 q=True, 
                                                 value=True)

                correctiveName = cmds.textScrollList(self.scrollCrList,
                                                     q=True, 
                                                     si=True)[0]
        
                self.getCrGrpItem()[str(correctiveName)][0]
                #correctiveItem = correctiveItem.split(str(correctiveName))[-1]
                
                # Apply to SubMenu Options
                applyTo = cmds.radioButtonGrp('radioGrpItem', 
                                              q=True, 
                                              select=True)
                # If All is selected...
                #if applyTo == 1:
                #    print 'tmp'
            
            #===================================================================
            def toolAction(mode, factorAdd, args):
                global originalPointIndex
                
                blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                                 q=True, value=True)
                correctiveName = cmds.textScrollList(self.scrollCrList,
                                                     q=True, si=True)[0]
                correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
                
                if cmds.radioButtonGrp('radioGrpItem', q=True, select=True) == 1:
                    correctiveItem = self.listItems(blendShapeNode, 
                                                    correctiveGroup)
                else:
                    correctiveItem = [cmds.intField('itemNumber', 
                                                    q=True, 
                                                    value=True)]
               
                mirrorPlane = cmds.radioButtonGrp('radioGrpPlaneSel',
                                                  q=True, 
                                                  select=True)
                mirrorSide = cmds.radioButtonGrp('radioGrpSideSel', 
                                                 q=True, 
                                                 select=True)
                pruneValue = cmds.floatField('bellowVal', 
                                             q=True, 
                                             value=True)
                factorValue = cmds.floatField('factorValue', 
                                              q=True, 
                                              value=True)
                
                # Open Chunk UNDO
                cmds.undoInfo(openChunk=True)
                
                newOriginalPointIndex = dslDo.combinePointIndex(blendShapeNode, 
                                                                correctiveGroup, 
                                                                correctiveItem[-1])

                if originalPointIndex == None:
                    originalPointIndex = [0]
                if len(originalPointIndex) != len(newOriginalPointIndex):
                    originalPointIndex = dslDo.combinePointIndex(blendShapeNode, 
                                                                 correctiveGroup, 
                                                                 correctiveItem[-1])

                for item in correctiveItem:
                    try:
                        dslDo.deltaTool(blendShapeNode, correctiveGroup, item, 
                                        mirrorPlane, mirrorSide, mode, 
                                        pruneValue, factorValue, factorAdd, 
                                        originalPointIndex, 0.00001)
                    except:
                        print 'There is no vertice selected'

                if mode == 'prune':
                    originalPointIndex = dslDo.combinePointIndex(blendShapeNode, 
                                                                 correctiveGroup, 
                                                                 correctiveItem=item)    
                    self.checkAnalysis(False, args)
                    print 'OriginalPointIdex has been re-created'
                
                # Close Chunk UNDO
                cmds.undoInfo(closeChunk=True)
            #===================================================================
            self.rowOptShape = cmds.rowLayout('Delta Tools',
                                              numberOfColumns=3, 
                                              columnWidth3=(130, 300, 190), 
                                              height=50,
                                              adjustableColumn=2, 
                                              columnAlign=(1, 'right'), 
                                              columnAttach=[(1, 'both', 2), 
                                                            (2, 'both', 2),
                                                            (3, 'both', 2), 
                                                            ],
                                              parent=self.optionTabs)
            
            cmds.frameLayout( 'applyFrameTools', 
                              label='Apply to', 
                              borderStyle='in', 
                              height=145, 
                              parent=self.rowOptShape )
            cmds.frameLayout( 'selectionFrame', 
                              label='Selection Format', 
                              borderStyle='in', 
                              height=145, 
                              parent=self.rowOptShape )
            cmds.frameLayout( 'toolsFrame', 
                              label='Tools', 
                              borderStyle='in', 
                              height=145, 
                              parent=self.rowOptShape )
            #===================================================================
            # APPLY SUB-MENU
            #===================================================================
            
                                          
            cmds.formLayout('formValueFrame', parent='applyFrameTools')
            cmds.radioButtonGrp('radioGrpItem', 
                                labelArray2=['All', 'Item'],
                                numberOfRadioButtons=2,
                                columnWidth2 = [55,0],
                                select=1,
                                cc=self.intFieldChange,
                                parent='formValueFrame')
            cmds.text('textItem', label='Item:', enable=False, 
                      height=20,parent='formValueFrame')
            self.itemNumber = cmds.intField('itemNumber', 
                                            enable=False, 
                                            height=20, 
                                            width=60, 
                                            parent='formValueFrame', 
                                            ec=partial(self.stateSelectToolBt, 
                                                       True),
                                            value=6000, min=5000, max=6000)
            cmds.iconTextCheckBox('selButton', 
                                  label='Select', 
                                  height=40, 
                                  style='textOnly', 
                                  bgc=[0.23,0.33,0.39],
                                  cc=partial(self.stateSelectToolBt, False),
                                  enable=False)
            cmds.formLayout('formValueFrame', 
                            e=True, 
                            af=[('radioGrpItem', 'left', 10),
                                ('radioGrpItem', 'top', 10),
                                ('radioGrpItem', 'right', 0),
                                ('selButton', 'left', 10),
                                ('selButton', 'right', 10),
                                ('selButton', 'bottom', 10),
                                ('textItem', 'left', 15),
                                ('itemNumber', 'right', 15),
                                ],
                            ac=[
                                ('textItem', 'right', 1, 'radioGrpItem'),
                                ('textItem', 'top', 10, 'radioGrpItem'),
                                ('itemNumber', 'top', 10, 'radioGrpItem')
                                ])
            #===================================================================
            # SELECTION SUB-MENU
            #===================================================================
            def radioPlaneChange(args):
                if cmds.radioButtonGrp('radioGrpSideSel', q=True, select=True) == 3:
                    cmds.radioButtonGrp(radioGroupMirrorPlanesSel, e=True, enable=False)
                elif cmds.radioButtonGrp('radioGrpSideSel', q=True, select=True) == 4:
                    cmds.radioButtonGrp(radioGroupMirrorPlanesSel, e=True, enable=False)
                else:
                    cmds.radioButtonGrp(radioGroupMirrorPlanesSel, e=True, enable=True)
            def texSideChange(args):
                if cmds.radioButtonGrp('radioGrpPlaneSel', q=True, select=True) == 1:
                    cmds.radioButtonGrp('radioGroup', e=True, select=1)
                    cmds.checkBox('checkBox', e=True, label=' Positive to negative ( +Z to -Z ) ')
                    cmds.radioButtonGrp(radioGroupSideSel, e=True, 
                                        labelArray3=['Z Pos', 'Z Neg', ' All'])
                elif cmds.radioButtonGrp('radioGrpPlaneSel', q=True, select=True) == 2:
                    cmds.radioButtonGrp('radioGroup', e=True, select=2)
                    cmds.checkBox('checkBox', e=True, label=' Positive to negative ( +X to -X ) ')
                    cmds.radioButtonGrp(radioGroupSideSel, e=True, 
                                        labelArray3=['X Pos', 'X Neg', ' All'])
                elif cmds.radioButtonGrp('radioGrpPlaneSel', q=True, select=True) == 3:
                    cmds.radioButtonGrp('radioGroup', e=True, select=3)
                    cmds.checkBox('checkBox', e=True, label=' Positive to negative ( +Y to -Y ) ')
                    cmds.radioButtonGrp(radioGroupSideSel, e=True, 
                                        labelArray3=['Y Pos', 'Y Neg', ' All'])
                    cmds.radioButtonGrp(radioGroupMirrorPlanesSel, e=True, enable=True)
            #===================================================================    
            cmds.formLayout('formSelectionFrame', parent='selectionFrame')
            radioGroupMirrorPlanesSel = cmds.radioButtonGrp('radioGrpPlaneSel', 
                                                            labelArray3=['XY', 'YZ', 'XZ'],
                                                            numberOfRadioButtons=3,
                                                            columnWidth3 = [73,73,73],
                                                            select=2,
                                                            enable=False,
                                                            cc=texSideChange,
                                                            parent='formSelectionFrame')
            radioGroupSideSel = cmds.radioButtonGrp('radioGrpSideSel', 
                                                    labelArray4=['X Pos', 'X Neg', ' All', 'User'],
                                                    numberOfRadioButtons=4,
                                                    columnWidth4 = [73,73,73,73],
                                                    select=4,
                                                    cc=radioPlaneChange,
                                                    parent='formSelectionFrame')
            cmds.button('checkSel', label='Check', height=20, width=60, 
                        enable=False, 
                        c=partial(self.checkAnalysis, True),
                        parent='formSelectionFrame')
            cmds.frameLayout('frameSelStatus', lv=False, enable=False)
            self.textStatus = cmds.text(label='Press "Check" to view Deltas', 
                                        parent='frameSelStatus')
            
            cmds.formLayout('formSelectionFrame', 
                            e=True, af=[('radioGrpPlaneSel', 'left', 15),
                                        ('radioGrpPlaneSel', 'top', 10),
                                        ('radioGrpSideSel', 'left', 15),
                                        ('checkSel', 'top', 10),
                                        #('checkSel', 'right', 15),
                                        ('frameSelStatus', 'left', 15),
                                        ('frameSelStatus', 'right', 15),
                                        ('frameSelStatus', 'bottom', 10),
                                        ],
                                    ac=[
                                        ('radioGrpSideSel', 'top', 10, 'radioGrpPlaneSel'),
                                        ('checkSel', 'left', 20, 'radioGrpPlaneSel'),
                                        ('frameSelStatus', 'top', 10, 'radioGrpSideSel'),
                                        ])
            
            #===================================================================
            # TOOLS SUB-MENU
            #===================================================================       
            cmds.formLayout('formPruneFrame', parent='toolsFrame')
            cmds.button('Prune', label='Prune', height=20, 
                        width=60, c=partial(toolAction, 'prune', True), parent='formPruneFrame')
            cmds.text('bellowText', label='Bellow:', 
                      height=20,parent='formPruneFrame')
            cmds.floatField('bellowVal', height=20, pre=5,
                            width=60, parent='formPruneFrame', 
                            min=0.00001, value=0.00001, step=0.00001)
            cmds.separator('firstSep', st='in')
            cmds.text('textFactor', label='Factor:', enable=False, height=20,
                      parent='formPruneFrame')
            cmds.floatField('factorValue', enable=False, height=20, pre=5, 
                            width=60, parent='formPruneFrame', 
                            step=0.00001, value=0.00001, min=0.00001)
            cmds.button('Add', label='+',  enable=False, 
                        height=20, width=25, 
                        c=partial(toolAction, 'factor', True),
                        parent='formPruneFrame')
            cmds.button('Sub', label='-',  enable=False, 
                        height=20, width=25,
                        c=partial(toolAction, 'factor', False), 
                        parent='formPruneFrame')
            cmds.separator('secondSep', st='in')
            cmds.button('ZeroBut', label='Zero', enable=False, 
                        height=35, width=75, 
                        c=partial(toolAction, 'zero', True),
                        parent='formPruneFrame')
            cmds.button('ResetBut', label='Reset', enable=False, 
                        height=35, width=75, 
                        c=partial(toolAction, 'reset', True),
                        parent='formPruneFrame')
            cmds.formLayout('formPruneFrame', 
                            e=True, af=[('bellowText', 'top', 10),
                                        ('bellowText', 'left', 10),
                                        ('bellowVal', 'top', 10),
                                        ('Prune', 'top', 10),
                                        ('Prune', 'right', 10),
                                        ('firstSep', 'left', 10),
                                        ('firstSep', 'right', 10),
                                        ('textFactor', 'left', 10),
                                        ('Sub', 'right', 10),
                                        ('secondSep', 'left', 10),
                                        ('secondSep', 'right', 10),
                                        ('ZeroBut', 'left', 10),
                                        ('ZeroBut', 'bottom', 10),
                                        ('ResetBut', 'right', 10),
                                        ('ResetBut', 'bottom', 10),
                                        ],
                                    ac=[
                                        ('bellowVal', 'left', 5, 'bellowText'),
                                        ('bellowVal', 'right', 5, 'Prune'),
                                        ('firstSep', 'top', 5, 'bellowText'),
                                        ('textFactor', 'top', 5, 'firstSep'),
                                        ('factorValue', 'top', 5, 'firstSep'),
                                        ('factorValue', 'left', 5, 'textFactor'),
                                        ('Add', 'top', 5, 'firstSep'),
                                        ('Sub', 'top', 5, 'firstSep'),
                                        ('Add', 'left', 5, 'factorValue'),
                                        ('secondSep', 'top', 5, 'textFactor'),
                                        ])

            #===================================================================
            # EDITING FORMS LAYOUT
            #===================================================================
            cmds.formLayout(blendNodeFormLayout,
                            edit=True,
                            attachForm=[(selectRefreshButton, 'left', 0),
                                        (self.optionMenuGrpBlend, 'top', 2),
                                        (self.createBlendShapeNode, 'right', 0)],
                            attachControl=[(self.optionMenuGrpBlend, 'left', 10,
                                            selectRefreshButton),
                                          (self.createBlendShapeNode, 'left', 10,
                                           self.optionMenuGrpBlend)])
            cmds.formLayout(tabForm,
                            edit=True,
                            attachForm=[(self.optionTabs, 'left', 0),
                                        (self.optionTabs, 'top', 0),
                                        (self.optionTabs, 'right', 0),
                                        (self.optionTabs, 'bottom', 0)])
            cmds.formLayout(crFormLayout,
                            edit=True,
                            attachForm=[(buttonCreateNewCr, 'left', 0),
                                        (buttonCreateNewCr, 'top', 0),
                                        (buttonCreateNewCr, 'right', 5),
                                        (self.scrollCrList, 'left', 0),
                                        (self.scrollCrList, 'right', 5),
                                       
                                        (self.checkActivated, 'left', 10),
                                        #(self.checkActivated, 'right', 5),
                                        #(self.checkNegValues, 'left', 25),
                                        (self.checkNegValues, 'right', 10),
                                                                             
                                        (self.filterField, 'left', 0),
                                        (self.filterField, 'right', 0),
                                        
                                        (self.buttonRefresh, 'left', 0),
                                        (self.buttonRefresh, 'right', 5),
                                        (self.buttonRefresh, 'bottom', 0)
                                        ],
                            attachControl=[(self.scrollCrList, 'top', 5,
                                            buttonCreateNewCr),
                                           (self.scrollCrList, 'bottom', 0,
                                            self.checkActivated),
                                           #(self.checkNegValues, 'left', 18,
                                           # self.checkActivated),
                                           (self.checkNegValues, 'bottom', 0,
                                            self.filterField),
                                           (self.checkActivated, 'bottom', 0,
                                            self.filterField),
                                           (self.filterField, 'bottom', 5,
                                            self.buttonRefresh)])
          
            cmds.formLayout(inbetweenFormLayout,
                            edit=True,
                            attachForm=[(buttonRefreshInbetween, 'right', 0),
                                        (buttonRefreshInbetween, 'top', 0),
                                        (textTypeRowLayout, 'left', 25),
                                        (textTypeRowLayout, 'right', 5),
                                        (separatorInbOut, 'left', 5),
                                        (separatorInbOut, 'right', 0),
                                        (self.checkInteractive, 'top', 3),
                                        (self.checkInteractive, 'left', 5),
                                        (self.scrollInbetweenList, 'left', 5),
                                        (self.scrollInbetweenList, 'right', 0),
                                        (self.scrollInbetweenList, 'bottom', 0)],
                            attachControl=[(buttonRefreshInbetween, 'left',
                                            10, self.checkInteractive),
                                           (separatorInbOut, 'top',
                                            6, buttonRefreshInbetween),
                                           (textTypeRowLayout, 'top',
                                            2, separatorInbOut),
                                           (self.scrollInbetweenList, 'top',
                                            2, textTypeRowLayout)])
            cmds.formLayout(mainForm,
                            edit=True,
                            attachForm=[(separatorTop, 'left', 5),
                                        (separatorTop, 'right', 5),
                                        (separatorTop, 'top', 0),
                                        (blendNodeFormLayout, 'left', 5),
                                        (blendNodeFormLayout, 'top', 5),
                                        (blendNodeFormLayout, 'right', 5),
                                        (separatorTopB, 'left', 5),
                                        (separatorTopB, 'right', 5),
                                        (self.mainPanelLayout, 'left', 5),
                                        (self.mainPanelLayout, 'right', 5),
                                        (separatorBottom, 'left', 5),
                                        (separatorBottom, 'right', 5),
                                        (tabForm, 'left', 5),
                                        (tabForm, 'right', 5),
                                        (tabForm, 'bottom', 5)],
                            attachControl=[(blendNodeFormLayout, 'top', 5, separatorTop),
                                           (separatorTopB, 'top', 5, blendNodeFormLayout),
                                           (self.mainPanelLayout, 'top', 0, separatorTopB),
                                           (self.mainPanelLayout, 'bottom', 5, separatorBottom),
                                           (separatorBottom, 'bottom', 5, tabForm)])

            
            # Adding callBack from redo and undo to refresh ui
            self.userCallback(cmd='add')
            # Activate All Tab options based on condition if has ibetweens or not
            self.enableUi()
            
            cmds.showWindow('dsl_Sculpt_Inbetween_Editor')
            cmds.window('dsl_Sculpt_Inbetween_Editor', 
                        title=self.winName, 
                        edit=True, 
                        wh=self.size)

    #===========================================================================
    # END OF UI CLASS
    #===========================================================================
    
    def intFieldChange(self, arg):
        if cmds.radioButtonGrp('radioGrpItem', q=True, select=True) == 1:
            cmds.text('textItem', e=True, enable=False)
            cmds.intField('itemNumber', e=True, enable=False)
            cmds.iconTextCheckBox('selButton', e=True, enable=False)
            cmds.iconTextCheckBox('selButton', e=True, value=0)
            cmds.iconTextCheckBox('selButton', e=True, label='Select')
            #------
            cmds.formLayout('formSelectionFrame', e=True, enable=True)
            cmds.formLayout('formPruneFrame', e=True, enable=True)
            cmds.button('checkSel', e=True, enable=False)
            cmds.frameLayout('frameSelStatus', e=True, enable=False)
            cmds.text(self.textStatus, e=True, label='Press "Check" to view Deltas')
            #------
            cmds.text('textFactor', e=True, enable=False)
            cmds.floatField('factorValue', e=True, enable=False)
            cmds.button('Add', e=True, enable=False)
            cmds.button('Sub', e=True, enable=False)
            cmds.separator('secondSep', e=True, enable=False )
            cmds.button('ZeroBut', e=True, enable=False)
            cmds.button('ResetBut', e=True, enable=False)
        else:
            cmds.text('textItem', e=True, enable=True)
            cmds.intField('itemNumber', e=True, enable=True)
            cmds.iconTextCheckBox('selButton', e=True, enable=True)
            cmds.iconTextCheckBox('selButton', e=True, value=0)
            #------
            cmds.formLayout('formSelectionFrame', e=True, enable=False)
            cmds.formLayout('formPruneFrame', e=True, enable=False)
            cmds.button('checkSel', e=True, enable=True)
            cmds.frameLayout('frameSelStatus', e=True, enable=True)
            #------
            cmds.text('textFactor', e=True, enable=True)
            cmds.floatField('factorValue', e=True, enable=True)
            cmds.button('Add', e=True, enable=True)
            cmds.button('Sub', e=True, enable=True)
            cmds.separator('secondSep', e=True, enable=True )
            cmds.button('ZeroBut', e=True, enable=True)
            cmds.button('ResetBut', e=True, enable=True)
                    

        
        
        
        
    
    def userCallback(self, cmd):
        #print 'def userCallback'
        
        # Thanks to Rosenio Pinto from facebook
        Null = om.MObject()
        undoFunc = self.refreshCrAndInbetweenList
        redoFunc = self.refreshCrAndInbetweenList
        #sceneOpenedFunc = self.refreshCrAndInbetweenList
        # Quit Tool
        sceneOpenedFunc = partial(self.barMenuOptions, 3)
        if cmd == 'add':
            undoID = om.MEventMessage.addEventCallback('Undo', undoFunc, Null)
            redoID = om.MEventMessage.addEventCallback('Redo', redoFunc, Null)
            sceneOpenedID = om.MEventMessage.addEventCallback('SceneOpened', 
                                                              sceneOpenedFunc, 
                                                              Null)
            NewSceneOpenedID = om.MEventMessage.addEventCallback('NewSceneOpened', 
                                                                 sceneOpenedFunc, 
                                                                 Null)
            self.callbackIDs = [undoID, redoID, sceneOpenedID, NewSceneOpenedID]
        elif cmd == 'remove':
            try:
                for ID in self.callbackIDs:
                    om.MEventMessage.removeCallback(ID)
            except:
                print 'There is no userCallback to be removed'
        else:
            print 'The argument must be "add" or "remove"'
           

    def popupBlendShapeSelect(self, arg=None):
        #print 'def popupBlendShapeSelect'
        
        
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        try:
            cmds.select(blendShapeNode)
        except:
            print 'None'

        
    
    def popupMenuLiveSlide(self, parentTo=None, arg=None):
        #print 'def popupMenuLiveSlide'
        
        # Popup for for the liveSlider of the corrective selected
       
        self.popUpMenuGadget = cmds.popupMenu(parent=parentTo)
        '''
        self.popOptKey = cmds.menuItem(label='Key',
                                       c=partial(self.liveSlideCmd, 'key'),
                                       parent=self.popUpMenuGadget)
        '''
        self.popOptSelectInput = cmds.menuItem(label='Select Input',
                                               c=partial(self.liveSlideCmd, 'SelectInput'),
                                               parent=self.popUpMenuGadget)
        self.popOptBreakConnections = cmds.menuItem(label='Break Connections',
                                                    c=partial(self.liveSlideCmd, 'BreakConnections'),
                                                    parent=self.popUpMenuGadget)
        '''
        self.popMirrorDeltaValues = cmds.menuItem(label='Auto Mirror Deltas',
                                                    c=partial(self.liveSlideCmd, 'MirrorDeltas'),
                                                    parent=self.popUpMenuGadget)
        self.popFlipDeltaValues = cmds.menuItem(label='Auto Flip Deltas',
                                                    c=partial(self.liveSlideCmd, 'FlipDeltas'),
                                                    parent=self.popUpMenuGadget)
        self.popOptPrintInput = cmds.menuItem(label='Print Input',
                                              c=partial(self.liveSlideCmd, cmd='PrintInput'),
                                              parent=self.popUpMenuGadget)
        self.popOptPrintOutput = cmds.menuItem(label='Print Output',
                                               c=partial(self.liveSlideCmd, cmd='PrintOutput'),
                                               parent=self.popUpMenuGadget)
        '''
   
    def popupMenuCr(self, parentTo=None, arg=None):
        #print 'def popupMenuCr'
        
        # Popup for all into the corrective textScrollLayout
        self.popUpMenuGadget = cmds.popupMenu(parent=parentTo)
        #self.popOptReplace = cmds.menuItem(label='Replace',
        #                                   parent=self.popUpMenuGadget)
        self.popOptAutoMirror = cmds.menuItem(label='Auto Mirror',
                                              parent=self.popUpMenuGadget,
                                              c=partial(self.applyMirrorOptionData, autoMirror=True))
        self.popOptRename = cmds.menuItem(label='Rename',
                                          parent=self.popUpMenuGadget,
                                          c=self.renameCorrective)
        self.popOptDuplicate = cmds.menuItem(label='Duplicate',
                                             parent=self.popUpMenuGadget,
                                             c=self.duplicateCorrective)
        self.popOptDelete= cmds.menuItem(label='Delete',
                                         parent=self.popUpMenuGadget,
                                         c=self.deleteCorrective)
        self.popCreateCombo= cmds.menuItem(label='Combo',
                                           parent=self.popUpMenuGadget,
                                           c=partial(self.createCrCombo, 'multiplyDivide', 'Cmb_'))
        return self.popUpMenuGadget
       
    
    def popupMenuInbetween(self, parentTo=None, correctiveItem=None, arg=None):
       
        #print 'def popupMenuInbetween'
        # Popup to add for each inbetween item listed
        namePopUp = parentTo
        
        self.popUpMenuGadget = cmds.popupMenu(parent=parentTo)
        self.popReplace = cmds.menuItem('popReplace' + namePopUp, label='Replace',
                                     parent=self.popUpMenuGadget,
                                     c=partial(self.addShape, None, mode='Replace',
                                               correctiveItem=correctiveItem))
        self.popCopy = cmds.menuItem('popCopy' + namePopUp, label='Copy',
                                     parent=self.popUpMenuGadget,
                                     c=partial(self.copyDataCr, 
                                               correctiveItem))
        self.popPaste = cmds.menuItem('popPaste' + namePopUp, label='Paste',
                                      parent=self.popUpMenuGadget,
                                      c=partial(self.pasteDataCr, 
                                               correctiveItem))
        self.popZero = cmds.menuItem('popZero' + namePopUp, label='Zero',
                                      parent=self.popUpMenuGadget,
                                      c=partial(self.resetDataCr, 
                                                correctiveItem))
        self.popDelta = cmds.menuItem('popDelta' + namePopUp, label='Delta',
                                      parent=self.popUpMenuGadget,
                                      c=partial(self.seeDelta, 
                                                correctiveItem, True))
        self.popTools = cmds.menuItem('popTools' + namePopUp, label='Tools',
                                      parent=self.popUpMenuGadget,
                                      c=partial(self.itemToTools, 
                                                correctiveItem))
        

        return self.popUpMenuGadget
   
   
    def listInbetween(self, inbetweenList=None,
                      interactiveMode=None,
                      correctiveName=None,
                      parent=None,
                      resetDeltaTools=False,
                      arg=None):
      
        #print 'def listInbetween'
        # List all items of the corrective and place them as a slider into the
        # inbetween scrollLayout.  Includes the liveSlider of the respective
        # selected corrective
       
        checkInteractive = cmds.checkBox(self.checkInteractive, q=True, value=True)
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend, q=True, value=True)
        if not correctiveName:
            correctiveName = cmds.textScrollList(self.scrollCrList,
                                                 q=True,
                                                 si=True)[0]
       
        # Try get inbetween list, if does not, return 0 to proceed with the loop
        try:
            inbetweenList = self.getCrGrpItem()[str(correctiveName)][1]
        except:
            inbetweenList = [0]
        listCurrentInbetween = cmds.scrollLayout(self.scrollInbetweenList, 
                                                 q=True, childArray=True)
        # Try delete all current UI widgets 
        try:
            #print '---->', listCurrentInbetween
            for i in listCurrentInbetween:
                #print '==>', i
                cmds.deleteUI(i)
        except:
            pass
      
        self.headText = cmds.text('headText' + correctiveName,
                                  label=correctiveName,
                                  align='center',
                                  height=20,
                                  bgc=[0.5, 0.4, 0.33],
                                  parent=self.scrollInbetweenList)
        cmds.separator('separator'  + correctiveName, style='out', height=10, 
                       parent=self.scrollInbetweenList)
        #=======================================================================
        # LIVE SLIDE
        #=======================================================================
       
        ## Add as popup menu: select Input / Key / breakConnections /
        self.liveSlide = cmds.floatSliderButtonGrp('liveSlide' + correctiveName,
                                                   label='VALUE',
                                                   enable=True,
                                                   field=True,
                                                   fieldMinValue=0.000,
                                                   fieldMaxValue=1.000,
                                                   value=0.5,
                                                   adjustableColumn=3,
                                                   columnWidth=([1,50],
                                                                [2,40],
                                                                [3,200],
                                                                [4, 50]),
                                                   columnAttach=[(1, 'both', 0),
                                                                 (2, 'right', 0),
                                                                 (3, 'both', 0)],
                                                   rowAttach=[1, 'both', 1],
                                                   columnAlign=[(1, 'center')],
                                                   precision=3,
                                                   buttonLabel='   Key  ',
                                                   symbolButtonDisplay=False,
                                                   image='cmdWndIcon.xpm',
                                                   minValue=0.000,
                                                   maxValue=1.000,
                                                   buttonCommand=partial(self.liveSlideCmd, 'key'),
                                                   parent=self.scrollInbetweenList)
       
        # Create connection with the actual corrective 2 way link
        cmds.connectControl(self.liveSlide, blendShapeNode + '.' + correctiveName)
        # Add the popup menu:
        self.popupMenuLiveSlide(parentTo=self.liveSlide)
        cmds.separator(style='out', height=10, parent=self.scrollInbetweenList)
        #print '............. ', inbetweenList
        for idx, correctiveItem in enumerate(inbetweenList):
            if idx % 2 == 0:
                bcgValue = [0.22, 0.22, 0.22]
            else:
                bcgValue = [0.32, 0.32, 0.32]
            
            # ------------------------------------------------------------------
            # If there's no data indicate with a RED color on the slider
            try:
                dicData = self.getCrPointData(blendShapeNode, 
                                              correctiveName, 
                                              correctiveItem)
                if dicData.values()[0][0] == None:
                    bcgValue = [1.0, 0.0, 0.0]
            except:
                print '*** It has no item to be scanned'
                pass
            # ------------------------------------------------------------------

            finb = float(correctiveItem - 5000) / 1000
            
            #nameInbSlider = '%s%s' %(correctiveName, correctiveItem)
            nameInbSlider = re.sub('[[\]]', '', '%s%s%s' %(correctiveName, '__', correctiveItem))
            #print '---nameInbSlider---> ', nameInbSlider
            #===================================================================
            # INBETWEEN SLIDES
            #===================================================================
            self.slider = cmds.floatSliderButtonGrp(nameInbSlider,
                                                    label=str(correctiveItem),
                                                    field=True,
                                                    fieldMinValue=0.000,
                                                    fieldMaxValue=1.000,
                                                    value=finb,
                                                    adjustableColumn=3,
                                                    columnWidth=([1,50],
                                                                 [2,40],
                                                                 [3,200],
                                                                 [4, 50]),
                                                    columnAttach=[(1, 'both', 0),
                                                                  (2, 'right', 0),
                                                                  (3, 'both', 0)],
                                                    rowAttach=[1, 'both', 1],
                                                    columnAlign = [(1, 'center')],
                                                    precision=3,
                                                    buttonLabel=' Select ',
                                                    symbolButtonDisplay=True,
                                                    image='dslCmDelete.xpm',
                                                    minValue=0.000,
                                                    maxValue=1.000,
                                                    bgc=bcgValue,
                                                    buttonCommand=partial(self.selectCorrective,
                                                                          nameInbSlider),
                                                    changeCommand=partial(self.copyPasteInbetween,
                                                                          nameInbSlider,
                                                                          closeChunk=True),
                                                    symbolButtonCommand=partial(self.deleteInbetween,
                                                                                correctiveItem=correctiveItem,
                                                                                deleteSlider=True),
                                                    parent=self.scrollInbetweenList)

            # Adding the popup for each inbetween in the loop
            self.popupMenuInbetween(parentTo=nameInbSlider, correctiveItem=correctiveItem, arg=None)
            if correctiveItem == 0:
                cmds.floatSliderButtonGrp(self.slider, e=True, label='N/D',
                                          enable=False)
                cmds.floatSliderButtonGrp(self.liveSlide, e=True, enable=False)
          
            interactiveMode = checkInteractive
            if interactiveMode == True:
                cmds.floatSliderButtonGrp(self.slider, e=True,
                                          dragCommand=partial(self.copyPasteInbetween,
                                                              nameInbSlider))
                
            if correctiveItem == inbetweenList[-1]:
                cmds.floatSliderButtonGrp(self.slider, e=True,
                                          #enable=True,
                                          symbolButtonDisplay=False)
            # Reset DELTA TOOLS for each new user selection at crList
            if resetDeltaTools:
                try:
                    # Reset Data to the selected one
                    self.itemToTools(correctiveItem)
                    cmds.radioButtonGrp('radioGrpItem', e=True, select=1)
                    self.intFieldChange(arg)                    
                except:
                    pass
    
    def checkIfData(self, blendShapeNode=None, corrective=None):
        #print 'def checkIfData'
        '''
        Check if there is data inside the corrective to colorize the bar inside
        the inbetween menu
        ...incomplete
        '''
        
        #======================================================================
        # AUTO INFO FROM UI STATEMENT
        #======================================================================
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True,
                                             si=True)[0]     
        #=======================================================================        
        correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
        
        iTg = '%s.inputTarget[0]' %blendShapeNode
        iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
        iTi = '.inputTargetItem[%s]' %correctiveItem
        iPt = '.inputPointsTarget'
        
        
        print cmds.getAttr(iTg + iTgGr + iTi + iPt)
        
        
        # Remove multiInstance to reset the shape
        #cmds.removeMultiInstance(iTg + iTgGr + iTi, b=True)
        # Query to create the proper new plug with NONE inside
        #cmds.getAttr(iTg + iTgGr + iTi + iPt)
        
    
    def rePattern(self, filterUi):
        patternRe = []
        for c in enumerate(filterUi):
            #print c
            # Check first string Item:
            if c[0] == 0 and c[1] != '*':
                patternRe.append('\\b')
                patternRe.append(c[1])
            # Check last string Item:
            elif c[0] == len(filterUi)-1 and c[1] != '*':
                patternRe.append(c[1])
                patternRe.append(r'\\b')
            elif c[1] != '*' and c[1] != '+':
                patternRe.append(c[1])
            elif c[1] == '+':
                patternRe.append('(\\b)|(\\b)')
            elif c[1] == '*':
                patternRe.append('(\w+|\d+)')
        rePattern = r''.join(patternRe)
        return rePattern
    
    
    def listCorrective(self, corrective=None, arg=None):
       
        #print 'def stateGadgets'
        # Refresh and list the corrective List
       
        # Try to perform "Clean No Data" before add new Corrective, if
        # doesn't exist any corrective, ignore the cleanup

        if corrective == None:
            corrective = cmds.textScrollList(self.scrollCrList, q=True, si=True)[0]
        textFilter = cmds.textFieldGrp(self.filterField, q=True, text=True)
        checkState = cmds.checkBox(self.checkActivated, q=True, v=True)
        checkNegState = cmds.checkBox(self.checkNegValues, q=True, v=True)
        '''
        if ('*') in textFilter:
            textFilter = textFilter.split('*')
        else:
            textFilter = [textFilter]
        '''
        #### ------------------------------------------------------------------
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        try:
            gatherInfoFrom = '.weight'
            listAttrPath = str(blendShapeNode) + str(gatherInfoFrom)
            listCorrective = cmds.listAttr(listAttrPath, multi=True)
        except:
            listCorrective = ['None']
            pass
        #### ------------------------------------------------------------------
        pat = str(self.rePattern(textFilter))
        p = re.compile(pat)
        textFilteredList = []
        if textFilter != None:
            for c in listCorrective:
                if p.match(c):
                    textFilteredList.append(c)

            '''
            for text in textFilter:

                for cr in listCorrective:
                    if str(text) in cr:
                        textFilteredList.append(cr)
           '''
            
        checkFilteredList = []
        toleranceValue = 0.00001
        if checkState == True:
            for cr in listCorrective:
                if cmds.getAttr(blendShapeNode + '.' + cr) >= toleranceValue:
                    checkFilteredList.append(cr)
                if checkNegState == True:
                    for cr in listCorrective:
                        if cmds.getAttr(blendShapeNode + '.' + cr) <= -toleranceValue:
                            checkFilteredList.append(cr)
        
        else:
            checkFilteredList = listCorrective
       
        intersectList = list(set(textFilteredList)&set(checkFilteredList))
        if intersectList:
            listFilteredCr = intersectList
        else:
            listFilteredCr = ['None']
        ##### ------------------------------------------------------------------
        # If current selected in crList isn't in the new listFilteredCr...
        confirmRefresh = None
        if corrective not in intersectList:
            corrective = listFilteredCr[0]
            confirmRefresh = True
            #print corrective
        listFilteredCr = list(sorted(set(listFilteredCr)))
        cmds.textScrollList(self.scrollCrList, e=True, ra=True)
        cmds.textScrollList(self.scrollCrList,
                            e=True,
                            a=listFilteredCr,
                            si=corrective)
       
        if confirmRefresh:
            self.listInbetween()
       
        return listCorrective

                                       
    def stateSelectToolBt(self, resetButton, args):
        global originalPointIndex
        
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True, value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True, si=True)[0]
        correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
        item = cmds.intField('itemNumber', q=True, value=True)
        if resetButton:
            cmds.iconTextCheckBox('selButton', e=True, value=0)
            cmds.formLayout('formSelectionFrame', e=True, enable=False)
            cmds.formLayout('formPruneFrame', e=True, enable=False)
            cmds.iconTextCheckBox('selButton', e=True, label='Select')
        else:
            if cmds.iconTextCheckBox('selButton', q=True, value=True) == 0:
                cmds.formLayout('formSelectionFrame', e=True, enable=False)
                cmds.formLayout('formPruneFrame', e=True, enable=False)
                cmds.iconTextCheckBox('selButton', e=True, label='Select')
            elif (cmds.iconTextCheckBox('selButton', q=True, value=True) == 1 
                  and self.itemExist(item) == True):
                print self.itemExist(item)
                cmds.formLayout('formSelectionFrame', e=True, enable=True)
                cmds.formLayout('formPruneFrame', e=True, enable=True)
                cmds.iconTextCheckBox('selButton', e=True, label='Item %s' %item)
                try:
                    self.refreshCr(args)
                    originalPointIndex = dslDo.combinePointIndex(blendShapeNode, 
                                                                 correctiveGroup, 
                                                                 correctiveItem=item)
                except:
                    print 'Corrective cannot be refreshed'

            else:
                print self.itemExist(item)
                print 'item: %s does not exist in this corrective' %item
                cmds.iconTextCheckBox('selButton', e=True, value=0)
    
    def refreshCr(self, args):
        #print 'def refreshCr'
        # Refresh the corrective with delta that never been used (Value 0)
        
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True, value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True, si=True)[0]
        
        originalValue = cmds.getAttr(blendShapeNode + '.' + correctiveName)    
        cmds.setAttr(blendShapeNode + '.' + correctiveName, 1)
        cmds.refresh()
        cmds.setAttr(blendShapeNode + '.' + correctiveName, originalValue)
        cmds.refresh()

        
        
        
    def checkAnalysis(self, selectAtTheEnd, args):
        
        #print 'def checkAnalysis'
        
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True, value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True, si=True)[0]
        correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
        
        if cmds.radioButtonGrp('radioGrpItem', q=True, select=True) == 1:
            correctiveItem = self.listItems(blendShapeNode, correctiveGroup)[0]
        else:
            correctiveItem = [cmds.intField('itemNumber', q=True, value=True)]

        
        try: 
            deltaCount = self.seeDelta(correctiveItem[0], selectAtTheEnd)
            labelText = '%s Deltas' %deltaCount
            cmds.text(self.textStatus, e=True, label=labelText)
        except:
            # If "All" is selected in Apply to Section
            pass    

    def listItems(self, blendShapeNode, correctiveGroup):
        #print 'def listItems'
        iTg = '%s.inputTarget[0]' %blendShapeNode
        iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
        iTi = '.inputTargetItem'
        return cmds.getAttr(iTg + iTgGr + iTi, mi=True)
        
    def itemExist(self, item, arg=None):
        #print 'def itemExist'
        # True if item exist in the corrective
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                                 q=True, value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True, si=True)[0]
        correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
        iTg = '%s.inputTarget[0]' %blendShapeNode
        iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
        iTi = '.inputTargetItem'
        listAllItems = cmds.getAttr(iTg + iTgGr + iTi, mi=True)
        if item in listAllItems:
            return True
        else:
            return False
        
    def createCrCombo(self, typeNode='blendColors', prefix='Cmb_', arg=None):
        #print 'def createCrCombo'
        
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True, value=True)
        selCrList = cmds.textScrollList(self.scrollCrList, q=True, nsi=True)
        
        if selCrList != 2:
            print 'select 2 correctives to create a combo'   
        else:
            
            crName =  cmds.textScrollList(self.scrollCrList, q=True, si=True)
            #print '--->', '_' + crName[0] + '_' + crName[-1]
            #print cmds.getAttr(blendShapeNode + '.' + crName[0])
            #print cmds.getAttr(blendShapeNode + '.' + crName[-1])
            newCrName = str(prefix + crName[0] + '_' + crName[-1])
            #print type(prefix)
            #print type(newCrName)
            comboConditionName = typeNode + '_Combo_' + newCrName
            shNode = cmds.shadingNode(typeNode, 
                                      n=str(comboConditionName), 
                                      asUtility=True)
            self.addCorrective(newCorrectiveName=newCrName, 
                               refreshLists=True,
                               copyItself=False)
            
            if typeNode == 'blendColors':
                inputNodeA = '.color1R'
                inputNodeB = '.color2R'
                outputNode = '.output.outputR'
            
            elif typeNode == 'multiplyDivide':    
                inputNodeA = '.input1.input1X'
                inputNodeB = '.input2.input2X'
                outputNode = '.output.outputX'
                
            cmds.connectAttr(blendShapeNode + '.' + crName[0],
                            shNode + inputNodeA)
            cmds.connectAttr(blendShapeNode + '.' + crName[-1],
                            shNode + inputNodeB)
            cmds.connectAttr(shNode + outputNode,
                             blendShapeNode + '.' + newCrName)
            
    
    def bakeEditItem(self, correctiveItem=None, arg=None):
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                             q=True, value=True)
        cmds.textScrollList(self.scrollCrList, q=True, si=True)[0]
        self.getGeoNameFromNode(blendShapeNode)
        
    def enableUi(self, arg=None):
        # Turn off all tabs if theres no inbetween showing:
        if cmds.floatSliderButtonGrp(self.slider, q=True, label=True)!= 'N/D':

            cmds.paneLayout(self.mainPanelLayout, e=True, enable=True)
            cmds.tabLayout(self.optionTabs, e=True, enable=True)
            
        else:

            cmds.paneLayout(self.mainPanelLayout, e=True, enable=False)
            cmds.tabLayout(self.optionTabs, e=True, enable=False)
    
    def refreshCrAndInbetweenList(self, blendShapeNode=None,
                                  listCorrective=None,
                                  corrective=None,
                                  arg=None):
       
        #print 'def refreshCrAndInbetweenList'
        # Wraper to refresh both list when a filter or activated checkBox is on
        #cmds.checkBox(self.checkActivated, e=True, value=False)
        #cmds.textFieldGrp(self.filterField, e=True, text='')

        self.listCorrective(corrective=corrective)
        self.listInbetween(inbetweenList=listCorrective, correctiveName=corrective)
        
        if cmds.text(self.textStatus, q=True, label=True) != 'Press "Check" to view Deltas':
            om.MGlobal.displayInfo('Press "Check" again to refresh Delta count display')
            
        # Turn off all tabs if theres no inbetween showing:
        self.enableUi()

        
    def liveSlideCmd(self, cmd=None, arg=None):

        # Commands of the popup menu of the liveSlider
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True, value=True)
       
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                                 q=True, si=True)[0]
       
        selCorrective = blendShapeNode + '.' + correctiveName
        if cmd == 'key':
            cmds.setKeyframe(selCorrective, itt='linear', ott='linear')
            self.liveSlideCmd(cmd='SelectInput')
            print 'Key created'
        elif cmd == 'SelectInput':
            connection = cmds.listConnections(selCorrective, p=True)[0]
            cmds.select(connection.split('.')[0])
           
        elif cmd == 'BreakConnections':
            userConfirm = str(cmds.confirmDialog(title='Break Connection', 
                                                 message='Are you sure?', 
                                                 button=['Confirm', 'Cancel'],
                                                 defaultButton='Cancel', 
                                                 cancelButton='Cancel', 
                                                 dismissString='Cancel'))
            
            if userConfirm == 'Confirm':
                try:
                    connection = cmds.listConnections(selCorrective, p=True)[0]
                    cmds.disconnectAttr(connection, selCorrective)
                except:
                    print 'There is no input connected to this corrective'
                    pass
                else:
                    print 'Break Connection Action Canceled'

    def listBlendShapeNode(self, refreshCrInb=False, selectedBlendShape=None, arg=None):
        
        # Turn off checkButtom
        
        allBlendShapeNode = cmds.ls(type='blendShape')
        listSelection = cmds.ls(sl=True)
        listBlendShapeNode = []
        
        if listSelection:
            try:
                for obj in listSelection:
                    objHistory = cmds.listHistory(obj, pdo=True)
                    listBsNode = cmds.ls(objHistory, type='blendShape')
                    for node in listBsNode:
                        listBlendShapeNode.append(node)
            except:
                listBlendShapeNode.append('None')
            if not listBlendShapeNode:
                listBlendShapeNode = ['None']
        else:
            if len(allBlendShapeNode) == 0:
                listBlendShapeNode = ['None']
            else:
                for node in cmds.ls(type='blendShape'):
                    listBlendShapeNode.append(node)
      
        #=======================================================================
        # REFRESHING CURRENT MENU ITEMS
        #=======================================================================
        listCurrentMi = cmds.optionMenu(self.optionMenuGrpBlend, q=True, ill=True)
        if listCurrentMi:
            for mi in listCurrentMi:
                cmds.deleteUI(mi)   
                 
        for node in listBlendShapeNode:
            cmds.menuItem(label=str(node), parent=self.optionMenuGrpBlend)
           
        if selectedBlendShape:
            cmds.optionMenu(self.optionMenuGrpBlend, e=True, v=selectedBlendShape)
        # REFRESH CORRECTIVE LIST DURING THE REFRESH BUTTON ONLY
        if refreshCrInb: 
            self.refreshCrAndInbetweenList()
 
    def confirmDialogWin(self, **args):
        
        #print 'def confirmDialogWin'
        #=======================================================================
        # cmds.confirmDialog(title, 
        #                   message, 
        #                   button, 
        #                   defaultButton, 
        #                   cancelButton, 
        #                   dismissString)
        #=======================================================================
        return cmds.confirmDialog(**args)
        #return confirmResult
  
    
    def promptDialogWin(self, titleDialog='None',
                        instrunctions='Default',
                        text=None,
                        arg=None):
      
        #print 'def promptDialogWin'
        dialog = cmds.promptDialog(title=titleDialog,
                                   message=instrunctions,
                                   tx=text,
                                   button=['OK', 'Cancel'],
                                   defaultButton='OK',
                                   cancelButton='Cancel',
                                   dismissString='Cancel')

        if dialog == 'OK':
            text = cmds.promptDialog(query=True, text=True)
        else:
            text = None
       
        return text       
        
    def deleteCorrective(self, blendShapeNode=None,
                         correctiveName=None,
                         arg=None):
      
        #=======================================================================
        # AUTO INFO FROM UI STATEMENT
        #=======================================================================
        if not blendShapeNode:
            blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                             q=True,
                                             value=True)
        if not correctiveName:
            correctiveName = cmds.textScrollList(self.scrollCrList,
                                                 q=True,
                                                 si=True)
        allCr = cmds.textScrollList(self.scrollCrList,
                                                 q=True,
                                                 ai=True)

        # Check to see what InputConnection is..
        if not isinstance(correctiveName, list):
            correctiveName = [correctiveName]
        #=======================================================================
        dicCrGrpItem = self.getCrGrpItem()
        iTg = '%s.inputTarget[0]' %blendShapeNode

        if len(allCr) >= 2:
            for cr in correctiveName:
                comboNodes = ['blendColors', 'multiplyDivide', 'condition']
                # Check if there is a combo node attatched to it to be deleted
                # Combo correctives
                selCorrective = blendShapeNode + '.' + cr
                try:
                    InputConnection = cmds.listConnections(selCorrective, p=True)[0]
                    blendCrNode = InputConnection.split('.')[0]
                    for nodes in comboNodes:
                        if str(cmds.objectType(blendCrNode)) == nodes:
                            cmds.delete(blendCrNode)
                except:
                    pass
                
                # ----------- COMBO BLEND COLORS DELETED --------------------------
                correctiveItem = dicCrGrpItem[cr][1]
                #print 'allCrGrp.index(grp) ', dicCrGrpItem[cr][1]
                correctiveGroup = dicCrGrpItem[cr][0]
                #print 'dicCrGrpItem[cr][0] ', dicCrGrpItem[cr][0]
                iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
              
                blendShapeCorrective = blendShapeNode + '.' + cr
                inputAttrCnx = cmds.listConnections(blendShapeCorrective,
                                                    s=True,
                                                    d=True,
                                                    p=True)
                outputAttrCnx = cmds.listConnections(blendShapeCorrective,
                                                     s=False,
                                                     d=True,
                                                     p=True)
              
                try:
                    if inputAttrCnx:
                        cmds.disconnectAttr(inputAttrCnx[0], blendShapeNode + '.' + cr)
                    if outputAttrCnx:
                        cmds.disconnectAttr(outputAttrCnx, blendShapeNode + '.' + cr)
                except:
                    pass
              
                cmds.aliasAttr(blendShapeNode + '.' + cr, rm=True)
                removePath = blendShapeNode + '.weight[' + str(correctiveGroup) + ']'
                cmds.removeMultiInstance(removePath, b=True)
    
                for item in correctiveItem:
                    iTi = '.inputTargetItem[%s]' %item
                    gatherGroupCorrective = iTg + iTgGr + iTi
                    cmds.removeMultiInstance(gatherGroupCorrective, b=True)
                cmds.removeMultiInstance(iTg + iTgGr, b=True)
        else:
            print 'The last corrective cannot be deleted, instead delete the blendShape node specified'    
            
      
     
        self.refreshCrAndInbetweenList()
       
  
    def barMenuOptionsTools(self, command=None, arg=None):
        #print 'def barMenuOptionsTools'
        '''
        The mirror plane that will be used to check the symmetry is the same
        from the mirrorData tab options
        
        '''
        global globalMirrorSubList
        global previousMirrorPlane
        global previousTolerance
        
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        
        toleranceValueUi = cmds.floatField('tolField', q=True, value=True)
        
        if command == 1:
            valueMirrorPlane = cmds.radioButtonGrp('radioGroup', q=True, select=True)
            if valueMirrorPlane == 1:
                mirrorPlane = 'XY'
            elif valueMirrorPlane == 2:
                mirrorPlane = 'YZ'
            elif valueMirrorPlane == 3:
                mirrorPlane = 'XZ'
            
            # plane options inherited by the UI options
            if not globalMirrorSubList:
                globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                             mirrorPlane, 
                                                             tolerance=toleranceValueUi)
            elif previousMirrorPlane != mirrorPlane:
                    globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                                 mirrorPlane, 
                                                                 tolerance=toleranceValueUi)
            elif previousTolerance != toleranceValueUi:
                globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                                 mirrorPlane, 
                                                                 tolerance=toleranceValueUi)
            
            if (dslDo.checkMirrorList(blendShapeNode, globalMirrorSubList, 
                                      check=True, sectionSelection='unmatched')) == True:
                om.MGlobal.displayInfo('The geometry is symmetrical')
                
            previousMirrorPlane = mirrorPlane
            previousTolerance = toleranceValueUi
        
    def barMenuOptions(self, command=None, arg=None):
        #=======================================================================
        # 1 - Reset
        # 2 - Help
        # 3 - Quit
        #=======================================================================
        if command == 1: #RESET
            print 'reset'
            cmds.window('dsl_Sculpt_Inbetween_Editor', 
                        title=self.winName, 
                        e=True, 
                        wh=self.size)
        elif command == 2: #HELP
            webbrowser.open('http://www.danielslima.com/tools/sculpt-ibetween-editor-documentation-page/', 
                            new=0, autoraise=True)
        elif command  == 3: # QUIT
            cmds.deleteUI ('dsl_Sculpt_Inbetween_Editor', window=True)
            self.userCallback(cmd='remove')
        elif command  == 4: # ABOUT
            webbrowser.open('www.danielslima.com', new=0, autoraise=True)
        

  
    def renameCorrective(self, arg=None):
        #print 'def renameCorrective'
        
        #=======================================================================
        # AUTO INFO FROM UI STATEMENT
        #=======================================================================
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        selectedCr = cmds.textScrollList(self.scrollCrList,
                                         q=True,
                                         si=True)[-1]
        #=======================================================================
      
        newName = self.promptDialogWin(titleDialog='Rename',
                                       instrunctions='New Name:',
                                       text=selectedCr)
        if newName:
            if newName == selectedCr:
                print 'SAME NAME'
            else:
                cmds.aliasAttr(str(newName), str(blendShapeNode) + '.' + (selectedCr))
                cmds.text('headText' + selectedCr, e=True, label=str(newName))
                self.listCorrective(corrective=newName)
        
        #Refresh list Inbtween to avoid error restoring geo after renaming it
        self.listInbetween()
       
    def mirrorStringSide(self, selectedCr, arg=None):

        infoSide = []
        # Left & Right
        if 'Lf' in selectedCr[-2::]:
            selectedCr = selectedCr[:-2:]
            infoSide.append(selectedCr + 'Rt')
            infoSide.append('YZ')
            return infoSide
        elif 'Rt' in selectedCr[-2::]:
            selectedCr = selectedCr[:-2:]
            infoSide.append(selectedCr + 'Lf')
            infoSide.append('YZ')
            return infoSide
        else:
            om.MGlobal.displayError('The selected corrective must end with "Lf" or "Rt" to proceed with AutoMirror')
      
            
    def applyMirrorOptionData(self, fromCr=None, toCr=None, flipModel=True, 
                              posToNeg=True, copyMode=False, autoMirror=False):
        
        print 'def applyMirrorOptionData'
        # Gather all info from the MirrorData Tab and deal with it!
        #t = time.time()
        
        global globalMirrorSubList
        global previousMirrorPlane
        global previousTolerance

        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)

        valueMirrorPlane = cmds.radioButtonGrp('radioGroup', q=True, select=True)
        if valueMirrorPlane == 1:
            mirrorPlane = 'XY'
        elif valueMirrorPlane == 2:
            mirrorPlane = 'YZ'
        elif valueMirrorPlane == 3:
            mirrorPlane = 'XZ'

        # Querying values from ui
        posToNeg = cmds.checkBox('checkBox', q=True, value=True)
        dataType = cmds.radioButtonGrp('radioGrpDataOption', q=True, select=True)
        if dataType == 1:
            dataType = 'Deltas'
        elif dataType == 2:
            dataType = 'Corrective Weights'
        elif dataType == 3:
            dataType = 'Base Weights'
        
        if flipModel == True:
            userApply = 'Flip'
        else:
            userApply = 'Mirror'
        
        
        sourceCr = []
        destinationCr = []
        
        
        fromCr = cmds.textFieldButtonGrp('fromCr', q=True, text=True)
        toCr = cmds.textFieldButtonGrp('toCr', q=True, text=True)
        
        # If nothing in FromCr chose the corrective selected by user to be the fromCr
        if fromCr != '':
            sourceCr.append(fromCr)     
        else:
            fromCr = cmds.textScrollList(self.scrollCrList, q=True, si=True)[-1]
            sourceCr.append(fromCr)
        
        # Query tolerance form Ui    
        toleranceValueUi = cmds.floatField('tolField', q=True, value=True)
        
        #=======================================================================
        grpItem = self.getCrGrpItem(blendShapeNode, fromCr)[fromCr]
        sourceCr.append(grpItem)
        #=======================================================================
        if toCr != '':
            # If have some Cr inside textField
            destinationCr.append(toCr)
            
            if copyMode != True: 
                if not globalMirrorSubList:
                    globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                                 mirrorPlane, 
                                                                 tolerance=toleranceValueUi)
                elif previousMirrorPlane != mirrorPlane:
                        globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                                     mirrorPlane, 
                                                                     tolerance=toleranceValueUi)
                elif previousTolerance != toleranceValueUi:
                    globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                                     mirrorPlane, 
                                                                     tolerance=toleranceValueUi)
            ### Update Globals
            previousMirrorPlane = mirrorPlane
            previousTolerance = toleranceValueUi
                        

        else:
            if autoMirror:
                # Auto Mirror
                mirrorPlane = 'YZ'
                stringResult = self.mirrorStringSide(fromCr)
                if stringResult != None:
                    if previousMirrorPlane != mirrorPlane:
                        
                        globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                                     mirrorPlane='YZ', 
                                                                     tolerance=toleranceValueUi)
                    elif previousTolerance != toleranceValueUi:
                        globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                                     mirrorPlane, 
                                                                     tolerance=toleranceValueUi)
                    
                    if stringResult != None:
                        toCr = stringResult[0]
                        mirrorPlane = stringResult[1]
                        listCr = cmds.listAttr(blendShapeNode + '.weight', multi=True)
                        if toCr not in listCr:
                            self.addCorrective(newCorrectiveName=toCr,
                                               refreshLists=False,
                                               copyItself=True)
                        previousMirrorPlane = 'YZ'
                        destinationCr.append(toCr)
                        
                    ### Update Globals
                    previousMirrorPlane = mirrorPlane
                    previousTolerance = toleranceValueUi
                
                else:
                    sys.exit()
                
            else:
                # Corrective Selected
                if copyMode != True:
                    if not globalMirrorSubList:
                        
                        globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                                     mirrorPlane, 
                                                                     tolerance=toleranceValueUi)
                if previousMirrorPlane != mirrorPlane or previousMirrorPlane == None:
                    globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                                 mirrorPlane, 
                                                                 tolerance=toleranceValueUi)
                
                elif previousTolerance != toleranceValueUi:
                    #print '** previous: (%s) -----> Actual: (%s)' %(previousTolerance, toleranceValueUi)
                    globalMirrorSubList = dslDo.createMirrorList(blendShapeNode, 
                                                                     mirrorPlane, 
                                                                     tolerance=toleranceValueUi)
                
                
                toCr = cmds.textScrollList(self.scrollCrList, q=True, si=True)[-1]
                destinationCr.append(toCr)
                
                ### Update Globals
                previousMirrorPlane = mirrorPlane
                previousTolerance = toleranceValueUi
        # If does not end with Lf or Rt ends the tool        
        try:
            grpItem = self.getCrGrpItem(blendShapeNode, toCr)[toCr]
            destinationCr.append(grpItem)
        except:
            sys.exit()

        '''
        print '# previousMirrorPlane: ',previousMirrorPlane
        print '# mirrorPlane: ',mirrorPlane
        print '# posToNeg: ',posToNeg
        print '# 1 = Delta / 2 = crWeight / 3 = bsWeight | dataType: ',dataType
        print '# mirrorPlane: ', mirrorPlane
        print '# sourceCr ---------> ',sourceCr
        print '# destinationCr ----> ',destinationCr
        '''

        # If there is one field missing get the one selected
        if sourceCr[0] != '' and destinationCr[0] != '' and sourceCr[0] != destinationCr[0]:
            #print 'TEM CR VALIDO NO CAMPO!'
            if copyMode:
                userApply = 'Copy'
                
            userConfirm = cmds.confirmDialog(title='Confirm',
                                             button=['Yes', 'No'],
                                             defaultButton='Yes',
                                             cancelButton='No',
                                             dismissString='No',
                                             icn='question',
                                             message=('%s %s from [%s] to [%s]?' 
                                                      %(userApply, 
                                                        dataType, 
                                                        sourceCr[0], 
                                                        destinationCr[0])))
            
            #print '--------------------USER--------------> ', userConfirm
            if userConfirm == 'Yes':
                
                #===================================================================
                # PROPER CLEAR ALL ITEMS ON CR DESTINATION: 
                #===================================================================
                fromCrItems = sourceCr[-1][-1]
                toCrItems = destinationCr[-1][-1]
                    
                if 6000 in toCrItems:
                    toCrItems.pop()
                
                # Deleting Items from destination before the items from ToCr get placed
                for i in toCrItems:
                    if i not in fromCrItems:
                        self.deleteInbetween(blendShapeNode, 
                                             correctiveName=destinationCr[0],
                                             correctiveItem=i)
                
                for i in fromCrItems:
                    dataFromCr =  self.getCrPointData(blendShapeNode, 
                                                      sourceCr[0], 
                                                      correctiveItem=i)
                    self.newInbetween(blendShapeNode, 
                                      destinationCr[0], 
                                      newcorrectiveItem=i, 
                                      pointArray=dataFromCr.values()[0][0], 
                                      componentList=dataFromCr.values()[0][1])
                
                if copyMode != True:
                    if autoMirror:
                        mirrorPlane = 'YZ'
                        self.mirrorCrIndices(blendShapeNode, toCr, flipModel, mirrorPlane, posToNeg)
                    else:
                        self.mirrorCrIndices(blendShapeNode, toCr, flipModel, mirrorPlane, posToNeg)
    
                self.refreshCrAndInbetweenList(corrective=destinationCr[0])
                
            else:
                print 'Creation of (%s) has been canceled by user' %toCr
                self.deleteCorrective(blendShapeNode, correctiveName=toCr)
            
            previousMirrorPlane = mirrorPlane
            
                
            
        else:
            #print 'APLICA NO SELECIONADO'
            selectedCr = cmds.textScrollList(self.scrollCrList,
                                         q=True,
                                         si=True)[-1]
            
            grpItem = self.getCrGrpItem(blendShapeNode, selectedCr)[selectedCr]
            correctiveGroup = grpItem[0]
            selectedCrItem = grpItem[1]

            if dataType == 'Deltas':
                self.mirrorCrIndices(blendShapeNode, selectedCr, flipModel, mirrorPlane, posToNeg)
                #===============================================================
                previousMirrorPlane = mirrorPlane
                #===============================================================
            elif dataType == 'Corrective Weights':
                #print 'MIRROR CORRECTIVE WEIGHTS'
                dslDo.mirrorTargetWeights(blendShapeNode, 
                                          correctiveGroup, 
                                          mirrorPlane, 
                                          posToNeg=posToNeg, 
                                          flipModel=flipModel, 
                                          tolerance=0.00001, 
                                          mirrorList=globalMirrorSubList,
                                          getMode='getTargetWeights',
                                          applyMode='applyTargetWeights')
                #===============================================================
                previousMirrorPlane = mirrorPlane
                #===============================================================
                
            elif dataType == 'Base Weights':
                #print 'MIRROR BLENDSHAPE NODE WEIGHTS'

                previousMirrorPlane = mirrorPlane
                
                dslDo.mirrorTargetWeights(blendShapeNode, 
                                          correctiveGroup, 
                                          mirrorPlane, 
                                          posToNeg=posToNeg, 
                                          flipModel=flipModel, 
                                          tolerance=0.00001, 
                                          mirrorList=globalMirrorSubList,
                                          getMode='getBaseWeights',
                                          applyMode='applyBaseWeights')
                #===============================================================
                previousMirrorPlane = mirrorPlane
                #===============================================================
                
            
                
    def mirrorCrIndices(self, blendShapeNode, selectedCr, flipModel, mirrorPlane, posToNeg, arg=None):
        
        global globalMirrorSubList
        global previousMirrorPlane
        
        #t = time.time()
 
        grpItem = self.getCrGrpItem(blendShapeNode, selectedCr)[selectedCr]
        selectedCrGroup = grpItem[0]
        selectedCrItem = grpItem[1]
        
        # StatusBar Creation
        # labelText = 'Mirroing Delta Item: %s' %selectedCrItem[0]
        dslDo.statusBarWindow(maxValue=len(selectedCrItem))
        cmds.refresh()
        
        for item in selectedCrItem:
            labelText = 'Mirroing Delta Item: %s' %item
            dslDo.statusBarWindow(edit=True, step=1, text=labelText)

            dslDo.mirrorCorrectiveData(blendShapeNode, 
                                       correctiveGroup=selectedCrGroup, 
                                       correctiveItem=item,
                                       mirrorPlane=mirrorPlane, 
                                       posToNeg=posToNeg, 
                                       flipModel=flipModel, 
                                       tolerance=0.00001,
                                       mirrorList=globalMirrorSubList)

        
        previousMirrorPlane = mirrorPlane 
        dslDo.statusBarWindow(selfDelete=True)
        #print "Time Auto Mirror Delta: %s" %(time.time() - t)
                                                              
    
    def duplicateCorrective(self, mirroed=False, arg=None):
        #print 'def duplicateCorrective'
        
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        
        selectedCr = cmds.textScrollList(self.scrollCrList,
                                         q=True,
                                         si=True)[-1]
        

        newCorrectiveName = self.promptDialogWin(titleDialog='Duplicate',
                                                 instrunctions='New Name:',
                                                 text=selectedCr)
        
        
        allCr = self.listCorrective()
        # If the respective duplication CR does not exist, proceed with this...
        if (newCorrectiveName != selectedCr and newCorrectiveName != None 
            and newCorrectiveName not in allCr):
            
            
            # Add new blendShape and store in a variable it's correctiveGroup
            self.addCorrective(newCorrectiveName=newCorrectiveName,
                               refreshLists=False,
                               copyItself=True)
            listCorrectiveItem = self.getCrGrpItem()[str(selectedCr)][1]
            for item in listCorrectiveItem:
               
                dataInfo = self.getCrPointData(blendShapeNode,
                                               correctiveName=selectedCr,
                                               correctiveItem=item)
               
                pointArray = dataInfo.values()[0][0]
                componentList = dataInfo.values()[0][1]
                
                                
                self.newInbetween(blendShapeNode,
                                  correctiveName=newCorrectiveName,
                                  newcorrectiveItem=item,
                                  mesh=None,
                                  pointArray=pointArray,
                                  componentList=componentList)
                
#                #===============================================================
#                # CHECKING NEW PASTE DATA TO CONFIRM 
#                #===============================================================
#                pastedDataInfo = self.getCrPointData(blendShapeNode,
#                                                     correctiveName=newCorrectiveName,
#                                                     correctiveItem=item)
#                pastedPointArray = pastedDataInfo.values()[0][0]
#                pastedComponentList = pastedDataInfo.values()[0][1]
#                print pastedPointArray
#                print pastedComponentList
#                if pastedPointArray == None and pastedComponentList == None:
#                    self.resetDataCr(correctiveItem=item)
                
               
            # Delete the last if the selected one does not have the 6000 because
            # the last item of the new one needed to be 6000 when it's created.
            if listCorrectiveItem[-1] != 6000:
                self.deleteInbetween(blendShapeNode, 
                                     correctiveName=newCorrectiveName,
                                     correctiveItem=str(6000))
        
        # If the respective duplication CR aready exist, proceed with this...
        elif (newCorrectiveName != selectedCr and newCorrectiveName != None 
              and newCorrectiveName in allCr):
            
            listCorrectiveItem = self.getCrGrpItem()[str(selectedCr)][1]
            mirrorListCorrectiveItem = self.getCrGrpItem()[str(newCorrectiveName)][1]
            for item in listCorrectiveItem:
                dataInfo = self.getCrPointData(blendShapeNode,
                                            correctiveName=selectedCr,
                                            correctiveItem=item)
               
                pointArray = dataInfo.values()[0][0]
                componentList = dataInfo.values()[0][1]
                self.newInbetween(blendShapeNode,
                                  correctiveName=newCorrectiveName,
                                  newcorrectiveItem=item,
                                  mesh=None,
                                  pointArray=pointArray,
                                  componentList=componentList)
            
            # Delete the ones that are not in the selectedCr...
            for item in mirrorListCorrectiveItem:
                if item not in listCorrectiveItem:
                    self.deleteInbetween(blendShapeNode, 
                                         correctiveName=newCorrectiveName,
                                         correctiveItem=item)

        # RefreshAll
        self.refreshCrAndInbetweenList(corrective=newCorrectiveName)
   
    def addBlendShapeDef(self, arg=None):
       
        #print 'def addBlendShapeNode'
        
        objectList = cmds.ls(sl=True)
        # Check if there is something selected
        if len(objectList) == 0:
            # Query object form UI
            try:
                defModel = cmds.optionMenu(self.optionMenuGrpBlend, 
                                           q=True, value=True)
                geo = self.getGeoNameFromNode(blendShapeNode=defModel)
                defaultShape = cmds.duplicate(geo)[0]
            except:
                print 'Selection Failed!!'
                pass
            
        else:
            geo = objectList[0]
            # Check if the object has some skinClusterDef
            try:
                defModel = cmds.ls(cmds.listHistory(geo), et='skinCluster')
                defaultShape = self.originalShape(blendShapeNode=defModel, 
                                                  newName='Original')
            except:
                defaultShape = cmds.duplicate(geo)[0]
                pass
                

        try:
            newBlendShapeNode = cmds.blendShape(defaultShape, 
                                                geo, 
                                                foc=True, 
                                                w=[0, 0], 
                                                n='blendShape' + geo.capitalize())[0]
            cmds.delete(defaultShape)
            
            
            self.listBlendShapeNode(refreshCrInb=True, 
                                    selectedBlendShape=newBlendShapeNode)
            self.listCorrective()
        except:
            print 'Select Something'

    def addShape(self, blendShapeNode=None, correctiveName=None, 
                 mode='Inbetween', correctiveItem=None, arg=None):
        
        # Open Chunk UNDO 
        cmds.undoInfo(openChunk=True)
        
        
        presentSel = cmds.ls(sl=True)
        #From component mode to Object Mode
        cmds.selectMode(component=True )
        cmds.selectMode(object=True )
        
        # Check SculptON / OFF state
        sculptModeSt = cmds.iconTextCheckBox(self.bCreateScultGeo, q=True, value=True)
        
        # Check SculptON for conditions
        if sculptModeSt == True:
            
            
            blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                             q=True,
                                             value=True)
            geo = self.getGeoNameFromNode(blendShapeNode)
            userSculptGeo = cmds.ls(geo + '_GeoSculpt')[0]
            if userSculptGeo == []:
                sculptGeo = geo
            else:
                sculptGeo = cmds.duplicate(userSculptGeo)[0]
                self.resetSculpt(geo)
            
        else:
            sculptGeo = cmds.ls(sl=True)[0]
            if cmds.objectType(sculptGeo) != 'transform':
                sculptGeo = cmds.pickWalk(d='Up')[0]

        selShapeObj = cmds.listRelatives(sculptGeo, s=True, ni=True)[0]
        selShapeObj = '%s|%s' %(sculptGeo, selShapeObj)
        if not blendShapeNode:
            blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                             q=True, value=True)
        if not correctiveName:
            correctiveName = cmds.textScrollList(self.scrollCrList,
                                                 q=True, si=True)[0]
            correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
        
        skinGeo = self.getGeoNameFromNode(blendShapeNode)
        if correctiveItem == None:
            crValue = round(cmds.getAttr(str(blendShapeNode) + '.' + correctiveName), 3)
            correctiveItem = int((crValue * 1000) + 5000)
            print 'crValue: ', crValue
        ## Check if there's an geo connected to apply otherwise the calculation
        ## will be overwritten by this geo // Action: Delete Geo

        mesh = None
        if mesh:
            print 'Mesh deleted before perform inverse calculation: ', mesh
            cmds.delete(mesh[0])
        
        '''
        print '------addShape--------'
        print 'skinGeo: ', skinGeo
        print 'sculptGeo: ', sculptGeo
        print 'blendShapeNode: ', blendShapeNode
        print 'correctiveGroup: ', correctiveGroup
        print 'correctiveName: ', correctiveName
        #print 'crValue: ', crValue
        print '-----addShape---------'
        '''
        
        #=======================================================================
        # SAVING DATA WEIGTS / BASE & TARGET
        #=======================================================================
        tmpTgtWeights = dslDo.getApplyPI(blendShapeNode, 
                                         correctiveGroup, 
                                         correctiveItem,
                                         mode='getTargetWeights')
        
        tmpBsWeights = dslDo.getApplyPI(blendShapeNode, 
                                        correctiveGroup, 
                                        correctiveItem,
                                        mode='getBaseWeights')
        
        #=======================================================================
        # WIPE OUT DATA WEGIHTS / BASE & TARGET            
        #=======================================================================
#        dslDo.wipeOutWeights(blendShapeNode, 
#                             correctiveGroup, 
#                             correctiveItem, 
#                             type='wipeTargetWeights')
        
        keepSculpt = cmds.checkBox(self.keepS, q=True, value=True)
        if sculptGeo != skinGeo:
            if cmds.objectType(selShapeObj) == 'mesh':
                
                '''
                print '================='
                print 'skinGeo ', skinGeo
                print 'sculptGeo ',sculptGeo
                print 'blendShapeNode ',blendShapeNode
                print 'correctiveGroup ',correctiveGroup
                print 'correctiveName ',correctiveName
                print 'correctiveItem ',correctiveItem
                print '================='
                '''
                
                if mode == 'Inbetween':
                    # Zero Delta before revert calculate the sculpt Geo
                    self.resetDataCr(correctiveItem)
                    dslRs.dslCorrectiveShape(skinGeo,
                                             sculptGeo,
                                             blendShapeNode,
                                             correctiveGroup,
                                             correctiveName,
                                             correctiveItem,
                                             inBetweenMode=True,
                                             keepSculpt=keepSculpt)

                    # Refresh inBetween list after perform any of the addShape buttons
                    self.listInbetween()
                if mode == 'Projection':
                    # Zero Delta before revert calculate the sculpt Geo
                    self.resetDataCr(correctiveItem)
                    dslRs.dslCorrectiveShape(skinGeo,
                                             sculptGeo,
                                             blendShapeNode,
                                             correctiveGroup,
                                             correctiveName,
                                             correctiveItem,
                                             inBetweenMode=False,
                                             keepSculpt=keepSculpt)
                    # Refresh inBetween list after perform any of the addShape buttons
                    self.listInbetween()
               
                if mode == 'Flatten':
                    # Zero Delta before revert calculate the sculpt Geo
                    self.resetDataCr(correctiveItem)
                    dslRs.dslCorrectiveShape(skinGeo,
                                             sculptGeo,
                                             blendShapeNode,
                                             correctiveGroup,
                                             correctiveName,
                                             correctiveItem,
                                             inBetweenMode=True,
                                             flatten=True,
                                             keepSculpt=keepSculpt)
                    # Refresh inBetween list after perform any of the addShape buttons
                    self.listInbetween()
               
                if mode == 'Basic':
                    
                    correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
                    cmds.blendShape(blendShapeNode,
                                    e=True,
                                    tc=True,
                                    ib=True,
                                    t=[skinGeo, correctiveGroup, 
                                       sculptGeo, 
                                       crValue])
                    # Refresh inBetween list after perform any of the addShape buttons
                    self.listInbetween()
                   
                if mode == 'Replace':
                    # Zero Delta before revert calculate the sculpt Geo
                    self.resetDataCr(correctiveItem)
                    dslRs.dslCorrectiveShape(skinGeo,
                                             sculptGeo,
                                             blendShapeNode,
                                             correctiveGroup,
                                             correctiveName,
                                             correctiveItem,
                                             inBetweenMode=True,
                                             flatten=False,
                                             keepSculpt=True)
               
                    # Do not Refresh inBetween list after perform Replace
                    # otherwise Maya will crash
            else:
                print 'Only Polygons is available to be reversed'
        else:
            sculptGeo = cmds.duplicate(sculptGeo)[0]
            dslRs.dslCorrectiveShape(skinGeo,
                                     sculptGeo,
                                     blendShapeNode,
                                     correctiveGroup,
                                     correctiveName,
                                     correctiveItem,
                                     inBetweenMode=True)
            self.listInbetween()
            cmds.select(skinGeo)
            print 'Sculped shape cannot be the same skinned Geometry'
            #===================================================================
        #=======================================================================
        # APPLY BACK DATA WEIGHTS
        #=======================================================================


        dslDo.getApplyPI(blendShapeNode, 
                         correctiveGroup, 
                         correctiveItem,
                         mode='applyTargetWeights',
                         weightData=tmpTgtWeights)
        dslDo.getApplyPI(blendShapeNode, 
                         correctiveGroup, 
                         correctiveItem,
                         mode='applyBaseWeights',
                         weightData=tmpBsWeights)
        
        cmds.undoInfo(closeChunk=True)
        
        # Maintain original selection
        # In case the user wants to add a inbetween from a separed geo pose and
        # "Keep Sculpt Geometry" is not checked do not error here
        try:
            cmds.select(presentSel)
        except:
            pass
        
    def copyPose(self, arg=None):
        #print 'def copyPose'
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True, si=True)[0]
        
        numberValue = str(cmds.floatSliderButtonGrp(self.liveSlide, 
                                                    q=True, 
                                                    value=True))
        curValue = numberValue.split('.')
        geoName = self.getGeoNameFromNode(blendShapeNode)
        
        copyGeoName = correctiveName + '_' + curValue[0] + '_' + curValue[-1]
        copyGeo = cmds.duplicate(geoName, name=copyGeoName)[0]
        shapeGeo = cmds.pickWalk(copyGeo, d='down' )[0]

        cmds.rename(str(shapeGeo), str(copyGeo) + 'Shape')
        cmds.editDisplayLayerMembers("defaultLayer", 
                                     copyGeo, 
                                     noRecurse=True)
        # Unlock Channel box attrs
        for attr in 'trs':
            for axis in 'xyz':
                #print '%s.%s%s' %(copyGeoName, attr, axis)
                cmds.setAttr('%s.%s%s' %(copyGeoName, attr, axis), l=False)
                
        # Try to unparent the copyGeo
        try:
            cmds.parent(copyGeoName, w=True)
        except:
            print 'copyGeo already belong to world'
            pass
        
        cmds.select(copyGeoName)
            
            
               
    def addCorrective(self, newCorrectiveName=None,
                      refreshLists=True,
                      copyItself=False,
                      arg=None):
      
        #print 'def addCorrective'
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
       
       
        if blendShapeNode != str(None):
            checkCrExistence = cmds.textScrollList(self.scrollCrList,
                                                   q=True,
                                                   si=True)
            if checkCrExistence:
                geo = self.getGeoNameFromNode(blendShapeNode)
                if not newCorrectiveName:
                    newCorrectiveName = self.promptDialogWin(titleDialog='Add Corrective',
                                                             instrunctions='Name:')
                    #newCorrectiveName = '%s|%s' %(geo, newCorrectiveName)
                if newCorrectiveName != None:
                    if copyItself == True:
                        newCorrectiveGeo = self.originalShape(blendShapeNode, 
                                                              newName=newCorrectiveName)
                        #newCorrectiveGeo = cmds.duplicate(geo, n=newCorrectiveName)[0]
                        
                        
                    else:
                        newCorrectiveGeo = self.originalShape(blendShapeNode,
                                                              newName=newCorrectiveName,
                                                              visibility=False)

                    # Get All Grp
                    groupsUnsorted = []
                    dicValues = self.getCrGrpItem().values()
                    for grp in dicValues:
                        groupsUnsorted.append(grp[0])
                   
                    groups = list(sorted(set(groupsUnsorted))) 
                    # Try to find the next available group, in case that doesn't
                    # exist any just ignore it and add to the first group 0
                    try:
                        for correctiveGroup in groups:
                            #print correctiveGroup
                            if correctiveGroup + 1 not in groups:
                                availableGrp = correctiveGroup + 1
                                cmds.blendShape(blendShapeNode,
                                                e=True,
                                                t=[str(geo), int(availableGrp),
                                                   newCorrectiveGeo, 1.0])
                                #print '----- Next Available Grp Is ----> ', availableGrp
                                break
                   
                    # Add as the fist group created Zero
                    except:
                        
                        cmds.blendShape(blendShapeNode,
                                        e=True,
                                        t=[str(geo),
                                           int(0),
                                           newCorrectiveGeo, 1.0])
                        pass
                   
                if newCorrectiveName != None:
                    if refreshLists:
                        # Check this later
                        self.refreshCrAndInbetweenList(corrective=newCorrectiveGeo)
                    cmds.delete(newCorrectiveGeo)
           
           
        else:
           
            print 'NO BLENDSHAPE NODE SELECTED'
       
          
    def cleanNoData(self, blendShapeNode=None, arg=None):
       
        #print 'def cleanNoData'
        # Clean corrective that doesn't have any data into they group
       
        if not blendShapeNode:
            blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                             q=True,
                                             value=True)
      
        # Get All Grp
        groups = []
        dicValues = self.getCrGrpItem().values()
        for grp in dicValues:
            groups.append(grp[0])
       
        listCr = cmds.listAttr(blendShapeNode + '.weight', multi=True)
       
        # Removing the aliasTrash ex: ".weight[4]"
        try:
            for cr in listCr:
                if 'weight[' in str(cr):
                    cmds.removeMultiInstance(blendShapeNode + '.' + cr)
        except:
            pass
       
        for grp in groups:
            iTg = '%s.inputTarget[0]' %blendShapeNode
            iTgGr = '.inputTargetGroup[%s]' %grp
            iTi = '.inputTargetItem'
            gatherGroupCorrective = iTg + iTgGr + iTi
            if cmds.getAttr(gatherGroupCorrective, mi=True) == None:
                print '------------DELETED---------->: ', gatherGroupCorrective
                cmds.removeMultiInstance(iTg + iTgGr, b=True)
      

    def getGeoNameFromNode(self, blendShapeNode=None, arg=None):
       
        # Give the blendShapeNode and it'll be returned the name of the Geometry
      
        hist = cmds.listHistory(blendShapeNode, f=True)
        #shapeGeo = cmds.ls(hist, type='mesh', long=True)
        #geoName = cmds.listRelatives(shapeGeo, ap=True, f=True)[0]
        shapeGeo = cmds.ls(hist, type='mesh')[0]
        geoName = cmds.listRelatives(shapeGeo, ap=True)[0]
        #print 'def getGeoNameFromNode'
        shapeGeoSplit = shapeGeo.split('|')[-1]
        if str(shapeGeoSplit) == str(geoName):
            #print '========> shapeGeo: ',shapeGeo
            #print '========> geoName: ',geoName
            cmds.rename(shapeGeo, str(shapeGeoSplit) + 'Shape')
        
        return geoName

    def getCrGrpItem(self, blendShapeNode=None,
                       correctiveName=None,
                       arg=None):
       
       
        #print 'def getCrGrpItem'
        # New function with Dictionary to substitute some getGroupCr
        # If there is no corrective, try to don't fail the ui and show NONE
        #=======================================================================
        # try:
        #    self.cleanNoData()
        # except:
        #    pass
        #=======================================================================
       
        if not blendShapeNode:
            blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend, q=True, 
                                             value=True)
        if not correctiveName:
            correctiveName = cmds.textScrollList(self.scrollCrList, q=True, 
                                                 si=True)[0]
        #print 'blendShapeNode: ', blendShapeNode
        #print 'correctiveName: ', correctiveName
        #=======================================================================
        # BLENDSHAPE PATH
        #=======================================================================
        iTg = '%s.inputTarget[0]' %blendShapeNode
        iTi = '.inputTargetItem'
        dicCrGrp = {}
        allCrName = cmds.listAttr(blendShapeNode + '.weight', m=True)
        allCrGrp = cmds.getAttr(blendShapeNode + '.weight', mi=True)
        for nm in allCrName:
            dicCrGrp[nm] = allCrGrp[allCrName.index(nm)]
        '''
        print 'dicCrGrp --> ', dicCrGrp
        print '---dicCrGrp.keys()> ', dicCrGrp.keys()
        print '---dicCrGrp.values()> ', dicCrGrp.values()
        print '---dicCrGrp["teste"]> ', dicCrGrp['teste']
        '''
        dicCrGrpItem = {}
        for crName in dicCrGrp.keys():
            iTgGr = '.inputTargetGroup[%s]' %dicCrGrp[crName]
            grpItem = cmds.getAttr(iTg + iTgGr + iTi, mi=True)
            if grpItem == None:
                print '*** corrective: %s has no item, restauring...' %correctiveName
                cmds.getAttr(iTg + iTgGr + '.inputTargetItem[6000].inputGeomTarget')
                cmds.getAttr(iTg + iTgGr + '.inputTargetItem[6000].inputPointsTarget')
                cmds.getAttr(iTg + iTgGr + '.inputTargetItem[6000].inputComponentsTarget')
                grpItem = [6000]
                dicCrGrpItem[crName] = (dicCrGrp[crName], grpItem)
            dicCrGrpItem[crName] = (dicCrGrp[crName], grpItem)
        #print 'dicCrGrpItem----------> ', dicCrGrpItem
        return dicCrGrpItem

    def originalShape(self, blendShapeNode=None, newName=None, 
                      visibility=True, offset=[0, 0, -10], 
                      verbose=True, arg=None):
       
        # Extract the original shape of the geometry and return the name of it.
        # This same geometry requires to have an blendShapeNode otherwise
        # will result in failure.

        geo = self.getGeoNameFromNode(blendShapeNode)
        
        origShape = cmds.ls(cmds.listHistory(blendShapeNode),
                             et='mesh', intermediateObjects=True, long=True)[0]

        restoredGeo = cmds.duplicate(geo, name=newName)[0]
        tmpShape = cmds.pickWalk(restoredGeo, d='down' )[0]
        resGeoShape = restoredGeo + 'Shape'
        cmds.rename(tmpShape, resGeoShape)

        
        cmds.connectAttr(origShape + '.outMesh', resGeoShape + '.inMesh')
        cmds.refresh()
        cmds.disconnectAttr(origShape + '.outMesh', resGeoShape + '.inMesh')
        
        # Unlock channels
        xyz = 'xyz'
        trs = 'trs'
        for m in trs:
            for a in xyz: 
                cmds.setAttr(restoredGeo + '.%s%s' %(m, a), l=False)
        cmds.xform(restoredGeo, t=offset)
        cmds.select(cl=True)
        return restoredGeo

    def restoreCorrective(self, blendShapeNode=None,
                         correctiveName=None,
                         correctiveItem=None,
                         pruneDelta=0,
                         bruteForce=False,
                         verbose=True,
                         arg=None):
       
        #print 'def restoreCorrective'
        # Restore the corrective from the item selected in the inbetween list.
        #=======================================================================
        # AUTO INFO FROM UI STATEMENT
        #=======================================================================
        if not blendShapeNode:
            blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                             q=True,
                                             value=True)
        if not correctiveName:
            correctiveName = cmds.textScrollList(self.scrollCrList,
                                                 q=True,
                                                 si=True)[0]
        #=======================================================================
        correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
        iTg = '%s.inputTarget[0]' %blendShapeNode
        iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
        iTi = '.inputTargetItem[%s]' %correctiveItem
        iGt = '.inputGeomTarget'
        iPt = '.inputPointsTarget'
        iCt = '.inputComponentsTarget'
      
        gatherMesh = iTg + iTgGr + iTi + iGt
        blendInbDataAddress = '.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000]'
        checkGeoExistence = cmds.listConnections(gatherMesh)
        #=======================================================================
        # IN BRUTEFORCE MODE THE USER CAN SPECIFY THE PRUNE VALUE FOR THE TARGET
        #=======================================================================
        dataInfo = self.getCrPointData(blendShapeNode,
                                       correctiveName,
                                       correctiveItem)

        delta = dataInfo.values()[0][0]
        vtxUnflatten = dataInfo.values()[0][1]       
       
        # Changing Name to the respective ITEM
        if correctiveItem != str(6000):
            correctiveName = correctiveName + str(correctiveItem)
        #=======================================================================
        # BRUTE FORCE OFF - OBSOLETE
        #=======================================================================
        if bruteForce:
            if verbose: '# Brute Force ON'
            ### IF THE GEOMETRY EXIST, THEN SELECT
            if checkGeoExistence:
                cmds.select(checkGeoExistence[0])
            else:
                restoredGeo = self.originalShape(blendShapeNode, 
                                                 newName=correctiveName)
                print '.........BRUTE FORCE..........', restoredGeo
                if delta:
                    cmds.select(d=True)
                    for v in vtxUnflatten:
                        cmds.select(correctiveName + '.' + str(v), add=True)
                    vtx = cmds.ls(sl=True, fl=True)
                    #===========================================================
                    # PRUNING POINTARRAY VALUES
                    #===========================================================
                    prunedArray = self.utilPrunePointArray(pointArray=delta,
                                                           pruneDelta=pruneDelta)
                    for value in range(len(prunedArray)):
                        cmds.xform(vtx[value], r=True, t=(prunedArray[value][0],
                                                          prunedArray[value][1],
                                                          prunedArray[value][2]))
                    cmds.connectAttr(restoredGeo + '.worldMesh[0]',
                                     gatherMesh, force=True)  
        
        #=======================================================================
        # BRUTE FORCE ON // No prune values
        #=======================================================================
        else:
            if verbose: '# Brute Force OFF'
            if checkGeoExistence:
                restoredGeo = checkGeoExistence[0]
                cmds.select(restoredGeo)
                return restoredGeo
            else:
                restoredGeo = self.originalShape(blendShapeNode, newName=correctiveName)
                if delta:
                    restoreGeoShape = cmds.listRelatives(restoredGeo, s=True, ni=True, typ='mesh')[0]
                    blendInbNode = cmds.deformer(restoredGeo,
                                                 type='blendShape',
                                                 name=('blendShape' +
                                                       restoredGeo.capitalize()),
                                                 foc=True)[0]
                    cmds.blendShape(blendInbNode,
                                    e=True,
                                    t=[restoredGeo, 0, restoredGeo, 1])
                    fromGeo = str(restoreGeoShape) + '.worldMesh[0]'
                    fromNode = blendInbNode + blendInbDataAddress + iGt
                    cmds.disconnectAttr(fromGeo, fromNode)
                    cmds.setAttr(blendInbNode + '.%s' %restoredGeo, 1)
                    deltaPath = blendInbNode + blendInbDataAddress
                    cmds.setAttr(deltaPath + iPt,
                                 type='pointArray',
                                 *delta)
                    cmds.setAttr(deltaPath + iCt,
                                 type='componentList',
                                 *vtxUnflatten)
                cmds.connectAttr(restoredGeo + '.worldMesh[0]',
                                 gatherMesh,
                                 force=True)
                
                om.MGlobal.displayInfo('Corrective "%s" Restored!' %restoredGeo)
                
                return restoredGeo
        
    def selectCorrective(self, nameInbSlider=None, verbose=False, arg=None):
       
        #print 'def selectCorrective'
        # This function is a wraper for the restoreCorrective func.
        # This function is called into the button 'Select' of
        # each item.
      
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True,
                                             si=True)[0]     
        correctiveItem = nameInbSlider[-4:]
        restoredGeo = self.restoreCorrective(blendShapeNode,
                                              correctiveName,
                                              correctiveItem,
                                              bruteForce=False)  
        
        if verbose: print '%s RESTORED!' %restoredGeo
        cmds.select(restoredGeo)

    def copyPasteInbetween(self, nameInbSlider=None, deletePrev=True, 
                           closeChunk=False, arg=None):
       
        #print 'def copyPasteInbetween'
        # Perform copying, pasting to the new item Number and deleting the previous
        # left over item.  Peform to change the position of the item in the slider
        # of each ibetween list
       
        global undoState
       
        # Check if the undo chunk has been opened before to proper the undo
        # None mean undo state is closed
        # 1 mean undo state in opened // The flag closeChunk is used only to the
        # changeCommand flag into the each respective floatSliderButtonGrp
       
        if undoState == None:
            undoState = 1
            cmds.undoInfo(openChunk=True)

        #=======================================================================
        # AUTO INFO FROM UI STATEMENT
        #=======================================================================
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True,
                                             si=True)[0]     
        #=======================================================================
        correctiveItem = cmds.floatSliderButtonGrp(nameInbSlider,
                                                   q=True,
                                                   label=True)
        crSlideValue = cmds.floatSliderButtonGrp(nameInbSlider,
                                                 q=True,
                                                 value=True)
        newcorrectiveItem = str(int((crSlideValue * 1000) + 5000))
        newMeshName = correctiveName + str(newcorrectiveItem)
        
        dataInfo = self.getCrPointData(blendShapeNode,
                                       correctiveName,
                                       correctiveItem)
        mesh = dataInfo.keys()
        pointArray = dataInfo.values()[0][0]
        componentList = dataInfo.values()[0][1]

        #===================================================================
        # APPLYING DATA
        #===================================================================
        if pointArray and componentList:
            # UPDATE POPUP MENUS:
            cmds.menuItem('popReplace' + nameInbSlider, e=True,
                          c=partial(self.addShape, None, mode='Replace',
                          correctiveItem=correctiveItem))
            cmds.menuItem('popCopy' + nameInbSlider, e=True, 
                          c=partial(self.copyDataCr, newcorrectiveItem))
            cmds.menuItem('popPaste' + nameInbSlider, e=True, 
                          c=partial(self.pasteDataCr, newcorrectiveItem))
            cmds.menuItem('popZero' + nameInbSlider, e=True, 
                          c=partial(self.resetDataCr, newcorrectiveItem))
            cmds.menuItem('popDelta' + nameInbSlider, e=True, 
                          c=partial(self.seeDelta, newcorrectiveItem))
            cmds.menuItem('popTools' + nameInbSlider, e=True, 
                          c=partial(self.itemToTools, int(newcorrectiveItem)))
            cmds.floatSliderButtonGrp(nameInbSlider,
                                      edit=True,
                                      label=newcorrectiveItem,
                                      symbolButtonCommand=partial(self.deleteInbetween,
                                                                  correctiveItem=newcorrectiveItem,
                                                                  deleteSlider=True),
                                      buttonCommand=partial(self.selectCorrective,
                                                            newMeshName))
            self.deleteInbetween(blendShapeNode, correctiveName, correctiveItem)
            self.newInbetween(blendShapeNode, correctiveName, newcorrectiveItem,
                              mesh, pointArray, componentList)
        else:
            om.MGlobal.displayInfo('There is no Delta yet on this Corrective Item') 
            pValue = float(int(correctiveItem) - 5000) / 1000
            cmds.floatSliderButtonGrp(nameInbSlider, edit=True, value=pValue)
        
        if cmds.radioButtonGrp('radioGrpItem', q=True, select=True) == 2:
            cmds.radioButtonGrp('radioGrpItem', e=True, select=1)
            self.stateSelectToolBt(True, arg)
            self.intFieldChange(arg) 
        
        # Refresh
        cmds.refresh()
        # Check if the undo chunk has been opened before to proper the undo
        if closeChunk == True:
            undoState = None
            cmds.undoInfo(closeChunk=True)

    def deleteInbetween(self, blendShapeNode=None,
                        correctiveName=None,
                        correctiveItem=None,
                        deleteSlider=False,
                        arg=None):
       
        #print 'def deleteInbetween'
        # Delete inbetween item
        
        if not blendShapeNode:
            blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend, q=True,
                                             value=True)
        if not correctiveName:
            correctiveName = cmds.textScrollList(self.scrollCrList, q=True,
                                                 si=True)[0]
       
        correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
        iGt = '.inputGeomTarget'
        gatherInfoFromDelta = ('%s.inputTarget[0].inputTargetGroup[%s].inputTargetItem[%s]'
                               %(blendShapeNode,
                                 correctiveGroup,
                                 correctiveItem))
       
        # Try disconnecting Mesh to undo properly, if there is no geometry, pass
        try:
            meshConnected = cmds.listConnections(gatherInfoFromDelta + iGt)[0]
            getGeoShape = cmds.listRelatives(restoredGeo, s=True, ni=True, typ='mesh')[0]
            #getGeoShape = '%s|%s' %(meshConnected, getGeoShape)
            cmds.disconnectAttr(getGeoShape + '.worldMesh[0]', 
                                gatherInfoFromDelta + iGt)
        except:
            pass
        cmds.removeMultiInstance(gatherInfoFromDelta, b=True)
       
        # Refresh Inbetween Layout
        if deleteSlider:
            # Refresh ListInbetween
            self.listInbetween()
            
            print ('The item: %s have been removed from the corrective %s'
                   %(correctiveItem, correctiveName))
      
    def newInbetween(self, blendShapeNode=None,
                     correctiveName=None,
                     newcorrectiveItem=None,
                     mesh=None,
                     pointArray=None,
                     componentList=None,
                     arg=None):
       
        #print 'def newInbetween'
        # Creates a new ibetween with the proper data
        
        #=======================================================================
        # ADD WARNING BEFORE DUPLICATE CR WHEN THE SELECTED ONE DOES NOT HAVE ANY DELTA, 
        # OTHERWISE WILL ERROR
        #=======================================================================
        
        '''
        print '----> ',blendShapeNode
        print '----> ',correctiveName
        print '----> ',newcorrectiveItem
        print '----> ',mesh
        print '----> ',pointArray
        print '----> ',componentList
        '''
        
        correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
       
        iTg = '%s.inputTarget[0]' %blendShapeNode
        iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
        iTi = '.inputTargetItem[%s]' %newcorrectiveItem
        #iGt = '.inputGeomTarget'
        iPt = '.inputPointsTarget'
        iCt = '.inputComponentsTarget'
        
        if pointArray == None and componentList == None:
            pointArray = []
            componentList = []
        
        cmds.setAttr(iTg + iTgGr + iTi + iPt, type='pointArray', *pointArray)
        cmds.setAttr(iTg + iTgGr + iTi + iCt, type='componentList', *componentList)


            
       
    def copyDataCr(self, correctiveItem=None, arg=None):
        
        #print 'def copyDataCr'
        global crData
        #======================================================================
        # AUTO INFO FROM UI STATEMENT
        #======================================================================
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True,
                                             si=True)[0]     
        #=======================================================================
        crData = self.getCrPointData(blendShapeNode, correctiveName, correctiveItem)
        
        '''
        print '--------> ', blendShapeNode
        print '--------> ', correctiveName
        print '--------> ', correctiveItem
        print '--------> ', crData
        '''
    
    '''
    # To add this option for the next version!
    
    def pasteSelectedDataCr(self, correctiveItem=None, arg=None):
        print 'def pasteSelectedDataCr'
        global crData
        #======================================================================
        # AUTO INFO FROM UI STATEMENT
        #======================================================================
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True,
                                             si=True)[0]     
        #=======================================================================
        
        print '--------> ', blendShapeNode
        print '--------> ', correctiveName
        print '--------> ', correctiveItem
                
    '''
        
    def pasteDataCr(self, correctiveItem=None, arg=None):
        
        #print 'def pasteDataCr'
        global crData
        #======================================================================
        # AUTO INFO FROM UI STATEMENT
        #======================================================================
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True,
                                             si=True)[0]     
        #=======================================================================
        
        '''
        print '--------> ', blendShapeNode
        print '--------> ', correctiveName
        print '--------> ', correctiveItem
        '''
        
        
        if crData != None:
            pArray = crData.values()[0][0]
            cList = crData.values()[0][1]
            self.newInbetween(blendShapeNode, 
                              correctiveName, 
                              newcorrectiveItem=correctiveItem, 
                              mesh=None, 
                              pointArray=pArray, 
                              componentList=cList)
        else:
            print 'No Data To Paste'
        
        # None to crData for safe COPY/PASTE
        crData = None
    
    def resetDataCr(self, correctiveItem=None, arg=None):
        
        #print 'def resetCrData'
        #======================================================================
        # AUTO INFO FROM UI STATEMENT
        #======================================================================
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True,
                                             si=True)[0]     
        #=======================================================================        
        correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]
        
        iTg = '%s.inputTarget[0]' %blendShapeNode
        iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
        iTi = '.inputTargetItem[%s]' %correctiveItem
        iPt = '.inputPointsTarget'
        
        # Remove multiInstance to reset the shape
        cmds.removeMultiInstance(iTg + iTgGr + iTi, b=True)
        # Query to create the proper new plug with NONE inside
        cmds.getAttr(iTg + iTgGr + iTi + iPt)

    def resetSculpt(self, geo, copyMode=True):
        #print 'def resetSculpt'

        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        
        geo = self.getGeoNameFromNode(blendShapeNode)
        shapeGeo = cmds.listRelatives(geo, s=True, ni=True)[0]
        
        sculptGeo = str(geo) +  '_GeoSculpt'
        shapeSculptGeo = cmds.listRelatives(sculptGeo, s=True, ni=True)[0]
        shapeSculptGeo = '%s|%s' %(sculptGeo, shapeSculptGeo)
        
        if copyMode:
            listSculptPnts = cmds.getAttr(shapeSculptGeo + '.pnts', mi=True)
            #listPnts = cmds.getAttr(shapeGeo + '.pnts', mi=True)
            if listSculptPnts != None:
                for p in xrange(len(listSculptPnts)):
                    cmds.removeMultiInstance(shapeSculptGeo + '.pnts[%s]' %listSculptPnts[p])
            #===================================================================
            # if listPnts != None:
            #    for p in xrange(len(listPnts)):
            #        #print (shapeGeo + '.pnts[%s]' %listPnts[p])
            #        cmds.removeMultiInstance(shapeGeo + '.pnts[%s]' %listPnts[p])
            #===================================================================
            
            cmds.select(sculptGeo)
            
        else:
            print 'TWEAK NODE ---------------- OBSOLETE'
            # USE TWEAK NODE - OBSOLETE
            listDef = self.listOrderDef(geo)
            cmds.select(geo)
            shapeSculptGeo = cmds.pickWalk(d='down')
            
            if listDef != None:
                for d in listDef:
                    if cmds.objectType(d) == 'tweak':
                        tweakNode = d
                        vlistDir = tweakNode + '.vlist[0].vertex'
                        listV = cmds.getAttr(vlistDir, mi=True)
                        if listV != None:
                            for v in xrange(len(listV)):
                                #print vlistDir + '[%s]' %listV[v]
                                cmds.removeMultiInstance(vlistDir + '[%s]' %listV[v], b=True)
                            # Restore original Tweak connection
                            if cmds.isConnected(tweakNode + '.vlist[0].vertex[0]', shapeSculptGeo[0] + '.tweakLocation') != True:
                                cmds.connectAttr(tweakNode + '.vlist[0].vertex[0]', shapeSculptGeo[0] + '.tweakLocation')

        
        #print '-----> ', blendShapeNode
        #print '-----> ', geo
        #print '-----> ', sculptGeo
                
    def listOrderDef(self, geo):
        #print 'def listOrderDef'
        
        histObj = cmds.listHistory(geo, pdo=True)

        defList = []
        for h in histObj:
            current = cmds.nodeType(h, inherited=True)
            if 'geometryFilter' in current:
                defList.append(h)
        
        return defList
            
    def reorderSculptDef(self, geo, switch=False):
        #print 'def reorderSculptDef'
        
        listDef = self.listOrderDef(geo)
        #print listDef
#        for d in listDef:
#            if cmds.objectType(d) == 'tweak':
#                if 'tweakGeoSculpt' not in d:
#                    cmds.rename(d, 'tweakGeoSculpt')
        
        if cmds.objectType(listDef[0]) == 'blendShape':
            cmds.reorderDeformers(listDef[-1], listDef[0], geo)
        
        elif cmds.objectType(listDef[0]) == 'tweak':
            if switch:
                cmds.reorderDeformers(listDef[-1], listDef[0], geo)
            
    
    def createSculptGeo(self, geoName, copyMode=True, shader=False):
        #print 'def sculptGeo'
        
        #=======================================================================
        # MODE:
        # True - geo simply copy the geometry and use in/Out Mesh
        # False - copy the geometry and reorder tweak and blendShape
        #=======================================================================
        
        
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        
        geo = self.getGeoNameFromNode(blendShapeNode)
        
        
        if copyMode:
            if cmds.ls(geo + '_GeoSculpt') == []:
                sculptGeo = self.originalShape(blendShapeNode, 
                                               newName=geo + '_GeoSculpt', 
                                               offset=[0, 0, 0])
                cmds.connectAttr(geo + '.outMesh', sculptGeo + '.inMesh')
            else:
                print 'SculptGeo exists'
                sculptGeo = geo + '_GeoSculpt'
                if cmds.isConnected(geo + '.outMesh', sculptGeo + '.inMesh') != True:
                    cmds.connectAttr(geo + '.outMesh', sculptGeo + '.inMesh')
            
        
        else:
            if cmds.ls(geo + '_GeoSculpt') == []:
                sculptGeo = self.originalShape(blendShapeNode, 
                                               newName=geo + '_GeoSculpt', 
                                               offset=[0, 0, 0])
                
                cmds.blendShape(geo, 
                                sculptGeo, 
                                foc=True, 
                                w=[0, 1], 
                                n='blendShapeGeoSculpt')
    
                self.reorderSculptDef(geo=sculptGeo)
        
        cmds.setAttr('%s.visibility' %geo, 0)
        cmds.select(geo + '_GeoSculpt')
        
            
    def switchBetween(self, both=False, arg=None):
        #print 'def switchBetween'
        
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        
        geo = self.getGeoNameFromNode(blendShapeNode)
        
        sculptGeo = geo + '_GeoSculpt'       
        
        if cmds.ls(sculptGeo) != [] and cmds.ls(geo) != []:
            if both:
                cmds.setAttr(sculptGeo + '.visibility', 1)
                cmds.setAttr(geo + '.visibility', 1)
            else:
                if cmds.getAttr(sculptGeo + '.visibility') == 1:
                    cmds.setAttr(sculptGeo + '.visibility', 0)
                    cmds.setAttr(geo + '.visibility', 1)
                    cmds.select(geo)
                elif cmds.getAttr(geo + '.visibility') == 1:
                    cmds.setAttr(sculptGeo + '.visibility', 1)
                    cmds.setAttr(geo + '.visibility', 0)
                    cmds.select(sculptGeo)
        
        
    
    def deleteSculptGeo(self, geo):
        #print 'def deleteSculptGeo'
        
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        
        geo = self.getGeoNameFromNode(blendShapeNode)
        sculptGeo = geo + '_GeoSculpt'
        try:
            cmds.delete(sculptGeo)
            cmds.setAttr(geo + '.visibility', 1)
        except:
            print 'sculptGeo has been deleted by the user'
        
        
    def itemToTools(self, correctiveItem=None, arg=None):
        #print 'def itemToTools', correctiveItem
        cmds.radioButtonGrp('radioGrpItem', e=True, select=2)
        
        cmds.intField(self.itemNumber, edit=True, enable=True, value=correctiveItem)
        
        
        cmds.iconTextCheckBox('selButton', e=True, value=0)
        cmds.formLayout('formSelectionFrame', e=True, enable=True)
        cmds.formLayout('formPruneFrame', e=True, enable=True)
        self.stateSelectToolBt(False, arg)
        self.intFieldChange(arg)
        #cmds.iconTextCheckBox('selButton', e=True, label='Select', enable=True)
        #self.stateSelectToolBt( False)
        #cmds.iconTextCheckBox('selButton', e=True, label='Select')
        #print self.itemNumber()
    
    def seeDelta(self, correctiveItem=None, selectAtTheEnd=True, arg=None):
        
        #print 'def seeDelta'
        #======================================================================
        # AUTO INFO FROM UI STATEMENT
        #======================================================================
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True,
                                             si=True)[0]
        
        geoName = self.getGeoNameFromNode(blendShapeNode)
        #=======================================================================
        crData = self.getCrPointData(blendShapeNode, correctiveName, correctiveItem)
        #print '====> ', crData
        #print '====> ', crData.values()[0][0][0]
        # Delete the first item from the list that represents the
        # amount of delta values
        try:
            crData.values()[0][1].pop(0)
            #print '--------> ', blendShapeNode
            #print '--------> ', correctiveName
            #print '--------> ', geoName
            #print '--------> ', crData.values()[0][1]
            geoVtxList = []
            for vts in crData.values()[0][1]:
                if cmds.getAttr(str(geoName) + '.visibility') == 1:
                    geoVtxList.append(str(geoName) + '.' + vts)
                # If sculptGeo name exists, add to the list to be selected as well
                elif cmds.getAttr(str(geoName) + '_GeoSculpt.visibility') == 1:
                    geoVtxList.append(str(geoName) + '_GeoSculpt' + '.' + vts)
            
            #if selectAtTheEnd:
            #print geoVtxList
            cmds.select(geoVtxList)
            #return len(geoVtxList)
            return crData.values()[0][0][0]
        except:
            print 'THERE IS NO DATA AVAILABLE'
            return 0
        
    
    def zeroPts(self, correctiveItem=None, arg=None):
        
        #print 'def resetPoints'
        
        #======================================================================
        # AUTO INFO FROM UI STATEMENT
        #======================================================================
        blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                         q=True,
                                         value=True)
        correctiveName = cmds.textScrollList(self.scrollCrList,
                                             q=True,
                                             si=True)[0]
        
        #geoName = self.getGeoNameFromNode(blendShapeNode)
        #=======================================================================
        crData = self.getCrPointData(blendShapeNode, correctiveName, correctiveItem)
        # Delete the first item from the list that represents the amount of delta
        # values
        crData.values()[0][1].pop(0)
    
    def getCrPointData(self, blendShapeNode=None, correctiveName=None,
                       correctiveItem=None, geo=None, arg=None):
        
        #print 'def getCrPointData'
        # Get data from one inbetween item
        #=======================================================================
        # AUTO INFO FROM UI STATEMENT
        #=======================================================================
        if not blendShapeNode:
            blendShapeNode = cmds.optionMenu(self.optionMenuGrpBlend,
                                             q=True, value=True)
        if not correctiveName:
            correctiveName = cmds.textScrollList(self.scrollCrList,
                                                 q=True, si=True)[0]
        #=======================================================================
        # if not geo:
        #    geoName = self.getGeoNameFromNode(blendShapeNode)
        #=======================================================================
        
        #=======================================================================
        correctiveGroup = self.getCrGrpItem()[str(correctiveName)][0]  
       
        ### CHECK THIS This is not safe!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if not correctiveItem:
            correctiveItem = correctiveItem.split(str(correctiveName))[-1]
        #=======================================================================
        # BLENDSHAPE PATH
        #=======================================================================
        iTg = '%s.inputTarget[0]' %blendShapeNode
        iTgGr = '.inputTargetGroup[%s]' %correctiveGroup
        iTi = '.inputTargetItem[%s]' %correctiveItem
        iGt = '.inputGeomTarget'
        iPt = '.inputPointsTarget'
        iCt = '.inputComponentsTarget'
       
        gatherMesh = iTg + iTgGr + iTi + iGt
        gatherDataPointArray = iTg + iTgGr + iTi + iPt
        gatherDataComponentList =  iTg + iTgGr + iTi + iCt      
        '''
        print 'gatherMesh: ',gatherMesh
        print 'gatherDataPointArray: ',gatherDataPointArray
        print 'gatherDataComponentList: ',gatherDataComponentList
        '''
        
        #=======================================================================
        # DATA TYPE
        #=======================================================================
        # targetName: (delta, vtx)
        dicData = {}
        try:
            meshInfo = cmds.listConnections(gatherMesh, source=True)[0]
        except:
            meshInfo = None
        deltaInfo = cmds.getAttr(gatherDataPointArray)
        componentInfo = cmds.getAttr(gatherDataComponentList)
        dicData[meshInfo] = (deltaInfo, componentInfo)
        # When the corrective is default it does not have any data so for that
        # reason needs to try to add to do not have failure at this point!
        try:
            deltaInfo.insert(0, len(deltaInfo))
            componentInfo.insert(0, len(componentInfo))
        except:
            pass
        return dicData
    