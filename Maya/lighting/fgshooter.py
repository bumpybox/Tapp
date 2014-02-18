# written by Brenton Rayner at The Mill (www.themill.com)
# fgshooter.py
# version 1.0.1
# released 1/7/12

import pymel.core as pm
import logging

log = logging.getLogger("fgshooter")


def currentCamera(render_cam):
    '''
    Create an fgshooter camera at same location as the render camera.
    '''
    # Duplicate the render camera and make sure the duplicate is not renderable.
    fg_cam = pm.duplicate(render_cam, rr=True, name="fgshooterCamera")[0]
    fg_cam_shape = fg_cam.getShape()
    fg_cam_shape.renderable.set(False)
    # Change the fgshooter camera's wireframe color.
    pm.color(fg_cam, ud=2)

    # Find the render camera's transfrom and parent the fgshooter to it.
    render_cam_transform = render_cam.listRelatives(p=True, type="transform")[0]
    pm.parent(fg_cam, render_cam_transform)

    # Pass aperture and aspect information with the fgshooter camera's scale.
    aperture = render_cam.horizontalFilmAperture.get()
    aspect = aperture / pm.Attribute("defaultResolution.deviceAspectRatio").get()
    fg_cam.scaleX.set(aperture)
    fg_cam.scaleY.set(aspect)

    # Connect the render camera's focal length to the fgshooter since it could be animated.
    multiply_divide = pm.createNode("multiplyDivide")
    multiply_divide.input2X.set(0.03937)
    render_cam.focalLength >> multiply_divide.input1X
    multiply_divide.outputX >> fg_cam.scaleZ

    return fg_cam_shape

def fixedCamera(render_cam, frame):
    '''
    Create an fgshooter camera fixed at the render camera's position for a spcified frame.
    '''
    # Not the best way to get the world position and rotation values out of the render_camera... but it works.
    # Pymel's matrix.rotate and matrix.getRotation() seem to be broken.
    tmp_node = pm.createNode("decomposeMatrix")
    render_cam.worldMatrix >> tmp_node.inputMatrix
    frame_position = [tmp_node.outputTranslateX.get(time = frame),
                      tmp_node.outputTranslateY.get(time = frame),
                      tmp_node.outputTranslateZ.get(time = frame)]
    frame_rotation = [tmp_node.outputRotateX.get(time = frame),
                      tmp_node.outputRotateY.get(time = frame),
                      tmp_node.outputRotateZ.get(time = frame)]
    pm.delete(tmp_node)

    # Create the fixed camera. Change it's wireframe color.
    fg_cam, fg_cam_shape = pm.camera(name="fgshooterCamera", position=frame_position, rotation=frame_rotation)
    pm.color(fg_cam, ud=2)

    # Adjust the fgshooter camera's scale to pass aperture, aspect, and focal length information.
    aperture = render_cam.horizontalFilmAperture.get(time = frame)
    aspect = aperture / pm.Attribute("defaultResolution.deviceAspectRatio").get(time = frame)
    focal = 0.03937 * render_cam.focalLength.get(time = frame)

    fg_cam.scaleX.set(aperture)
    fg_cam.scaleY.set(aspect)
    fg_cam.scaleZ.set(focal)

    return fg_cam_shape

