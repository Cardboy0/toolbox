import bpy
import warnings

D = bpy.data


def createShapekey(context, obj, reference):
    """Creates a new shapekey for an object with coordinates from the reference. Different reference types are accepted.
    Make sure that a Basis shapekey already exists when using this function.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
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

    origActiveIndex = obj.active_shape_key_index
    origActiveShapekey = obj.active_shape_key

    newShapekey = obj.shape_key_add(from_mix=False)

    obj.active_shape_key_index = origActiveIndex
    if obj.active_shape_key != origActiveShapekey:
        warnings.warn(
            "Had a problem resetting the active shape key. Ignoring...")

    refType = type(reference)

    if refType == bpy.types.Mesh:
        seqCoordinates = [0, 0, 0] * len(obj.data.vertices)
        # doing it with foreach_get/set is like 10 times faster than "normal" set/get methods
        reference.vertices.foreach_get("co", seqCoordinates)
        reference = seqCoordinates
        refType = list

    if refType == list:
        newShapekey.data.foreach_set("co", reference)
    elif refType == dict:
        for vertIndex, coVector in reference.items():
            newShapekey.data[vertIndex].co = coVector

    return newShapekey


def muteAllShapekeys(context, mesh, mute=True, exclude=["BASIS"]):
    """Mutes or unmutes all shapekeys of a mesh except the ones specified!
    Very fast.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
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
    originalMutes = []
    for sk in exclude:
        if sk == "BASIS":
            basisSK = mesh.shape_keys.reference_key
            originalMutes.append((basisSK, basisSK.mute))
            continue
        originalMutes.append((sk, sk.mute))

    # instead of True's and False's, foreach_set() needs 1's and 0's
    mute = int(mute)
    seq = [mute]*len(mesh.shape_keys.key_blocks)
    mesh.shape_keys.key_blocks.foreach_set("mute", seq)

    for sk, origMute in originalMutes:
        sk.mute = origMute
