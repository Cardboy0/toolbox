# Part of the "toolbox" repository
# Copyright (C) 2022  Cardboy0 (https://twitter.com/cardboy0)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import bpy
import bmesh


# functions for deleting different kinds of things in Blender


# https://blender.stackexchange.com/questions/27234/python-how-to-completely-remove-an-object


def delete_object_together_with_data(obj):
    """Deletes the specified object AND its data (depending on the type this can be the a mesh, armature, light, etc.)

    Vital for scripts where you create large amounts of objects and delete them again, as the "default" deleting does not remove the obj.data, meaning they would pile up in your file.


    Parameters
    ----------
    obj : bpy.types.Object
        Object to delete
    """
    # TODO: Check out what unlinking is, and if it isn't a better alternative.
    accepted_types_dict = "acceptedTypes"
    # creating this dictionary everytime this function is called would waste time, so instead we declare it as a function property once and then access it later again everytime
    # I tried to declare the property outside of the function, but when I then used the function in an add-on I got some _RestrictData access () exception
    # so we do it inside
    if (getattr(delete_object_together_with_data, accepted_types_dict, False) == False):
        # all classes below (except the None class) are subclasses of the Blender bpy.types.ID class:
        # https://docs.blender.org/api/current/bpy.types.ID.html
        # the values are the method to use to remove an obj.data of that type
        delete_object_together_with_data.acceptedTypes = {
            bpy.types.Mesh: (bpy.data.meshes.remove),
            bpy.types.Armature: (bpy.data.armatures.remove),
            bpy.types.Camera: (bpy.data.cameras.remove),
            bpy.types.Curve: (bpy.data.curves.remove),
            bpy.types.GreasePencil: (bpy.data.grease_pencils.remove),
            bpy.types.Image: (bpy.data.images.remove),
            bpy.types.Lattice: (bpy.data.lattices.remove),
            bpy.types.Light: (bpy.data.lights.remove),
            bpy.types.LightProbe: (bpy.data.lightprobes.remove),
            bpy.types.MetaBall: (bpy.data.metaballs.remove),
            bpy.types.Speaker: (bpy.data.speakers.remove),
            # nothing to do with your computer volumes, I checked ;)
            bpy.types.Volume: (bpy.data.volumes.remove),

            # does Nothing, which is exactly what we want. "placeholder" exists as an argument so we can call this function with a objData, even if it is None
            # empties and some other objects have None as obj.data
            type(None): lambda placeholder: None
        }

    obj_data = obj.data
    data_type = type(obj_data)

    # getting the correct method to remove the obj.data from where it is stored in bpy.data
    remove_method = delete_object_together_with_data.acceptedTypes.get(
        data_type, False)
    if remove_method == False:
        # means main type is not in dictionary, which is the case for subclasses (such as bpy.types.TextCurve, which is a subclass of bpy.types.Curve)
        # so we check out the parent classes next
        for parent_class in data_type.__bases__:
            remove_method = delete_object_together_with_data.acceptedTypes.get(
                parent_class, False)
            if remove_method != False:
                break
        if remove_method == False:
            raise Exception(
                "Class of object's data is not recognised: " + str(type(obj_data)))

    bpy.data.objects.remove(obj)
    remove_method(obj_data)


# Small note: You can get a list of all indices of e.g. the mesh vertices by writing myIndexList = list( range( len( mesh.vertices)))
def delete_verts_faces_edges(mesh, index_list, type="VERTEX", delete_child_elements=False):
    """Deletes all vertices, edges or faces of your mesh whose index is in the indexList parameter.

    Example: delete_VertsFacesEdges(C, someMesh, [1,5,2,3],"EDGE",False) would delete edges number 1, 2, 3 and 5 from the specified mesh


    Parameters
    ----------
    mesh : bpy.types.Mesh
        Mesh whose verts/edges/faces you want deleted
    index_list : list on ints
        A list that contains the indices of all the verts/edges/faces you want deleted.
        Invalid indices (negative or out-of-range) get ignored automatically.
    type : "VERTEX", "EDGE" or "FACE"
        Whether you want to delete vertices, edges or faces (polygons). by default "VERTEX"
    delete_child_elements : bool
        To differentiate between e.g. deleting faces but keeping their edges and vertices, vs deleting them as well. Only matters for type="FACE" or "EDGE", by default False
    """

    bm = bmesh.new()
    bm.from_mesh(mesh)
    # since bm.verts, bm.faces and bm.edges share the same required methods, we can just use "elements" as an alias to save us redundant code.
    if type == "VERTEX":
        elements = bm.verts
        bmesh_parameter = "VERTS"
    elif type == "EDGE":
        if delete_child_elements == False:
            elements = bm.edges
            bmesh_parameter = "EDGES"
        elif delete_child_elements == True:
            # sadly, there isn't a parameter value for bmesh.ops.delete() that allows us to automatically delete child vertices of an edge or face
            # so we need to get the vertices of each edge manually and delete them
            # their parent edges of course will also get deleted as a result
            elements = bm.verts
            bmesh_parameter = "VERTS"
            # the foreach_get() method is exceptionally fast in getting data and thus the best option to use here
            all_child_verts = [0, 0] * len(mesh.edges)
            mesh.edges.foreach_get("vertices", all_child_verts)
            our_child_verts = []
            for index in index_list:
                if index >= 0 and index < len(mesh.edges):
                    real_index = index * 2
                    our_child_verts.extend(
                        all_child_verts[real_index:real_index + 2])
            # bmesh.ops.delete() doesn't allow duplicate elements, so we simply sort out duplicate indices by turning the list into a set
            our_child_verts = set(our_child_verts)
            index_list = our_child_verts  # the "fixed" version
    elif type == "FACE":
        if delete_child_elements == False:
            elements = bm.faces
            bmesh_parameter = "FACES"
        elif delete_child_elements == True:
            # See the comments for the corresponding edges code above
            # Different to above, we cannot use foreach_get() for getting the child vertices of faces like we did with the edges
            # For the simple reason that to efficiently use that method, all faces would need the same amount of child vertices
            # That's not given however - one face could consist of 3 vertices, and the next one of 6
            # So we'll do it a bit more complicated
            elements = bm.verts
            bmesh_parameter = "VERTS"
            child_vert_indices = set()
            for face_index in index_list:
                if face_index >= 0 and face_index < len(mesh.polygons):
                    face = mesh.polygons[face_index]
                    vert_indices = [0] * len(face.vertices)
                    face.vertices.foreach_get(vert_indices)
                    child_vert_indices.update(vert_indices)
            index_list = child_vert_indices

    else:
        raise Exception(
            "Invalid value for type parameter - only 'VERTEX', 'EDGE' and 'FACE' are recognised")

    # bmeshes always want to do this after you create them and after you did changes to some indices, e.g. by removing a vertex:
    elements.ensure_lookup_table()
    max_index = len(elements) - 1  # user might have given us invalid indices
    element_list = []
    for index in index_list:
        if index >= 0 and index <= max_index:
            element_list.append(elements[index])
    # the bmesh opertor wants the actual elements, not their indices, that's why we get them
    # Not the context Blender usually refers to
    bmesh.ops.delete(bm, geom=element_list, context=bmesh_parameter)
    # the internet always tells you that you shouldn't use bpy.ops in your code, but is that also true for bmesh.ops? Coding these functionalities by hand would be tedious.

    # deleting an element one by one by getting them via index doesn't work because after each deletion the indices refresh and would need "elements.ensure_lookup_table()" again
    # for element in elementList:
    #    elements.remove(element)

    bm.to_mesh(mesh)
    bm.free()  # "delete" the bmesh
