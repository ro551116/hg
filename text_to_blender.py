# Simple text-driven Blender script
# This script reads instructions from a text file and generates 3D objects in Blender

import bpy
import sys


def parse_line(line):
    """Parse a single instruction line.

    Supported formats:
      cube size=<float> location=x,y,z color=r,g,b
      sphere radius=<float> location=x,y,z color=r,g,b

    Returns a dictionary with object info or None if line is empty or invalid.
    """
    tokens = line.strip().split()
    if not tokens:
        return None
    obj_type = tokens[0]
    args = {}
    for token in tokens[1:]:
        if '=' in token:
            key, value = token.split('=', 1)
            args[key] = value
    return {'type': obj_type, 'args': args}


def create_object(info):
    """Create a Blender object based on parsed info."""
    obj_type = info['type']
    args = info['args']
    location = [float(x) for x in args.get('location', '0,0,0').split(',')]
    color = [float(x) for x in args.get('color', '1,1,1').split(',')]
    if obj_type == 'cube':
        size = float(args.get('size', 1))
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    elif obj_type == 'sphere':
        radius = float(args.get('radius', 1))
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
    elif obj_type == 'cylinder':
        radius = float(args.get('radius', 1))
        depth = float(args.get('depth', 2))
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
    else:
        print(f"Unsupported object type: {obj_type}")
        return

    obj = bpy.context.active_object
    mat = bpy.data.materials.new(name=f"mat_{obj.name}")
    mat.diffuse_color = (*color, 1)
    obj.data.materials.append(mat)


if __name__ == '__main__':
    if '--' in sys.argv:
        idx = sys.argv.index('--')
        instructions_file = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
    else:
        instructions_file = None

    if not instructions_file:
        print("Usage: blender --python text_to_blender.py -- <instructions_file>")
        sys.exit(1)

    with open(instructions_file, 'r') as f:
        for line in f:
            info = parse_line(line)
            if info:
                create_object(info)