def offsetCamera(render_cam, offset):
    '''
    Create an fgshooter camera offset from the render camera by a few frames.
    '''
    # Create camera and change wireframe color.
    fg_cam, fg_cam_shape = pm.camera(name = "fgshooterCamera")
    pm.color(fg_cam, ud=2)

    # Create all the connection nodes we are going to need.
    decompose_matrix = pm.createNode("decomposeMatrix")
    multiply_divide = pm.createNode("multiplyDivide")
    frame_cache_tx = pm.createNode("frameCache")
    frame_cache_ty = pm.createNode("frameCache")
    frame_cache_tz = pm.createNode("frameCache")
    frame_cache_rx = pm.createNode("frameCache")
    frame_cache_ry = pm.createNode("frameCache")
    frame_cache_rz = pm.createNode("frameCache")
    frame_cache_fl = pm.createNode("frameCache")

    # Connect all of those nodes to the render camera.
    render_cam.worldMatrix >> decompose_matrix.inputMatrix
    decompose_matrix.outputTranslateX >> frame_cache_tx.stream
    decompose_matrix.outputTranslateY >> frame_cache_ty.stream
    decompose_matrix.outputTranslateZ >> frame_cache_tz.stream
    decompose_matrix.outputRotateX >> frame_cache_rx.stream
    decompose_matrix.outputRotateY >> frame_cache_ry.stream
    decompose_matrix.outputRotateZ >> frame_cache_rz.stream
    render_cam.focalLength >> frame_cache_fl.stream

    # If the offset is positive, use the future attribute.
    if offset > 0:
        # Workaround for a pymel bug
        offset = ".future[" + str(offset) +"]"
        pm.Attribute(frame_cache_tx + offset) >> fg_cam.translateX
        pm.Attribute(frame_cache_ty + offset) >> fg_cam.translateY
        pm.Attribute(frame_cache_tz + offset) >> fg_cam.translateZ
        pm.Attribute(frame_cache_rx + offset) >> fg_cam.rotateX
        pm.Attribute(frame_cache_ry + offset) >> fg_cam.rotateY
        pm.Attribute(frame_cache_rz + offset) >> fg_cam.rotateZ
        pm.Attribute(frame_cache_fl + offset) >> multiply_divide.input1X

    # If the offset is negative, use the past attribute.
    else:
        offset = -offset
        frame_cache_tx.past[offset] >> fg_cam.translateX
        frame_cache_ty.past[offset] >> fg_cam.translateY
        frame_cache_tz.past[offset] >> fg_cam.translateZ
        frame_cache_rx.past[offset] >> fg_cam.rotateX
        frame_cache_ry.past[offset] >> fg_cam.rotateY
        frame_cache_rz.past[offset] >> fg_cam.rotateZ
        frame_cache_fl.past[offset] >> multiply_divide.input1X

    # Pass aperture, aspect, and focal length infromation with the fgshooter camera's scale.
    # Focal length is connected because it could be animated.
    aperture = render_cam.horizontalFilmAperture.get()
    aspect = aperture / pm.Attribute("defaultResolution.deviceAspectRatio").get()
    multiply_divide.input2X.set(0.03937)

    fg_cam.scaleX.set(aperture)
    fg_cam.scaleY.set(aspect)
    multiply_divide.outputX >> fg_cam.scaleZ

    return fg_cam_shape

def resetFgShooter(fg_shooter):
    '''
    Deletes the fgshooter cameras and node trees connected to the mip_fgshooter shader.
    '''
    # The hip bone is connected to the thigh bone...
    nodes = set()
    for cam in fg_shooter.listConnections(type="camera"):
        for md in cam.listConnections(type="multiplyDivide"):
            for fc in md.listConnections(type="frameCache"):
                nodes.add(fc)
            nodes.add(md)
        for fc in cam.listConnections(type="frameCache"):
            for dm in fc.listConnections(type="decomposeMatrix"):
                nodes.add(dm)
            nodes.add(fc)
        for uc in cam.listConnections(type="unitConversion"):
            for fc in uc.listConnections(type="frameCache"):
                for dm in fc.listConnections(type="decomposeMatrix"):
                    nodes.add(dm)
                nodes.add(fc)
            nodes.add(uc)
        nodes.add(cam)
    pm.delete(nodes)

