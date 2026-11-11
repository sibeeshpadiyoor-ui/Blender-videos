"""Scene-building helpers shared by all animations."""
import colorsys
import math

import bpy
from mathutils import Vector


def reset_scene(fmt, quality, seconds):
    """Start from an empty file and configure the render for `fmt`."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = quality.samples
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True

    scene.render.resolution_x = fmt.width
    scene.render.resolution_y = fmt.height
    scene.render.resolution_percentage = quality.resolution_percent
    scene.render.fps = fmt.fps
    scene.frame_start = 1
    scene.frame_end = round(seconds * fmt.fps)
    scene.render.image_settings.file_format = "PNG"

    # AgX keeps bright lights from clipping; the punchy look restores the
    # contrast and saturation that reads well on a phone screen.
    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Punchy"
    except TypeError:
        pass

    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    return scene


def set_background(scene, color, strength=1.0):
    world = scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg is None:
        world.node_tree.nodes.clear()
        bg = world.node_tree.nodes.new("ShaderNodeBackground")
        out = world.node_tree.nodes.new("ShaderNodeOutputWorld")
        world.node_tree.links.new(bg.outputs[0], out.inputs[0])
    bg.inputs["Color"].default_value = (*color, 1.0)
    bg.inputs["Strength"].default_value = strength


def material(name, color, roughness=0.35, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def hsv(h, s=0.75, v=1.0):
    return colorsys.hsv_to_rgb(h % 1.0, s, v)


def add_floor(color, size=200.0):
    bpy.ops.mesh.primitive_plane_add(size=size)
    floor = bpy.context.object
    floor.name = "Floor"
    floor.data.materials.append(material("Floor", color, roughness=0.6))
    return floor


def add_wall(color, y=0.0, size=200.0):
    """A vertical backdrop facing the -Y direction."""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, y, 0),
                                     rotation=(math.pi / 2, 0, 0))
    wall = bpy.context.object
    wall.name = "Wall"
    wall.data.materials.append(material("Wall", color, roughness=0.7))
    return wall


def add_area_light(location, energy, size=5.0, color=(1, 1, 1), target=(0, 0, 0)):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.data.energy = energy
    light.data.size = size
    light.data.color = color
    look_at(light, target)
    return light


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_camera(scene, fmt, target, direction, half_width, half_height,
               lens=50.0, margin=1.15):
    """Add a camera that keeps a `half_width` x `half_height` area around
    `target` in view for any aspect ratio (so one animation works for
    both vertical Reels and horizontal YouTube).

    `direction` points from the target towards the camera.
    """
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Camera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    # With sensor_fit AUTO the 36mm sensor spans the longer image side.
    half_sensor = cam_data.sensor_width / 2
    if fmt.aspect >= 1:
        tan_h = half_sensor / lens
        tan_v = tan_h / fmt.aspect
    else:
        tan_v = half_sensor / lens
        tan_h = tan_v * fmt.aspect
    distance = max(half_width / tan_h, half_height / tan_v) * margin

    cam.location = Vector(target) + Vector(direction).normalized() * distance
    look_at(cam, target)
    return cam


def key(obj, frame, **props):
    """Set properties and keyframe them: key(obj, 10, location=(0, 0, 1))."""
    for name, value in props.items():
        setattr(obj, name, value)
        obj.keyframe_insert(data_path=name, frame=frame)


def ease_out_back(t, overshoot=1.70158):
    """0 -> 1 with a small bounce past 1; good for 'pop in' motion."""
    t = min(max(t, 0.0), 1.0) - 1.0
    return t * t * ((overshoot + 1) * t + overshoot) + 1.0


def smoothstep(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


TAU = math.tau
