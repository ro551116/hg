import bpy
import sys
import networkx as nx


def load_graph(path):
    """Load a graph from a DOT file and return positions using spring layout."""
    G = nx.drawing.nx_pydot.read_dot(path)
    # Convert positions to floats if provided
    pos = {}
    for node, data in G.nodes(data=True):
        if 'pos' in data:
            x, y = map(float, data['pos'].strip('"').split(','))
            pos[node] = (x, y, 0)
    if not pos:
        pos2d = nx.spring_layout(G)
        pos = {n: (p[0]*5, p[1]*5, 0) for n, p in pos2d.items()}
    return G, pos


def create_node(name, location):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=location)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=f"mat_{name}")
    mat.diffuse_color = (0.8, 0.8, 0.8, 1)
    obj.data.materials.append(mat)
    return obj


def create_edge(start_loc, end_loc):
    # Create a cylinder between two points
    start = bpy.mathutils.Vector(start_loc)
    end = bpy.mathutils.Vector(end_loc)
    direction = end - start
    distance = direction.length
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=distance,
                                        location=(start + end) / 2)
    obj = bpy.context.active_object
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('Z', 'Y')
    mat = bpy.data.materials.new(name="edge_mat")
    mat.diffuse_color = (0.2, 0.2, 0.2, 1)
    obj.data.materials.append(mat)
    return obj


def build_graph(dot_file):
    G, pos = load_graph(dot_file)
    objects = {}
    for node, loc in pos.items():
        objects[node] = create_node(str(node), loc)
    for u, v in G.edges():
        create_edge(pos[u], pos[v])


if __name__ == '__main__':
    if '--' in sys.argv:
        idx = sys.argv.index('--')
        dot_file = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
    else:
        dot_file = None

    if not dot_file:
        print("Usage: blender --background --python diagram_to_blender.py -- <graph.dot>")
        sys.exit(1)

    build_graph(dot_file)
