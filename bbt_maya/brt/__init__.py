'''
Bumpybox Rigging Tools
NOTES

proxy parent needs scale constraint as well
restructure bra similar to bat and rename to brt (Bumpybox Rigging Tools)
hierarchy files into create character function
better code structure > no copied functions
need character name on root > dropdown menu to choose specific character to work on or selected character
rewrite templates to python
generalize ik/fk setups to use one template > specify limb with dropdown, seperate bend limb from ik/fk, polevector pointer
                                                (line from knee/elbow to controller), templates are assets
simplify spine to be able to have single gut joint, new template system, hip optional
seperate foot rig
connectplugs need more fail safes: if metaParent is already connected



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