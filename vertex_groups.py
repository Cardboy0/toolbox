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


# as the name implies, is meant to deal with vertex groups


def create_vertex_group(obj, vg_name="Group"):
    """Creates and returns a new vertex group for the specified object.

    Parameters
    ----------
    obj : bpy.types.Object
        Which object is supposed to get the new vertex group
    vg_name : str
        Name of the new vertex group, by default "Group"

    Returns
    -------
    bpy.types.VertexGroup
        The newly created vertex group
    """
    orig_active_vg = obj.vertex_groups.active
    # creating a new vertex group makes it the "active" one, which I would like to undo
    new_vg = obj.vertex_groups.new(name=vg_name)
    # trying to set vertex_groups.active = None crashes Blender completely as of Blender 3.0
    # setting the active_index to -1 works however
    if orig_active_vg != None:
        obj.vertex_groups.active = orig_active_vg
    else:
        obj.vertex_groups.active_index = -1
    return new_vg


def validate_vert_indices_for_vg(vertex_group_or_mesh, vert_indices, return_type="list"):
    """Removes vertex indices from the supplied list that cannot be used for the given mesh / vertex group

    Parameters
    ----------
    vertex_group_or_mesh : bpy.types.VertexGroup or bpy.types.Mesh
        The vertex group (or mesh in general) you want your indices validated for.
    vert_indices : list-like collection of ints
        The indices of the vertices you want to be validated.
    return_type : "list" or "set"
        What type you want the returned collection of values to have

    Returns
    -------
    set
        valid Indices
    """
    if type(vertex_group_or_mesh) == bpy.types.VertexGroup:
        # VG.id_data returns the object the vg belongs to
        mesh = vertex_group_or_mesh.id_data.data
    else:
        mesh = vertex_group_or_mesh
    total_vert_amount = len(mesh.vertices)
    if return_type == "list":
        it = list
    elif return_type == "set":
        it = set
    return it(filter(lambda index: (index >= 0 and index < total_vert_amount), vert_indices))


def set_vertex_group_values_uniform(vertex_group, vertex_indices="ALL", value=1):
    """Sets all weights of the given vertices to the specified value in the vertex group. 
    If vertices aren't yet part of the vertex group, they will get added automatically.

    Parameters
    ----------
    vertex_group : bpy.types.VertexGroup
        In which vertex group you want to set the weights in.
    vertex_indices : list or similar, containing ints - or "ALL"
        The indices of all vertices whose weight you want changed. By default "ALL".
    value : int
        The weight to give every vertex in vertIndices. By default 1
    """
    if vertex_indices == "ALL":
        obj = vertex_group.id_data
        vertex_indices = range(len(obj.data.vertices))
        # apparently vertexIndices works with range() objects as well
        # we could still cast it into a list with list(range(someNumber)) if it shows to be unstable in the future
    vertex_group.add(vertex_indices, value, "REPLACE")
    # some notes:
    # vertices not yet in the VG will automatically get added to the VG with this
    # do not use "ADD" instead of "REPLACE" - "ADD" *adds* the given value to the current value


def set_vertex_group_values_specific(vertex_group, weights_for_verts):
    """Sets weights of the given vertices to different, specified values in the vertex group. 
    If vertices aren't yet part of the vertex group, they will get added automatically.

    Parameters
    ----------
    vertex_group : bpy.types.VertexGroup
        In which vertex group you want to set the weights in.
    weights_for_verts : dict; {float: multipleInts}
        The dictionary uses weights as keys. Vertices that are supposed to get that weight need to be included in the value (of type list or similar - even if only one int is wanted).
    """
    for weight, vert_indices in weights_for_verts.items():
        set_vertex_group_values_uniform(vertex_group=vertex_group, vertex_indices=vert_indices, value=weight)


