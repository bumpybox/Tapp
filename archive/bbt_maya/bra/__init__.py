'''
Bumpybox Rigging Tools
NOTES

restructure bra similar to bat and rename to brt (Bumpybox Rigging Tools)
hierarchy files into create character function
better code structure > no copied functions
improve on connecting the plugs and socket > doesnt take into account if a socket is nearest and already parented
visualize direction of elbow/knee
use cgmonks draw for placement of points
templates that scale with viewport > with indicators
threshold for left/right/center
scale matching on snappings
template nodes are easily breakable > make it into an asset? have common parameters on the asset node
clean up > not using scriptnodes anymore,
get a more unified finger setup
deleteRig > deletion of selected limb rig
mirror control shapes
templates for module hierachy
wrist orientation is off to the twist joints
finger > need single root control (curl control is separate at end of finger), need palm joint

create tab:
    path > have it not sesarch any subfolders
    deleteTemplate > need a failsafe for selecting multiple control from the same template module
    mirrorTemplate > account for multiple selected templates of same kind
    
setup tab:
    skinning joints > select > select mesh and skin?
    tool to manage sockets and plugs > possibly treeview for overview of how modules are connected > drag'n'drop feature?
    tagging tool
    tool for finding similarly tagged objects
    
templates builds:
    single joints/control
    blend chain 3 joints
    blend chain 3+ joints
    toe
    tail
    wing
    hind leg
    rebuild templates with skinning data included > use spheres and annotations?
    
utilies:
    spherePreview: use a nurbsSphere, place locator when single object selected
    js_cutPlane
    parent to nearest joint (proxy parent)

Changelog:
    
    BRA
    1.0.1
    - added proxy parent
    - change knee control to cube
    - knee control is now a child of ik foot control
    - added import/export hierarchy feature
    - added create character feature
    
    1.0.0
    - added ik neck control
    - added root control for legs
    - reorganized scripts
    - added version number on roots
    - changed orientation on torso control (affects animation)
    - changed orientation of fine tune controls (affects animation)
    - changed orientation of foot controls (affects animation)
    - changed orientation of finger controls (affects animation)
    - changed indexing of limbs (affects naming and animation)
    - added sphere preview
    - added weight map import
    - added weight map export

'''

import maya.cmds as cmds
import maya.mel as mel
import os
from shutil import move
import sys

from create import *
from setup import *
from utils import *

braDir=os.path.dirname(__file__)

def GUI():
    #delete previous window and initialize window
    if (cmds.window('raWindow', exists=True)):
        cmds.deleteUI('raWindow')
    dialog1 = cmds.loadUI(f=braDir+'/bra.ui')
    cmds.showWindow(dialog1)
    
    #setting initial path to templates
    cmds.textField('raPathLineEdit',edit=True,text=(braDir+'/templates'))
    refreshList()