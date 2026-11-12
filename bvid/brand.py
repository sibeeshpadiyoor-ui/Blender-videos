"""The "Beyond the Obvious Physics" channel look, for Blender.

Mirrors the style of the Modern_Physics_Animation series: near-black
starfield with a soft blue glow, off-white text, a fixed accent palette,
bold white headlines with one word in gold italic serif, the gold "?" ring
in the corner and the spaced gold channel name as a footer.
"""
import random
import textwrap
from pathlib import Path

import bpy

from . import scene as S

NAME = "BEYOND THE OBVIOUS PHYSICS"
SERIES = "Fundamentals of Physics"     # the Halliday & Resnick series
WATERMARK = Path(__file__).resolve().parent.parent / "assets/brand/watermark.png"

HEX = dict(
    bg="#02030A", glow="#1A2658", panel="#0B1430",
    fg="#EAF0FF", muted="#8892B0", soft="#B7C0E4",
    gold="#D9B26A", cyan="#4CC9F0", amber="#FFB703", yellow="#FFD866",
    pink="#FF6B9D", green="#5EE6A8", red="#FF5D5D", purple="#B388FF",
    blue="#4A5BA8", skin="#F2C79B",
)


def rgb(hex_color):
    """'#RRGGBB' (as seen on screen) -> linear RGB for Blender."""
    def channel(i):
        c = int(hex_color[i:i + 2], 16) / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (channel(1), channel(3), channel(5))


