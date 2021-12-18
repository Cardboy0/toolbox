import bpy
import bmesh

D = bpy.data


# functions for deleting different kinds of things in Blender


# https://blender.stackexchange.com/questions/27234/python-how-to-completely-remove-an-object


def deleteObjectAndMesh(context,obj):
    """Deletes the specified object AND its mesh.

    Vital for scripts where you create large amounts of objects and delete them again, as the "default" deleting does not remove meshes, meaning they would pile up your file.

    Parameters
    ----------
    obj : bpy.types.Object
        Object to delete
    """
    mesh = obj.data
    D.objects.remove(obj)
    D.meshes.remove(mesh)


# Small note: You can get a list of all indices of e.g. the mesh vertices by writing myIndexList = list( range( len( mesh.vertices)))
def delete_VertsFacesEdges(context, mesh, indexList, type="VERTEX", deleteChildelements=False):
    """Deletes all vertices, edges or faces of your mesh whose index is in the indexList parameter.

    Example: delete_VertsFacesEdges(C, someMesh, [1,5,2,3],"EDGE",False) would delete edges number 1, 2, 3 and 5 from the specified mesh


    Parameters
    ----------
    context : bpy.types.Context
        Most likely bpy.context
    mesh : bpy.types.Mesh
        Mesh whose verts/edges/faces you want deleted
    indexList : list on ints
        A list that contains the indices of all the verts/edges/faces you want deleted.
        Invalid indices (negative or out-of-range) get ignored automatically.
    type : "VERTEX", "EDGE" or "FACE"
        Whether you want to delete vertices, edges or faces (polygons). by default "VERTEX"
    deleteChildElements : bool
        To differentiate between e.g. deleting faces but keeping their edges and vertices, vs deleting them as well. Only matters for type="FACE" or "EDGE", by default False
    """

    bm = bmesh.new()
    bm.from_mesh(mesh)
    # since bm.verts, bm.faces and bm.edges share the same required methods, we can just use "elements" as an alias to save us redundant code.
    if type == "VERTEX":
        elements = bm.verts
        bmeshParameter = "VERTS"
    elif type == "EDGE":
        if deleteChildelements == False:
            elements = bm.edges
            bmeshParameter = "EDGES"
        elif deleteChildelements == True:
            # sadly, there isn't a parameter value for bmesh.ops.delete() that allows us to automatically delete child vertices of an edge or face
            # so we need to get the vertices of each edge manually and delete them
            # their parent edges of course will also get deleted as a result
            elements = bm.verts
            bmeshParameter = "VERTS"
            # the foreach_get() method is exceptionally fast in getting data and thus the best option to use here
            allChildVerts = [0, 0] * len(mesh.edges)
            mesh.edges.foreach_get("vertices", allChildVerts)
            ourChildVerts = []
            for index in indexList:
                if index >= 0 and index < len(mesh.edges):
                    realIndex = index * 2
                    ourChildVerts.extend(allChildVerts[realIndex:realIndex+2])
            # bmesh.ops.delete() doesn't allow duplicate elements, so we simply sort out duplicate indices by turning the list into a set
            ourChildVerts = set(ourChildVerts)
            indexList = ourChildVerts  # the "fixed" version
    elif type == "FACE":
        if deleteChildelements == False:
            elements = bm.faces
            bmeshParameter = "FACES"
        elif deleteChildelements == True:
            # See the comments for the corresponding edges code above
            # Different to above, we cannot use foreach_get() for getting the child vertices of faces like we did with the edges
            # For the simple reason that to efficiently use that method, all faces would need the same amount of child vertices
            # That's not given however - one face could consist of 3 vertices, and the next one of 6
            # So we'll do it a bit more complicated
            elements = bm.verts
            bmeshParameter = "VERTS"
            childVertIndices = set()
            for faceIndex in indexList:
                if faceIndex >= 0 and faceIndex < len(mesh.polygons):
                    face = mesh.polygons[faceIndex]
                    vertIndices = [0] * len(face.vertices)
                    face.vertices.foreach_get(vertIndices)
                    childVertIndices.update(vertIndices)
            indexList = childVertIndices

    else:
        raise Exception(
            "Invalid value for type parameter - only 'VERTEX', 'EDGE' and 'FACE' are recognised")
            
    # bmeshes always want to do this after you create them and after you did changes to some indices, e.g. by removing a vertex:
    elements.ensure_lookup_table()
    maxIndex = len(elements)-1  # user might have given us invalid indices
    elementList = []
    for index in indexList:
        if index >= 0 and index <= maxIndex:
            elementList.append(elements[index])
    # the bmesh opertor wants the actual elements, not their indices, that's why we get them
    # Not the context Blender usually refers to
    bmesh.ops.delete(bm, geom=elementList, context=bmeshParameter)
    # the internet always tells you that you shouldn't use bpy.ops in your code, but is that also true for bmesh.ops? Coding these functionalities by hand would be tedious.

    # deleting an element one by one by getting them via index doesn't work because after each deletion the indices refresh and would need "elements.ensure_lookup_table()" again
    # for element in elementList:
    #    elements.remove(element)

    bm.to_mesh(mesh)
    bm.free()  # "delete" the bmesh
