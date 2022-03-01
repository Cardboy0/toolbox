import bpy
import bmesh


# functions for deleting different kinds of things in Blender


# https://blender.stackexchange.com/questions/27234/python-how-to-completely-remove-an-object


def deleteObjectTogetherWithData(context, obj):
    """Deletes the specified object AND its data (depending on the type this can be the a mesh, armature, light, etc.)

    Vital for scripts where you create large amounts of objects and delete them again, as the "default" deleting does not remove the obj.data, meaning they would pile up in your file.


    Parameters
    ----------
    obj : bpy.types.Object
        Object to delete
    """

    acceptedTypesDict = "acceptedTypes"
    # creating this dictionary everytime this function is called would waste time, so instead we declare it as a function property once and then access it later again everytime
    # I tried to declare the property outside of the function, but when I then used the function in an add-on I got some _RestrictData access () exception
    # so we do it inside
    if (getattr(deleteObjectTogetherWithData, acceptedTypesDict, False) == False):
        # all classes below (except the None class) are subclasses of the Blender bpy.types.ID class:
        # https://docs.blender.org/api/current/bpy.types.ID.html
        # the values are the method to use to remove an obj.data of that type
        deleteObjectTogetherWithData.acceptedTypes = {
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

    objData = obj.data
    dataType = type(objData)

    # getting the correct method to remove the obj.data from where it is stored in bpy.data
    removeMethod = deleteObjectTogetherWithData.acceptedTypes.get(
        dataType, False)
    if removeMethod == False:
        # means main type is not in dictionary, which is the case for subclasses (such as bpy.types.TextCurve, which is a subclass of bpy.types.Curve)
        # so we check out the parent classes next
        for parentClass in dataType.__bases__:
            removeMethod = deleteObjectTogetherWithData.acceptedTypes.get(
                parentClass, False)
            if removeMethod != False:
                break
        if removeMethod == False:
            raise Exception(
                "Class of object's data is not recognised: " + str(type(objData)))

    bpy.data.objects.remove(obj)
    removeMethod(objData)


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