class Stage:
    """A vertical-first stage in the channel style, with text helpers.

    World objects live in the XZ plane (x across, z up), about 5 units wide.
    Screen positions run from -1 to 1 in x and y; sizes are fractions of the
    frame width of a 9:16 column, so layouts also fit wider formats.
    """

    def __init__(self, scene, fmt):
        self.scene, self.fmt, self.fps = scene, fmt, fmt.fps
        self._mats = {}
        self.column = min(1.0, (9 / 16) / fmt.aspect)
        S.flat_style(scene)
        S.set_background(scene, rgb(HEX["bg"]))
        self.cam = S.add_camera(scene, fmt, target=(0, 0, 0),
                                direction=(0, -1, 0), half_width=2.4,
                                half_height=2.4 * 16 / 9, margin=1.1)
        self._backdrop()
        self._watermark()
        footer = self.text(NAME, -0.945, 0.024, "gold", font="body")
        footer.data.space_character = 1.5

    # ----- materials ---------------------------------------------------
    def mat(self, color, strength=1.0):
        key = (color, strength)
        if key not in self._mats:
            value = rgb(HEX.get(color, color))
            self._mats[key] = S.emissive(f"{color}_{strength}", value, strength)
        return self._mats[key]

    # ----- background --------------------------------------------------
    def _screen_plane(self, x, y, width, height, depth, mat):
        """A rectangle fixed to the screen; sizes are fractions of the frame."""
        tan_h, tan_v = S.view_tangents(self.cam, self.fmt)
        bpy.ops.mesh.primitive_plane_add(size=1)
        plane = bpy.context.object
        plane.parent = self.cam
        plane.location = (x * tan_h * depth, y * tan_v * depth, -depth)
        plane.scale = (width * 2 * tan_h * depth, height * 2 * tan_v * depth, 1)
        plane.data.materials.append(mat)
        return plane

    def _backdrop(self):
        # Soft blue glow fading into the near-black background.
        glow = bpy.data.materials.new("Glow")
        glow.use_nodes = True
        nodes, links = glow.node_tree.nodes, glow.node_tree.links
        nodes.clear()
        coords = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (2.4, 2.4, 2.4)
        gradient = nodes.new("ShaderNodeTexGradient")
        gradient.gradient_type = "SPHERICAL"
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "EASE"
        ramp.color_ramp.elements[0].color = (*rgb(HEX["bg"]), 1)
        ramp.color_ramp.elements[1].color = (*rgb(HEX["glow"]), 1)
        emission = nodes.new("ShaderNodeEmission")
        output = nodes.new("ShaderNodeOutputMaterial")
        links.new(coords.outputs["Object"], mapping.inputs["Vector"])
        links.new(mapping.outputs["Vector"], gradient.inputs["Vector"])
        links.new(gradient.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], emission.inputs["Color"])
        links.new(emission.outputs[0], output.inputs[0])
        self._screen_plane(0, 0.05, 1.0, 1.0, 60.0, glow)

        # Stars: three brightness classes, each one mesh of tiny octagons.
        tan_h, tan_v = S.view_tangents(self.cam, self.fmt)
        depth = 59.0
        half_w, half_h = tan_h * depth, tan_v * depth
        rng = random.Random(3)
        unit = min(half_w, half_h) * 2
        for strength, count in ((0.9, 40), (0.55, 80), (0.3, 110)):
            verts, faces = [], []
            for _ in range(count):
                cx, cy = rng.uniform(-half_w, half_w), rng.uniform(-half_h, half_h)
                r = unit * rng.choice([0.0012, 0.0017, 0.0024, 0.0032])
                base = len(verts)
                for k in range(8):
                    a = S.TAU * k / 8
                    verts.append((cx + r * S.math.cos(a), cy + r * S.math.sin(a), 0))
                faces.append(tuple(range(base, base + 8)))
            mesh = bpy.data.meshes.new("Stars")
            mesh.from_pydata(verts, [], faces)
            stars = bpy.data.objects.new("Stars", mesh)
            self.scene.collection.objects.link(stars)
            stars.parent = self.cam
            stars.location = (0, 0, -depth)
            mesh.materials.append(self.mat("fg", strength))

    def _watermark(self):
        if not WATERMARK.exists():
            return
        mat = bpy.data.materials.new("Watermark")
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        nodes.clear()
        image = nodes.new("ShaderNodeTexImage")
        image.image = bpy.data.images.load(str(WATERMARK), check_existing=True)
        emission = nodes.new("ShaderNodeEmission")
        clear = nodes.new("ShaderNodeBsdfTransparent")
        mix = nodes.new("ShaderNodeMixShader")
        output = nodes.new("ShaderNodeOutputMaterial")
        links.new(image.outputs["Color"], emission.inputs["Color"])
        links.new(image.outputs["Alpha"], mix.inputs["Fac"])
        links.new(clear.outputs[0], mix.inputs[1])
        links.new(emission.outputs[0], mix.inputs[2])
        links.new(mix.outputs[0], output.inputs[0])
        size = 0.13 * self.column
        self._screen_plane(0.80, 0.905, size, size * self.fmt.aspect, 2.0, mat)

    # ----- timing ------------------------------------------------------
    def show(self, obj, start, end=None, duration=0.4):
        S.show(obj, start, end, self.fps, duration)
        return obj

    # ----- text --------------------------------------------------------
    def text(self, text, y, size, color="fg", start=None, end=None,
             font="bold", align="CENTER", x=0.0):
        """Text fixed to the screen, centered unless `x` is given."""
        obj = S.add_screen_text(self.scene, self.fmt, text, x * self.column, y,
                                size * self.column, self.mat(color), align,
                                font)
        if start is not None:
            self.show(obj, start, end)
        return obj

    def label(self, text, x, z, size, color="fg", start=None, end=None,
              font="bold", align="CENTER", front=0.0):
        """Text placed in the scene, next to the objects. Use `front` to
        bring text in front of a box it is written on."""
        obj = S.add_world_text(text, (x, -front, z), size, self.mat(color),
                               font=font, align=align)
        if start is not None:
            self.show(obj, start, end)
        return obj

    def box(self, width, height, x, z, color, start=None, end=None):
        obj = S.add_box(width, height, (x, 0, z), self.mat(color))
        if start is not None:
            self.show(obj, start, end)
        return obj

    def headline(self, white, gold, tag=None):
        """Bold white line(s) with one gold italic serif line under them."""
        y = 0.80
        for line in white:
            self.text(line.upper(), y, 0.095, "fg", 0.1)
            y -= 0.075
        self.text(gold, y - 0.01, 0.125, "gold", 0.4, font="serif")
        if tag:
            tag_obj = self.text(tag.upper(), 0.905, 0.024, "muted", 0.1,
                                font="body", align="LEFT", x=-0.88)
            tag_obj.data.space_character = 1.3

    def subtitles(self, timeline, width=34):
        """The spoken sentence at the bottom of the screen, on a dark box."""
        tan_h, tan_v = S.view_tangents(self.cam, self.fmt)
        for i, sentence in enumerate(timeline.sentences):
            lines = textwrap.wrap(sentence, width)
            start = timeline.start(i) - 0.05
            end = timeline.end(i) + 0.3
            if i + 1 < len(timeline.sentences):
                end = min(end, timeline.start(i + 1) - 0.1)
            obj = self.text("\n".join(lines), -0.78, 0.042, "fg",
                            font="body")
            obj.data.space_line = 1.15
            bpy.context.view_layer.update()      # measure before animating
            frame_w, frame_h = 2 * tan_h * 2.0, 2 * tan_v * 2.0
            w = obj.dimensions.x / frame_w + 0.07 * self.column
            h = obj.dimensions.y / frame_h + 0.03
            self.show(obj, start, end, duration=0.15)
            panel = self._screen_plane(0, -0.78, w, h, 2.02, self.mat("panel"))
            panel_scale = tuple(panel.scale)
            holder = bpy.data.objects.new("SubtitleBox", None)
            self.scene.collection.objects.link(holder)
            holder.parent = self.cam
            holder.location = panel.location
            panel.parent = holder
            panel.location = (0, 0, 0)
            panel.scale = panel_scale
            self.show(holder, start, end, duration=0.15)
