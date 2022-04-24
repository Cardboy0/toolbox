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


def create_real_mesh_copy(context, obj, frame="CURRENT", apply_transforms=True, keep_vertex_groups=False, keep_materials=False):
    """Creates a (static) copy of your chosen mesh where basically every deformation has been applied. This includes modifiers, shapekeys, etc.
    You can choose to keep certain properties (see function parameters)
    Transformations (size, scale, rotation) can be excluded by setting the apply_transforms parameter to False

    Parameters
    ----------
    context : bpy.types.Context
        Most likely bpy.context
    obj : bpy.types.Object
        The object with your mesh.
    frame : "CURRENT" or int
        The frame where your mesh has the desired shape, by default "CURRENT"
    apply_transforms : bool
        Whether you also want to apply transformations to your mesh (size, scale, rotation), by default True
    keep_vertex_groups : bool
        Whether you want the mesh to keep the data of any vertex groups it currentely possesses. If True, vertex groups will reappear automatically when you assign the mesh to an object.
    keep_materials : bool
        Whether you want to keep any material links the mesh has, by default False

    Returns
    -------
    bpy.types.Mesh
        The newly created mesh

    Warnings
    --------
    - You might get wrong results if your context.area.type is not either "CONSOLE", "VIEW_3D" or "TEXT_EDITOR"\\
        An example for a "bad" area type is "PROPERTIES", and you might encounter it when you're writing an add-on with an operator that gets called by clicking 
        a button in the object properties panel.\\
        Temporarily setting context.area.type="CONSOLE", calling this function and then setting it back to original is enough to make those bugs go away.
    """

    # frame stuff
    orig_frame = context.scene.frame_current
    if frame != "CURRENT" and frame != orig_frame:
        context.scene.frame_set(frame)

    dp_graph = context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(dp_graph)
    # IMPORTANT: Do not try to make changes to obj_eval in any way. They will (somehow) very likely persist even after this function is finished or you try to create it again.
    # For example deleting vertex groups would delete them from future obj_evals as well (but not the original object) - until you restart Blender.

    real_mesh = bpy.data.meshes.new_from_object(obj_eval)

    if apply_transforms == True or keep_vertex_groups == False or keep_materials == False:
        # TODO: Check how much more time creating tempObj requires. I did some testing and got weird, unusable results, but it seems like without tempObj it's at least in some cases twice as fast.
        temp_obj = bpy.data.objects.new("temporary object", real_mesh)
        # As written above, we should only use obj_eval for getting information, not changing anything.
        # So we create a temporary object to act as a substitute for certain operations, and delete it afterwards again.

        if apply_transforms == True:
            # some notes: depsgraph takes modifiers and shapekeys into account, but NOT object transformations
            # (i.e. changes to size, scale and rotation through various, different means)
            # Luckily however, the sum of all transformations are located at YourObject.matrix_world
            # We can then use YourMesh.transform(the_matrix_world) to "apply" all the transformations to the mesh
            # this is only valid for the current frame
            transformation_matrix = obj.matrix_world
            real_mesh.transform(transformation_matrix)

        if keep_vertex_groups == False:
            temp_obj.vertex_groups.clear()
            # believe it or not, but by default any vertex groups will stay with the mesh and reappear when you assign it to an object
            # probably because every vertex has a .groups attribute with any vertex group data.

        if keep_materials == False:
            # similar to Vertex Groups, materials also stay with the mesh by default
            real_mesh.materials.clear()

        bpy.data.objects.remove(temp_obj)

    # resetting to original frame if we had changed it at the beginning
    if context.scene.frame_current != orig_frame:
        context.scene.frame_set(orig_frame)

    return real_mesh


def create_new_obj_for_mesh(context, name, mesh):
    """Creates a new object for a mesh and links it to the master collection of the current scene.

    Parameters
    ----------
    context : bpy.types.Context
        Most likely bpy.context
    name : str
        Desired name of your new object
    mesh : bpy.types.Mesh
        The mesh you want the object to have

    Returns
    -------
    bpy.types.Object
        The new object
    """
    new_obj = bpy.data.objects.new(name, mesh)
    context.scene.collection.objects.link(new_obj)
    return new_obj
