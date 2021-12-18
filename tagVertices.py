import bpy
import random
import bmesh
#import math
D = bpy.data


class TagVertices:
    """
    Contains a few methods that help with "tagging" vertices, i.e. being able to identify a specifc vertex even after its index has changed.

    (Unlike with most other objects in Blender, it seems like you cannot assign vertices to variables in a stable way. Once you switch to Edit and then back to Object mode, they lose their validity. 
    See https://developer.blender.org/T88914 for more on that.)

    Works by using int data layers.
    """

    @staticmethod
    def tag(context,mesh, layerName="tagged_vertices", vertIndices="ALL"):
        """Tags the vertices with an int data layer so they can be identified by other methods of this class later.

        Parameters
        ----------
        mesh : bpy.types.Mesh
            The mesh whose vertices you want tagged
        layerName : str, optional
            The name you want the new data layer to have, by default "tagged_vertices"
            It's not guaranteed that this name will actually be possible.
        vertIndices : int-list or "ALL", optional
            If you only want to tag specific vertices, put their indices in a list for this parameter., by default "ALL"

        Returns
        -------
        dictionary
            contains "LAYERNAME" (The actual name that has been chosen for the Layer)
            and "LAYERVALUES" (The values the vertices were tagged with. You need this list for the other methods)
        """
        # check if a layer with that name already exist and change name accordingly
        while True:
            if mesh.vertex_layers_int.find(layerName) != -1:
                layerName = layerName+str(random.randint(0, 9))
            else:
                break

        # create new layer
        mesh.vertex_layers_int.new(name=layerName)

        if vertIndices == "ALL":
            vertIndices = list(range(0, len(mesh.vertices)))  # [0,1,2,3,4,...]

        layerValues = [0]*len(mesh.vertices)
        for index in vertIndices:
            layerValues[index] = index+1
            # normally you would give assign the vertex 23 also a value of 23, but since 0 is used as the defautl value, we should add 1 to every index, so vert23 = value24

        # set the value of each vertex to index+1
        mesh.vertex_layers_int[layerName].data.foreach_set(
            "value", layerValues)
        return {"LAYERNAME": layerName, "LAYERVALUES": layerValues}

    @staticmethod
    # returns a list where the position of a value is the old index, and the value itself the new index
    def identifyVerts(context,mesh, layerName, oldLayerValues):
        """Find out which old vertex is which new vertex in your mesh. You need the dictionary from the tag() method for this

        Parameters
        ----------
        mesh : bpy.types.Mesh
            Mesh which vertices you have tagged before
        layerName : str
            The name of the data layer that has been created previously
        oldLayerValues : list
            The returned value list from the tag() method

        Returns
        -------
        list of int
            The index of a value in this list equals the OLD vertex index of a specifc vertex, the value itself is the NEW vertex index of the same vertex.
            A value of -1 means that this old vertex doesn't exist anymore.
        """
        # basically, oldLayerValues looks like this:
        # oldLayerValues[oldIndex] = assignedValueInLayer
        # but what we want to return is:
        # old_vs_new[oldIndex] = newIndex

        newLayerValues = [0]*len(mesh.vertices)
        mesh.vertex_layers_int[layerName].data.foreach_get(
            "value", newLayerValues)
        # newLayerValues[newIndex] = assignedValueInLayer

        # value of -1 is basically our own default and means that the old vertex couldn't be found in the mesh anymore
        old_vs_new = [-1]*len(oldLayerValues)

        for newIndex in range(len(newLayerValues)):
            oldIndex = newLayerValues[newIndex] - 1
            # remember that value == oldIndex+1
            old_vs_new[oldIndex] = newIndex

        return old_vs_new

    @staticmethod
    # removes a datalayer
    def removeLayer(context,mesh, layerName):
        """Removes a data layer that has been created by the tag() method. Not actually neccessary, but advisable.

        Parameters
        ----------
        mesh : bpy.types.Mesh
        layerName : str
        """
        # either I'm blind or you actually cannot remove a vertex layer in an easy way
        # bmesh allows it though, so we will have to use that
        bm = bmesh.new()
        bm.from_mesh(mesh)
        #layer = bm.verts.layer.int[layerName]
        bm.verts.layers.int.remove(bm.verts.layers.int[layerName])
        bm.to_mesh(mesh)
        bm.free()

    # def update(self):
    #
    #    # ??????
    #    None
