import bpy


# as the name implies, is meant to deal with vertex groups


def createVertexGroup(context, obj, vgName="Group"):
    """Creates and returns a new vertex group for the specified object.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    obj : bpy.types.Object
        Which object is supposed to get the new vertex group
    vgName : str
        Name of the new vertex group, by default "Group"

    Returns
    -------
    bpy.types.VertexGroup
        The newly created vertex group
    """
    origActiveVG = obj.vertex_groups.active
    # creating a new vertex group makes it the "active" one, which I would like to undo
    newVG = obj.vertex_groups.new(name=vgName)
    # trying to set vertex_groups.active = None crashes Blender completely as of Blender 3.0
    # setting the active_index to -1 works however
    if origActiveVG != None:
        obj.vertex_groups.active = origActiveVG
    else:
        obj.vertex_groups.active_index = -1
    return newVG


def validateVertIndicesForVG(context, vertexGroupOrMesh, vertIndices, returnType="list"):
    """Removes vertex indices from the supplied list that cannot be used for the given mesh / vertex group

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    vertexGroupOrMesh : bpy.types.VertexGroup or bpy.types.Mesh
        The vertex group (or mesh in general) you want your indices validated for.
    vertIndices : list-like collection of ints
        The indices of the vertices you want to be validated.
    returnType : "list" or "set"
        What type you want the returned collection of values to have

    Returns
    -------
    set
        valid Indices
    """
    if type(vertexGroupOrMesh) == bpy.types.VertexGroup:
        # VG.id_data returns the object the vg belongs to
        mesh = vertexGroupOrMesh.id_data.data
    else:
        mesh = vertexGroupOrMesh
    totalVertAmount = len(mesh.vertices)
    if returnType == "list":
        it = list
    elif returnType == "set":
        it = set
    return it(filter(lambda index: (index >= 0 and index < totalVertAmount), vertIndices))


def setVertexGroupValuesUniform(context, vertexGroup, vertexIndices="ALL", value=1):
    """Sets all weights of the given vertices to the specified value in the vertex group. 
    If vertices aren't yet part of the vertex group, they will get added automatically.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    vertexGroup : bpy.types.VertexGroup
        In which vertex group you want to set the weights in.
    vertexIndices : list or similar, containing ints - or "ALL"
        The indices of all vertices whose weight you want changed. By default "ALL".
    value : int
        The weight to give every vertex in vertIndices. By default 1
    """
    if vertexIndices == "ALL":
        obj = vertexGroup.id_data
        vertexIndices = range(len(obj.data.vertices))
        # apparently vertexIndices works with range() objects as well
        # we could still cast it into a list with list(range(someNumber)) if it shows to be unstable in the future
    vertexGroup.add(vertexIndices, value, "REPLACE")
    # some notes:
    # vertices not yet in the VG will automatically get added to the VG with this
    # do not use "ADD" instead of "REPLACE" - "ADD" *adds* the given value to the current value


def setVertexGroupValuesSpecific(context, vertexGroup, weightsForVerts):
    """Sets weights of the given vertices to different, specified values in the vertex group. 
    If vertices aren't yet part of the vertex group, they will get added automatically.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    vertexGroup : bpy.types.VertexGroup
        In which vertex group you want to set the weights in.
    weightsForVerts : dict; {float: multipleInts}
        The dictionary uses weights as keys. Vertices that are supposed to get that weight need to be included in the value (of type list or similar - even if only one int is wanted).
    """
    for weight, vertIndices in weightsForVerts.items():
        setVertexGroupValuesUniform(
            context=context, vertexGroup=vertexGroup, vertexIndices=vertIndices, value=weight)


def removeVertsFromVertexGroup(context, vertexGroup, vertIndices="ALL", validate=False):
    """Remove the specified vertices from the vertex group.

    Vertex Indices must not be invalid, otherwise Blender will crash completely.



    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    vertexGroup : bpy.types.VertexGroup
        In which vertex group you want to set the weights in.
    vertIndices : list containing ints, or "ALL"
        The indices of the vertices you want to be removed. By default "ALL".
        Sets are not allowed
    validate : bool
        If set to True, indices from the supplied list will be automatically validated to prevent a crash each time this function is called. Not recommended, since it increases run time proportionally.

    """

    if vertIndices == "ALL":
        obj = vertexGroup.id_data
        vertIndices = range(len(obj.data.vertices))

    if validate == True:
        vertIndices = validateVertIndicesForVG(
            context=context, vertexGroupOrMesh=vertexGroup, vertIndices=vertIndices, returnType="list")

    vertexGroup.remove(vertIndices)


def getVertsInVertexGroup(context, vertexGroup):
    """Tells you which vertices are currently assigned to the given vertex group.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    vertexGroup : bpy.types.VertexGroup
        The vertex group to analyse

    Returns
    -------
    set
        All indices of vertices that are in the vertex group
    """
    obj = vertexGroup.id_data
    foundVerts = set()
    for vertIndex in range(len(obj.data.vertices)):
        try:
            vertexGroup.weight(vertIndex)
            foundVerts.add(vertIndex)
            # you might think that this is stupid, and you'd be right
            # but this seems to be the best possible solution
            # Some posts on the internet do this by searching inside someVertex.groups for the vertex group in question
            # That's at least twice as slow as this function, and with each added vertex group it would require more time. So don't do that.
        except:
            pass
    return foundVerts


def getVertexWeights(context, vertexGroup, vertexIndices):
    """Returns the weights of given vertices inside a vertex group.
    WARNING: All supplied vertices must exist within the vertex group, otherwise Blender will throw an error.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    vertexGroup : bpy.types.VertexGroup
        The vertex group to analyse
    vertexIndices : List or similar
        Contains the vertex indices to check. All indices must be assigned to the vertex group for this to work!

    Returns
    -------
    list
        Weight of vertex 20 = returnList[20]
    """
    obj = vertexGroup.id_data
    totalVerts = len(obj.data.vertices)
    weights = [None]*totalVerts
    for i in vertexIndices:
        weights[i] = vertexGroup.weight(i)
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
