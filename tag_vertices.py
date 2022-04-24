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
import random
import bmesh
#import math


class TagVertices:
    """
    Contains a few methods that help with "tagging" vertices, i.e. being able to identify a specifc vertex even after its index has changed.

    (Unlike with most other objects in Blender, it seems like you cannot assign vertices to variables in a stable way. Once you switch to Edit and then back to Object mode, they lose their validity. 
    See https://developer.blender.org/T88914 for more on that.)

    Works by using int data layers.
    """

    @staticmethod
    def tag(mesh, layer_name="tagged_vertices", vert_indices="ALL"):
        """Tags the vertices with an int data layer so they can be identified by other methods of this class later.

        Parameters
        ----------
        mesh : bpy.types.Mesh
            The mesh whose vertices you want tagged
        layer_name : str, optional
            The name you want the new data layer to have, by default "tagged_vertices"
            It's not guaranteed that this name will actually be possible.
        vert_indices : int-list or "ALL", optional
            If you only want to tag specific vertices, put their indices in a list for this parameter., by default "ALL"

        Returns
        -------
        dictionary
            contains "LAYERNAME" (The actual name that has been chosen for the Layer)
            and "LAYERVALUES" (The values the vertices were tagged with. You need this list for the other methods)
        """
        # check if a layer with that name already exist and change name accordingly
        while True:
            if mesh.vertex_layers_int.find(layer_name) != -1:
                layer_name = layer_name + str(random.randint(0, 9))
            else:
                break

        # create new layer
        mesh.vertex_layers_int.new(name=layer_name)

        if vert_indices == "ALL":
            # [0,1,2,3,4,...]
            vert_indices = list(range(0, len(mesh.vertices)))

        layer_values = [0] * len(mesh.vertices)
        for index in vert_indices:
            layer_values[index] = index + 1
            # normally you would give assign the vertex 23 also a value of 23, but since 0 is used as the defautl value, we should add 1 to every index, so vert23 = value24

        # set the value of each vertex to index+1
        mesh.vertex_layers_int[layer_name].data.foreach_set(
            "value", layer_values)
        return {"LAYERNAME": layer_name, "LAYERVALUES": layer_values}

    @staticmethod
    # returns a list where the position of a value is the old index, and the value itself the new index
    def identify_verts(mesh, layer_name, old_layer_values):
        """Find out which old vertex is which new vertex in your mesh. You need the dictionary from the tag() method for this

        Parameters
        ----------
        mesh : bpy.types.Mesh
            Mesh which vertices you have tagged before
        layer_name : str
            The name of the data layer that has been created previously
        old_layer_values : list
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

        new_layer_values = [0] * len(mesh.vertices)
        mesh.vertex_layers_int[layer_name].data.foreach_get(
            "value", new_layer_values)
        # newLayerValues[newIndex] = assignedValueInLayer

        # value of -1 is basically our own default and means that the old vertex couldn't be found in the mesh anymore
        old_vs_new = [-1] * len(old_layer_values)

        for new_index in range(len(new_layer_values)):
            old_index = new_layer_values[new_index] - 1
            # remember that value == oldIndex+1
            old_vs_new[old_index] = new_index

        return old_vs_new

    @staticmethod
    # removes a datalayer
    def remove_layer(mesh, layer_name):
        """Removes a data layer that has been created by the tag() method. Not actually neccessary, but probably advisable.

        Parameters
        ----------
        mesh : bpy.types.Mesh
        layer_name : str
        """
        # either I'm blind or you actually cannot remove a vertex layer in an easy way
        # bmesh allows it though, so we will have to use that
        bm = bmesh.new()
        bm.from_mesh(mesh)
        #layer = bm.verts.layer.int[layerName]
        bm.verts.layers.int.remove(bm.verts.layers.int[layer_name])
        bm.to_mesh(mesh)
        bm.free()

    # def update(self):
    #
    #    # ??????
    #    None