def getFgShooter(render_cam):
    '''
    Finds or creates a mip_fgshooter shader on the render camera.
    '''
    removeFgShooters()

    # We have not found a mip_fgshooter. Create one and connect it to the utilities.
    mip_fgshooter = pm.createNode("mip_fgshooter")
    mip_fgshooter.message.connect("defaultRenderUtilityList1.utilities", na=True)

    # We also need to connect the mip_fgshooter to our camera.
    if render_cam.miLensShader.isConnected() or render_cam.miLensShaderList.listConnections():
        if render_cam.miLensShaderList.get(mi=True) is not None:
            for index in render_cam.miLensShaderList.get(mi=True):
                if not render_cam.miLensShaderList[index].listConnections():
                    pm.mel.removeMultiInstance(render_cam.miLensShaderList[index])
        new_index = 0
        if render_cam.miLensShaderList.get(mi=True):
            new_index = render_cam.miLensShaderList.get(mi=True)[-1] + 1
        mip_fgshooter.message >> render_cam.miLensShaderList[new_index]
    else:
        mip_fgshooter.message >> render_cam.miLensShader
    return mip_fgshooter

def getRenderCamera():
    '''
    Find the render camera. If the render camera is a default camera, return None.
    '''
    render_cam = None

    # Do not include the default cameras.
    default_cameras = ["frontShape", "perspShape", "sideShape", "topShape"]
    cameras = pm.ls(cameras=True)
    for cam in cameras:
        if cam.renderable.get() and cam.name() not in default_cameras:
            render_cam = cam
            break

    return render_cam

def removeFgShooters():
    '''
    Remove all of the mip_fgshooter shaders as well as the fgshooter cameras and node trees.
    '''
    fg_shooters = pm.ls(type = "mip_fgshooter")
    for fg_shooter in fg_shooters:
        transform = fg_shooter.trans

        # Remove all the fgshooter cameras and node trees!
        resetFgShooter(transform)

        # Delete the mip_fgshooter shader!
        pm.delete(fg_shooter)

def createFgShooters(frames=[], offsets=[], current_camera=True):
    '''
    Create fgshooter cameras for the render camera. Cameras can be fixed, current, or offset.
    '''
    # Ensure that decomposeMatrix is loaded.
    if not pm.pluginInfo("decomposeMatrix", q=True, loaded=True):
        log.info("Loading \"decomposeMatrix\" plugin.")
        pm.loadPlugin("decomposeMatrix")

    # Make sure there are no duplicate frames or offsets.
    frames = set(frames)
    offsets = set(offsets)
    
    # Get the render Camera.
    render_cam = getRenderCamera()
    if render_cam is None:
        log.warning("Could not find non-default render camera.")
        return None
    
    # Get the mip_fgshooter shader connected to the render camera.
    fg_shooter = getFgShooter(render_cam)
    transform = fg_shooter.trans
    
    index = 0

    # Create current fgshooter camera.
    if current_camera:
        fg_cam = currentCamera(render_cam)
        fg_cam.worldMatrix >> transform[index]
        index += 1

    # Create fixed fgshooter cameras.
    for frame in frames:
        fg_cam = fixedCamera(render_cam, frame)
        fg_cam.worldMatrix >> transform[index]
        index += 1

    # Create offset fgshooter cameras.
    for offset in offsets:
        if not isinstance(offset, int):
            log.warning("Offsets must be intergers. Skipping: %s", offset)
            continue
        if offset:
            fg_cam = offsetCamera(render_cam, offset)
            fg_cam.worldMatrix >> transform[index]
            index += 1

def getMultiAttr(attribute):
    '''
    Returns the multi attribtues for a multi attribute.
    '''
    multi = []
    count = attribute.evaluateNumElements()
    for i in range(count):
        multi.append(attribute.elementByPhysicalIndex(i))
    return multi