def remove_verts_from_vertex_group(vertex_group, vert_indices="ALL", validate=False):
    """Remove the specified vertices from the vertex group.

    Vertex Indices must not be invalid, otherwise Blender will crash completely.



    Parameters
    ----------
    vertex_group : bpy.types.VertexGroup
        In which vertex group you want to set the weights in.
    vert_indices : list containing ints, or "ALL"
        The indices of the vertices you want to be removed. By default "ALL".
        Sets are not allowed
    validate : bool
        If set to True, indices from the supplied list will be automatically validated to prevent a crash each time this function is called. Not recommended, since it increases run time proportionally.

    """

    if vert_indices == "ALL":
        obj = vertex_group.id_data
        vert_indices = range(len(obj.data.vertices))

    if validate == True:
        vert_indices = validate_vert_indices_for_vg(vertex_group_or_mesh=vertex_group, vert_indices=vert_indices,
                                                    return_type="list")

    vertex_group.remove(vert_indices)


def get_verts_in_vertex_group(vertex_group):
    """Tells you which vertices are currently assigned to the given vertex group.

    Parameters
    ----------
    vertex_group : bpy.types.VertexGroup
        The vertex group to analyse

    Returns
    -------
    set
        All indices of vertices that are in the vertex group
    """
    obj = vertex_group.id_data
    found_verts = set()
    for vert_index in range(len(obj.data.vertices)):
        try:
            vertex_group.weight(vert_index)
            found_verts.add(vert_index)
            # you might think that this is stupid, and you'd be right
            # but this seems to be the best possible solution
            # Some posts on the internet do this by searching inside someVertex.groups for the vertex group in question
            # That's at least twice as slow as this function, and with each added vertex group it would require more time. So don't do that.
        except:
            pass
    return found_verts


def get_vertex_weights(vertex_group, vertex_indices):
    """Returns the weights of given vertices inside a vertex group.
    WARNING: All supplied vertices must exist within the vertex group, otherwise Blender will throw an error.

    Parameters
    ----------
    vertex_group : bpy.types.VertexGroup
        The vertex group to analyse
    vertex_indices : List or similar
        Contains the vertex indices to check. All indices must be assigned to the vertex group for this to work!

    Returns
    -------
    list
        Weight of vertex 20 = returnList[20]
    """
    obj = vertex_group.id_data
    total_verts = len(obj.data.vertices)
    weights = [None] * total_verts
    for i in vertex_indices:
        weights[i] = vertex_group.weight(i)
    return weights


# This function below should not be used as the time required will depend on the amount of vertex groups your object posseses
# def getVertsAndWeightsFromVertexGroup(context, vertexGroup, vertIndicesToCheck="ALL", addWeights=True):
#     """Returns the indices of all vertices that are inside the given vertex group, and additionally if desired their respective weights in said vertex group.

#     Parameters
#     ----------
#     context : bpy.types.Context
#         probably bpy.context
#     vertexGroup : bpy.types.VertexGroup
#         The vertex group to analyse
#     vertIndicesToCheck : List or similar, or "ALL"
#         If you only care about some specific vertices, put their indices in this parameter and all other vertices will get ignored. By default "ALL"
#     addWeights : bool
#         Whether you want to also get the weights of the vertices that were found in the vertex group. By default True

#     Returns
#     -------
#     dict
#         returnDict["vertsInside"] is a set that contains all vertices that were found inside\n
#         returnDict["weights"] - list that only gets added if addWeights=True. Contents: returnDict["weights"][vertIndex]==weight. Vertices that got ignored or weren't found get a default value of None.
#     """
#     # Sadly, foreach_get() doesnt work with sets
#     indexVertexGroup = vertexGroup.index
#     dictReturn = dict()
#     obj = vertexGroup.id_data
#     if vertIndicesToCheck == "ALL":
#         vertIndicesToCheck = range(len(obj.data.vertices))
#     vertsInVertexGroup = set()
#     dictReturn["vertsInside"] = vertsInVertexGroup
#     if addWeights:
#         weights = [None]*len(obj.data.vertices)
#         dictReturn["weights"] = weights

