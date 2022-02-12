import bpy
import mathutils

# for things related to coordinates in Blender


# main reason I created isVectorClose and getVertexCoordinates here even though they're so small
# is as a reminder to use the vector class when dealing with vertices rather than trying to do your own shit with highschool mathematics
# because the former has been coded for performance and thus faster that what you might come up with.


def isVectorClose(context, vector1, vector2, ndigits=6):
    """Checks if two (coordinate) vectors are approx. the same

    Parameters
    ----------
    context : bpy.types.Context
        Probably bpy.context
    vector1 : Vector (mathutils)
        First vector to compare
    vector2 : Vector (mathutils)
        Second vector to compare
    ndigits : int, optional
        The accuracy you want to use. Higher numbers make it more accurate. by default 6

    Returns
    -------
    bool
        Whether they are close to each other or not
    """
    length = (vector1-vector2).length
    return 0 == round(length, ndigits)


def getVertexCoordinates(context, mesh, vertIndices="ALL"):
    """Returns the coordinate vectors of all specified vertices.

    Parameters
    ----------
    context : bpy.types.Context
        Probably bpy.context
    mesh : bpy.types.Mesh
        The mesh in question
    vertIndices : list or "ALL"
        Specifiy your vertices by index, by default "ALL"

    Returns
    -------
    list
        List where listIndex == vertIndex, and the value at that index == coordinateVector\n
        Vertices that weren't specified get a value of None
    """
    vertCoordinates = [None]*len(mesh.vertices)
    if vertIndices == "ALL":
        vertIndices = list(range(len(mesh.vertices)))
    for vertIndex in vertIndices:
        vertCoordinates[vertIndex] = mesh.vertices[vertIndex].co.copy()
    # If my old notes are correct, doing it like this (iterating trough all vertices and using co.copy()) is approx. 30% faster than using foreach_get() to get the x,y,z values and then creating new Vectors from each of those triplets.
    return vertCoordinates