class ui():
    def __init__(self):
        self.window_title = "fgshooter window"
        self.window_name = "fgshooter_window"
        
        # Default fgshooter values.
        self.render_camera = True
        self.stationary_frames = [0.0, 12.0, 24.0]
        self.offset_frames = []
        self.create(3, 0)
    
    def create(self, stationary_count, offset_count):
        '''
        Create the fgshooter window.
        '''
        if pm.window(self.window_name, exists=True):
            pm.deleteUI(self.window_name)
        pm.window(self.window_name, title=self.window_title)
        
        main_form = pm.formLayout(numberOfDivisions=2)
        self.column = pm.columnLayout(adjustableColumn=True)
        
        # Render Camera
        self.render_camera_field = pm.checkBoxGrp(label="Include Render Camera", value1=self.render_camera, changeCommand=self.updateRenderCamera)
        
        # Stationary Cameras
        pm.separator(height=20, style="in")
        
        pm.rowLayout(numberOfColumns=3, columnWidth3=(140, 80, 80), columnAlign=(1, 'right'), columnAttach3=("right", "both", "both"))
        pm.text("Stationary Cameras")
        self.stationary_field = pm.intField(value=stationary_count)
        pm.button(label="Update", height=22, command=self.update)
        pm.setParent('..')
        
        self.stationary = []
        i = 0
        while i < stationary_count:
            self.stationary.append(pm.floatFieldGrp(value1=self.stationary_frames[i], label="frame"))
            i += 1
        
        # Offset Cameras
        pm.separator(height=20, style="in")
        
        pm.rowLayout(numberOfColumns=3, columnWidth3=(140, 80, 80), columnAlign=(1, 'right'), columnAttach3=("right", "both", "both"))
        pm.text("Offset Cameras")
        self.offset_field = pm.intField(value=offset_count)
        pm.button(label="Update", height=22, command=self.update)
        pm.setParent('..')
        
        self.offset = []
        i = 0
        while i < offset_count:
            self.offset.append(pm.intFieldGrp(value1=self.offset_frames[i], label="frame offset"))
            i += 1
        
        pm.setParent('..')
        
        # remove/apply buttons        
        self.remove_button = pm.button(label="Remove All", height=30, command=self.remove)
        self.apply_button = pm.button(label="Apply / Refresh", height=30, command=self.apply)
        
        pm.formLayout(main_form, edit=True, attachForm=[(self.column, "top", 2),(self.column, "left", 2),(self.column, "right", 2), (self.remove_button, "bottom", 2), (self.remove_button, "left", 2), (self.apply_button, "bottom", 2), (self.apply_button, "right", 2)], attachControl=(self.remove_button, "right", 1, self.apply_button), attachPosition=[ (self.remove_button, "right", 0, 1), (self.apply_button, "left", 1, 1)] )
        
        pm.setParent('..')
        pm.showWindow()
    
    def updateRenderCamera(self, ignore):
        self.render_camera = bool(self.render_camera_field.getValue1())
    
    def update(self, ignore):
        # Update stationary.
        self.find_stationary()
        stationary_count = self.stationary_field.getValue()
        
        stationary_length = len(self.stationary_frames)
        while stationary_length < stationary_count:
            default_stationary = 0.0 + stationary_length * 12.0
            self.stationary_frames.append(default_stationary)
            stationary_length = len(self.stationary_frames)
        self.stationary_frames = self.stationary_frames[:stationary_count]

        # Update offset
        self.find_offset()
        offset_count = self.offset_field.getValue()
        
        offset_length = len(self.offset_frames)
        while offset_length < offset_count:
            default_offset = offset_length / 2 + 1
            if offset_length % 2:
                default_offset *= -1
            self.offset_frames.append(default_offset)
            offset_length = len(self.offset_frames)
        self.offset_frames = self.offset_frames[:offset_count]
        
        # Refresh the UI
        self.create(stationary_count, offset_count)
    
    def find_stationary(self):
        self.stationary_frames = []
        for stationary_camera in self.stationary:
            self.stationary_frames.append(stationary_camera.getValue1())
    
    def find_offset(self):
        self.offset_frames = []
        for offset_camera in self.offset:
            self.offset_frames.append(offset_camera.getValue1())
    
    def remove(self, ignore):
        '''
        Delete fgshooter cameras and all associated nodes.
        '''
        removeFgShooters()
    
    def apply(self, ignore):
        '''
        Create/refresh the fgshooter cameras and connectons.
        '''
        self.find_stationary()
        self.find_offset()
        createFgShooters(frames=self.stationary_frames, offsets=self.offset_frames, current_camera=self.render_camera)