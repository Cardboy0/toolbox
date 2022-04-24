# ##### BEGIN GPL LICENSE BLOCK #####
#
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
#
# ##### END GPL LICENSE BLOCK #####


import bpy
import warnings


def create_shapekey(obj, reference):
    """Creates a new shapekey for an object with coordinates from the reference. Different reference types are accepted.
    Make sure that a Basis shapekey already exists when using this function.

    Parameters
    ----------
    obj : bpy.types.Object
        Which object is supposed to get the shapekey
    reference : either bpy.types.Mesh, list, or dictionary (list is the fastest)
        list: Requires length of 3 times the amount of vertices the object mesh has, with only float values. First 3 values are interpreted as x,y,z of vertex 1, second 3 values as x,y,z of vertex 2, and so on...\n
        mesh: Any other mesh with the same amount of vertices\n
        dictionary: No specific length required, just this structure: {vertexIndex: coordinateVector, vertexIndex: coordinateVector, etc...}. Make sure the vectors are copies of the original ones.

    Returns
    -------
    bpy.types.ShapeKey
        The created shape key
    """
    # if hasattr(obj.data.shape_keys,"reference_key") == False:
    #     #create basis shapekey
    #     basisShapekey = obj.shape_key_add(name="Basis")

    orig_active_index = obj.active_shape_key_index
    orig_active_shapekey = obj.active_shape_key

    new_shapekey = obj.shape_key_add(from_mix=False)

    obj.active_shape_key_index = orig_active_index
    if obj.active_shape_key != orig_active_shapekey:
        warnings.warn(
            "Had a problem resetting the active shape key. Ignoring...")

    ref_type = type(reference)

    if ref_type == bpy.types.Mesh:
        seq_coordinates = [0, 0, 0] * len(obj.data.vertices)
        # doing it with foreach_get/set is like 10 times faster than "normal" set/get methods
        reference.vertices.foreach_get("co", seq_coordinates)
        reference = seq_coordinates
        ref_type = list

    if ref_type == list:
        new_shapekey.data.foreach_set("co", reference)
    elif ref_type == dict:
        for vertIndex, coVector in reference.items():
            new_shapekey.data[vertIndex].co = coVector

    return new_shapekey


def mute_all_shapekeys(mesh, mute=True, exclude=["BASIS"]):
    """Mutes or unmutes all shapekeys of a mesh except the ones specified!
    Very fast.

    Parameters
    ----------
    mesh : bpy.types.Mesh
        The mesh that has the shape keys
    mute : bool
        True -> mutes all, False -> unmutes all
    exclude : list or similar containing bpy.types.ShapeKey and/or "BASIS" for the basis shapekey
        The shapekeys whose mute status you don't want to change.
        Shapekeys in here will slow the function down with increasing amounts.
    """
    # first we mute (or unmute) all, and then reset the mute status of theshapekeys in "exclude"
    # fyi, getting the index of a shapekey seems to mostly be guesswork, so we shouldn't work with individual indices
    original_mutes = []
    for sk in exclude:
        if sk == "BASIS":
            basis_sk = mesh.shape_keys.reference_key
            original_mutes.append((basis_sk, basis_sk.mute))
            continue
        original_mutes.append((sk, sk.mute))

    # instead of True's and False's, foreach_set() needs 1's and 0's
    mute = int(mute)
    seq = [mute] * len(mesh.shape_keys.key_blocks)
    mesh.shape_keys.key_blocks.foreach_set("mute", seq)

    for sk, orig_mute in original_mutes:
        sk.mute = orig_mute
