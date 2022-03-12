import bpy


# as the name implies, is meant to deal with vertex groups


def create_vertex_group(context, obj, vg_name="Group"):
    """Creates and returns a new vertex group for the specified object.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
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


def validate_vert_indices_for_vg(context, vertex_group_or_mesh, vert_indices, return_type="list"):
    """Removes vertex indices from the supplied list that cannot be used for the given mesh / vertex group

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
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


def set_vertex_group_values_uniform(context, vertex_group, vertex_indices="ALL", value=1):
    """Sets all weights of the given vertices to the specified value in the vertex group. 
    If vertices aren't yet part of the vertex group, they will get added automatically.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
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


def set_vertex_group_values_specific(context, vertex_group, weights_for_verts):
    """Sets weights of the given vertices to different, specified values in the vertex group. 
    If vertices aren't yet part of the vertex group, they will get added automatically.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    vertex_group : bpy.types.VertexGroup
        In which vertex group you want to set the weights in.
    weights_for_verts : dict; {float: multipleInts}
        The dictionary uses weights as keys. Vertices that are supposed to get that weight need to be included in the value (of type list or similar - even if only one int is wanted).
    """
    for weight, vert_indices in weights_for_verts.items():
        set_vertex_group_values_uniform(
            context=context, vertex_group=vertex_group, vertex_indices=vert_indices, value=weight)


def remove_verts_from_vertex_group(context, vertex_group, vert_indices="ALL", validate=False):
    """Remove the specified vertices from the vertex group.

    Vertex Indices must not be invalid, otherwise Blender will crash completely.



    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
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
        vert_indices = validate_vert_indices_for_vg(
            context=context, vertex_group_or_mesh=vertex_group, vert_indices=vert_indices, return_type="list")

    vertex_group.remove(vert_indices)


def get_verts_in_vertex_group(context, vertex_group):
    """Tells you which vertices are currently assigned to the given vertex group.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
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


def get_vertex_weights(context, vertex_group, vertex_indices):
    """Returns the weights of given vertices inside a vertex group.
    WARNING: All supplied vertices must exist within the vertex group, otherwise Blender will throw an error.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
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