#     for vertIndex in vertIndicesToCheck:
#         vert = obj.data.vertices[vertIndex]
#         totalGroups = len(vert.groups)
#         if totalGroups != 0:
#             groupIndeces = [0]*totalGroups
#             # vertex.groups[0].group returns the VG index of the first VG the vertex is part of
#             vert.groups.foreach_get("group", groupIndeces)
#             # while casting a list into a set will take extra time, sets are however magnitudes faster when using the in-operator for large arrays
#             # in theory you could check the total amount of vertex groups the object has at the beginning and then from that amount decide if lists are faster than sets
#             groupIndeces = set(groupIndeces)
#             if indexVertexGroup in groupIndeces:
#                 vertsInVertexGroup.add(vertIndex)
#                 if addWeights:  # these two lines of code look like they could be optimised - by somebody who's not me
#                     # accessing vert.groups[?].weight requires us to know ? first
#                     weights[vertIndex] = vertexGroup.weight(vertIndex)
#     return dictReturn

class VGroupsWithModifiers():
    """
    This class offers some methods for using modifiers to manipulate vertex groups.
    Modifiers allow dynamic changes, like if one vertex groups gets weight changes, another one you set up can too automatically.
    However, modifiers also add some layers of complexity, so if you think that you just want a normal, regular vertex group, better use the other methods
    available in this file.

    Note: When a method calls for a vertex group parameter, it always means you're supposed to give the name of the vertex group, not the vertex group object itself.

    Warning: 

    An important part of vertex groups is, aside from what weight a vertex has, obviously which vertices are even assigned to the vertex group.
    In certain scenarios, a vertex group altering modifier might assign every unassigned vertex with a weight of 0.
    This can later create problems for other modifiers who use that vertex group.

    This shouldn't happen with the modifiers created by the methods of this class in most cases, but not all. Keep this fact in mind when your modifiers give you
    unexpected results. 


    For general use of modifiers, check out the modifiers.py file.
    """
    # personal notes:
    # - new modifiers always seem to get placed last in modifier stack (that's a good thing)
    # - we use the names of vertex groups instead of them directly because almost every modifier uses their names too.
    #       Using them directly only adds potential problems.

    @classmethod
    def vertex_weight_uniform(clss, obj, vg_name: str, only_assigned=False, weight=1):
        """Adds a Vertex Weight Mix modifier that assigns every vertex the specified weight. 
        Can also include vertices that haven't been assigned to the vertex group yet.

        Parameters
        ----------
        obj : bpy.types.Object
            Object that the vertex_group belongs to
        vg_name : str
            Name of the vertex group whose values you want to change
        only_assigned : bool
            If True, only vertices that are assigned to the vertex group will be affected. If False, every vertex the geometry has will be affected.
        weight : float
            Which weight every vertex should have

        Returns
        -------
        bpy.types.VertexWeightMixModifier
            The created vertex weight mix modifier that enacts this weight change.
        """
        mod_vweight_mix = obj.modifiers.new(
            name='uniform ' + vg_name + ' weight:' + str(round(weight, 4)), type='VERTEX_WEIGHT_MIX')
        mod_vweight_mix.vertex_group_a = vg_name
        # even if 0, all vertices will still be assigned to it. You can check that with a mask modifier
        mod_vweight_mix.default_weight_b = weight
        if only_assigned == True:
            mod_vweight_mix.mix_set = 'A'  # 'A' for 'VGroup A'
        else:
            mod_vweight_mix.mix_set = 'ALL'
        mod_vweight_mix.mix_mode = 'SET'  # is displayed as 'Replace'
        return mod_vweight_mix

    @classmethod
    def mimic_external_vertex_group(clss, context, main_obj, target_obj, vg_of_target: str):
        """Adds a Data Transfer Modifier and a new vertex group to the main object. 
        The new vertex group will mimic the weights of the chosen vertex group of the target object and have the same name.

        Requirements: Both objects must have the same topology (simply: same number of vertices in viewport)  

        Warning: 
        - I did not test nor plan for what happens if your main object already has a vertex group with the name of the target vertex group.
        You might get unexpected results.
        - Be aware that edge cases exist where the new vertex group will assign every unassigned vertex with a weight of zero instead of leaving them unassigned.
        This depends on certain topology-changing modifiers, like a geometry node modifier.

        Parameters
        ----------
        context : bpy.types.Context
            probably bpy.context
        main_obj : bpy.types.Object
            Object that is supposed to get the vertex group data
        target_obj : bpy.types.Object
            Which object to get the vertex group data from
        vg_of_target : str
            Name of the vertex group of the obj_target you want to steal

        Returns
        -------
        bpy.types.DataTransferModifier
            The created data transfer modifier that keeps the new vertex group up to date with the target vertex group.
        You can get the new vertex group by using the name of the target vertex group.
        """
        mod_data_transfer = main_obj.modifiers.new(
            name='Keeps ' + vg_of_target + ' up to date with data from ' + target_obj.name, type='DATA_TRANSFER')
        mod_data_transfer.object = target_obj
        mod_data_transfer.use_vert_data = True
        mod_data_transfer.data_types_verts = {'VGROUP_WEIGHTS'}
        mod_data_transfer.vert_mapping = 'TOPOLOGY'
        mod_data_transfer.layers_vgroup_select_src = vg_of_target
        # using bpy ops is always best done with a context override
        override = {
            'object': main_obj,
            'active_object': main_obj,
            'scene': context.scene
        }
        bpy.ops.object.datalayout_transfer(
            override, modifier=mod_data_transfer.name)
        # This is the same as pressing the "Generate Data Layers" button of the modifier.
        # At this point, the new vertex group will automatically be added to the main object.
        # Some more notes: if the modifier is deleted, the group still exists but will be completely empty -> useless
        return mod_data_transfer

    @classmethod
    def mimic_vertex_group(clss, obj, vg_to_duplicate: str):
        """ Basically duplicates a vertex group by using a Vertex Weight Mix Modifier.

        If you want the same but for a vertex group from another object, use the mimic_external_vertex_group() method.

        Parameters
        ----------
        obj : bpy.types.Object
            Your object
        vg_to_duplicate : str
            The name of the vertex group you want to get a duplicate for.

        Returns
        -------
        dict
            {"mod": Created Vertex Weight Mix Modififer, "new vg": Created vertex group that acts as the duplicate}
        """
        vg_copy = obj.vertex_groups.new(
            name="Duplicate of (" + vg_to_duplicate + ")")
        mod_vweight_mix = obj.modifiers.new(
            name='Duplicate vg ' + vg_to_duplicate, type='VERTEX_WEIGHT_MIX')
        mod_vweight_mix.vertex_group_a = vg_copy.name
        mod_vweight_mix.vertex_group_b = vg_to_duplicate
        # 'B' for 'VGroup B', if instead 'ALL' then all vertices will be assigned, just some with a weight of 0 without you noticing
        mod_vweight_mix.mix_set = 'B'
        mod_vweight_mix.mix_mode = 'SET'  # What you see as 'Replace'
        return {"mod": mod_vweight_mix, "new vg": vg_copy}

    @classmethod
    def remove_0_weights(clss, obj, vg_name: str):
        """Removes/unassigns any vertex with a weight of 0 from a vertex group using a Vertex Weight Edit Modifier.

        Parameters
        ----------
        obj : bpy.types.Object
            Object that is supposed to get the new modifier.
        vg_name : str
            Name of the vertex group in question that's supposed to get 0 weight values removed.

        Returns
        -------
        bpy.types.VertexWeightEditModifier
            The created Vertex Weight Edit modifier that removes any weights with a value of 0.
        """
        # Note:
        # Vertex Weight Modifiers can remove/unassign all vertices whose weights are below a chosen threshold.
        # Choosing a threshold of 0 to only remove vertices with a weight of 0 will not work however, because the modifier doesn't see 0 as lower than 0
        # To get around this, we set the threshold to a number that's just above zero but so small that it
        # makes no practical difference for any vertices with weights above 0
        # Something like 0.0000000000000000000000000000000000000000000001
        mod_vweight_edit = obj.modifiers.new(
            name="Remove 0 weight vertices from " + vg_name, type='VERTEX_WEIGHT_EDIT')
        smallest_number = 1e-45
        # This is a zero with 45 zeroes behind the dot and one 1 at the end.
        # After some testing, this seems to be (almost) the smallest number you can give to a Blender float property.
        # Because if you use 1e-46,Blender will just reset the property to exactly 0.
        # Sidenote: Python itself is able to go down to 5e-324
        mod_vweight_edit.vertex_group = vg_name
        mod_vweight_edit.use_remove = True
        mod_vweight_edit.remove_threshold = smallest_number
        return mod_vweight_edit
