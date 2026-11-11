"""Scene-building helpers shared by all animations."""
import colorsys
import math
from pathlib import Path

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


def emissive(name, color, strength=1.0):
    """A glowing, unlit material: stays readable whatever the lighting."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    em = nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1.0)
    em.inputs["Strength"].default_value = strength
    out = nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(em.outputs[0], out.inputs[0])
    return mat


def add_arrow(start, end, mat, radius=0.04, parent=None):
    """An arrow from `start` to `end` (coordinates are local to `parent`)."""
    start, end = Vector(start), Vector(end)
    axis = end - start
    length = axis.length
    head = min(radius * 6, length * 0.5)
    rot = axis.to_track_quat("Z", "Y").to_euler()
    unit = axis.normalized()

    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=length - head, vertices=24,
        location=start + unit * (length - head) / 2, rotation=rot)
    shaft = bpy.context.object
    bpy.ops.mesh.primitive_cone_add(
        radius1=radius * 2.6, depth=head, vertices=24,
        location=end - unit * head / 2, rotation=rot)
    tip = bpy.context.object
    for part in (shaft, tip):
        part.data.materials.append(mat)
        part.parent = parent
    return shaft, tip


def add_screen_text(scene, fmt, text, x, y, size, mat, align="CENTER"):
    """Text fixed to the screen, like a caption.

    `x`, `y` run from -1 to 1 across the frame (0, 0 is the centre) and
    `size` is the letter height as a fraction of the frame width, so the
    same layout works for every format.
    """
    cam = scene.camera
    depth = 2.0
    half_sensor = cam.data.sensor_width / 2
    if fmt.aspect >= 1:
        tan_h = half_sensor / cam.data.lens
        tan_v = tan_h / fmt.aspect
    else:
        tan_v = half_sensor / cam.data.lens
        tan_h = tan_v * fmt.aspect

    bpy.ops.object.text_add()
    obj = bpy.context.object
    obj.data.body = text
    obj.data.font = maths_font() or obj.data.font
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size * 2 * tan_h * depth
    obj.data.materials.append(mat)
    obj.parent = cam
    obj.rotation_euler = (0, 0, 0)
    obj.location = (x * tan_h * depth, y * tan_v * depth, -depth)
    return obj


def pop_in(obj, frame, fps, duration=0.4):
    """Hide `obj` until `frame`, then scale it up with a small bounce."""
    key(obj, 1, scale=(0, 0, 0))
    steps = max(round(duration * fps), 1)
    for f in range(steps + 1):
        s = ease_out_back(f / steps)
        key(obj, frame + f, scale=(s, s, s))


# Fonts that include Greek letters and maths symbols (the font built into
# Blender does not). The first one found is used.
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "C:/Windows/Fonts/seguisym.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def maths_font():
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return bpy.data.fonts.load(path, check_existing=True)
    return None


def add_world_text(text, location, size, mat, parent=None, align="CENTER"):
    """Text standing in the XZ plane, readable from a camera on the -Y side."""
    bpy.ops.object.text_add()
    obj = bpy.context.object
    obj.data.body = text
    obj.data.font = maths_font() or obj.data.font
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.materials.append(mat)
    obj.parent = parent
    obj.rotation_euler = (math.pi / 2, 0, 0)
    obj.location = location
    return obj


def pop_out(obj, frame, fps, duration=0.25):
    """Shrink `obj` away, finishing at `frame`."""
    steps = max(round(duration * fps), 1)
    for f in range(steps + 1):
        s = 1.0 - smoothstep(f / steps)
        key(obj, frame - steps + f, scale=(s, s, s))


def show(obj, start, end, fps):
    """Make `obj` visible only between `start` and `end` (in seconds).
    `end=None` keeps it until the video finishes."""
    pop_in(obj, 1 + round(start * fps), fps)
    if end is not None:
        pop_out(obj, 1 + round(end * fps), fps)


def flat_style(scene):
    """Fast render settings for scenes made only of emissive materials:
    no light bounces to trace, so a few samples give a clean image."""
    scene.cycles.samples = min(scene.cycles.samples, 12)
    scene.cycles.use_denoising = False
    scene.cycles.max_bounces = 0
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"


def add_box(width, height, location, mat, depth=0.1, parent=None):
    """A flat bar or block in the XZ plane, `width` across and `height` tall."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.scale = (width, depth, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    obj.parent = parent
    return obj


def move(obj, start, end, to, fps):
    """Glide `obj` from where it is to `to` between two times (seconds)."""
    origin = Vector(obj.location)
    first, last = 1 + round(start * fps), 1 + round(end * fps)
    for frame in range(first, last + 1):
        t = smoothstep((frame - first) / max(last - first, 1))
        key(obj, frame, location=origin.lerp(Vector(to), t))
