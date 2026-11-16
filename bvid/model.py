"""Modelling helpers: real-size meshes (no object scale), parented in place."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector


def mesh_object(name, bm, mat, parent=None, location=(0, 0, 0), rotation=None,
            smooth_shading=False):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    if smooth_shading:
        for poly in mesh.polygons:
            poly.use_smooth = True
    if mat is not None:
        mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = parent
    obj.location = location
    if rotation is not None:
        obj.rotation_euler = rotation
    return obj


def box(name, size, location, mat, parent=None, rotation=None, taper=1.0):
    """A box `size` = (x, y, z); `taper` narrows the top face."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        k = taper if v.co.z > 0 else 1.0
        v.co = Vector((v.co.x * size[0] * k, v.co.y * size[1] * k,
                       v.co.z * size[2]))
    return mesh_object(name, bm, mat, parent, location, rotation)


def ball(name, radii, location, mat, parent=None, rotation=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2]))
    return mesh_object(name, bm, mat, parent, location, rotation, True)


def rod(name, start, end, radius, mat, parent=None, flatten=(1.0, 1.0),
        segments=16):
    """A cylinder from `start` to `end`."""
    start, end = Vector(start), Vector(end)
    axis = end - start
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius,
                          radius2=radius, depth=axis.length)
    for v in bm.verts:
        v.co.x *= flatten[0]
        v.co.y *= flatten[1]
    return mesh_object(name, bm, mat, parent, (start + end) / 2,
                   axis.to_track_quat("Z", "Y").to_euler(), True)


def empty(name, parent=None, location=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(obj)
    obj.empty_display_size = 0.3
    obj.parent = parent
    obj.location = location
    return obj


def slabs(name, boxes, mat):
    """Many boxes ((centre), (size)) merged into one object."""
    bm = bmesh.new()
    for centre, size in boxes:
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=Matrix.LocRotScale(Vector(centre), None, Vector(size)))
    return mesh_object(name, bm, mat)


def tube(name, r_in, r_out, height, location, mat, parent=None, gap=0.0,
         segments=64):
    """A flat-sided ring standing on `location`; `gap` (radians) cuts a slot
    through it."""
    bm = bmesh.new()
    closed = gap <= 0
    steps = segments if closed else segments + 1
    sections = []
    for i in range(steps):
        a = gap / 2 + (math.tau - gap) * i / segments
        c, s = math.cos(a), math.sin(a)
        sections.append([bm.verts.new((r * c, r * s, z)) for r, z in
                         ((r_in, 0), (r_out, 0), (r_out, height), (r_in, height))])
    for i in range(segments):
        a, b = sections[i], sections[(i + 1) % steps]
        for k in range(4):
            bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
    if not closed:
        bm.faces.new(sections[0])
        bm.faces.new(sections[-1][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_object(name, bm, mat, parent, location)


def cable(name, points, radius, mat):
    """A smooth round cable through `points`."""
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 3
    spline = curve.splines.new("NURBS")
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        point.co = (*co, 1.0)
    spline.use_endpoint_u = True
    spline.order_u = 3
    spline.resolution_u = 12
    curve.materials.append(mat)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    return obj
