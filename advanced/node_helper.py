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


# Blender has multiple different parts where a node system is used, for example Shader/Material nodes or Compositing nodes.
# I tried to create classes in this module that help dealing with those nodes.
# However, I only really implemented a class for Geometry nodes. The base class of it *might* still work for other node types as well, but I didn't test it.

class NodeGroupHandlerBasic():
    """Base class for the other Handler classes of this module.

    Using it on its own for the kind of node systems that I haven't implemented a class for yet hasn't been tested, but might still work anyway.
    """
    node_group: any
    nodes: bpy.types.Nodes

    def __init__(self):
        """Base class for the other Handler classes of this module.

        Using it on its own for the kind of node systems that I haven't implemented a class for yet hasn't been tested, but might still work anyway.
        """
        self.node_group = None
        self.nodes = None

    def clear_all_nodes(self):
        """Remove all nodes from the node group"""
        self.nodes.clear()

    def deselect_all_nodes(self):
        """Deselects all nodes of the node group"""
        for node in self.nodes:
            node.select = False
            # I remember that simply changing .select was a bad idea (at least when dealing with objects or vertices), but I don't see an alternative here

    def add_node(self, node_type) -> bpy.types.Node:
        """Adds a new node to the node group.

        Parameters
        ----------
        node_type : str
            Unlike in most other situations, node_type isn't some_node.type, but some_node.bl_idname

        Returns
        -------
        bpy.types.Node
            The created node.
        """
        node = self.nodes.new(type=node_type)
        return node

    def connect_nodes(self, output_socket, input_socket):
        """Connects two sockets between two nodes. 

        For cases where your nodes seemingly don't get connected but no error message appears, check out the warnings section of this description.

        Parameters
        ----------
        output : bpy.types.NodeSocket
            The output socket of a node. You can get them with your_node.outputs["Socket Name"]\\
            or use the get_input_socket_by_identifier method.
        input : bpy.types.NodeSocket
            The input socket of another node. You can get them your_node.inputs["Socket Name"]\\
            or use the get_output_socket_by_identifier method.

        Warning
        -------
        Unlike usual, multiple sockets with the same name can exist, even on default nodes.\\
        A 'Sample Index' Node (geometry node) appears to only have one 'Value' input, but it actually has five different ones - although all with the same name,
        which means typing my_node.inputs["Value"] doesn't work, you would actually need to use indices (like my_node.inputs[3])\\
        The only way to differentiate between them is their .identifier value.\\
        In this 'Sample Index'  case, you would then find the following 5 DIFFERENT identifiers:\\
        'Value_Float', 'Value_Int', 'Value_Vector', 'Value_Color' and 'Value_Bool'
        """
        # https://blender.stackexchange.com/questions/5413/how-to-connect-nodes-to-node-group-inputs-and-outputs-in-python
        self.node_group.links.new(input=input_socket, output=output_socket)

    @classmethod
    def get_input_socket_by_identifier(cls, node, socket_identifier) -> bpy.types.NodeSocket:
        """
        Gets the input socket of a node from its .identifier value instead of name.\\
        Required because some nodes can have multiple sockets with the same name. To differentiate between them,
        you either need to access them by their index in the node.inputs[] collection, or by their .identifier values,
        since they will not be the same.

        Parameters
        ----------
        node : bpy.types.Node
            Node that has the input socket.
        socket_identifier : str
            The .identifier value of the input socket you're searching for.

        Returns
        -------
        bpy.types.NodeSocket
            Input socket object
        """
        return cls.__get_socket_by_identifier(node=node, socket_identifier=socket_identifier, input=True)

    @classmethod
    def get_output_socket_by_identifier(cls, node, socket_identifier) -> bpy.types.NodeSocket:
        """
        Gets the output socket of a node from its .identifier value instead of name.\\
        Required because some nodes can have multiple sockets with the same name. To differentiate between them,
        you either need to access them by their index in the node.outputs[] collection, or by their .identifier values,
        since they will not be the same.

        Parameters
        ----------
        node : bpy.types.Node
            Node that has the output socket.
        socket_identifier : str
            The .identifier value of the output socket you're searching for.

        Returns
        -------
        bpy.types.NodeSocket
            Output socket object
        """
        return cls.__get_socket_by_identifier(node=node, socket_identifier=socket_identifier, input=False)

    @classmethod
    def __get_socket_by_identifier(cls, node, socket_identifier, input=True):
        if input == True:
            sockets = node.inputs
        else:
            sockets = node.outputs
        for socket in sockets:
            if socket.identifier == socket_identifier:
                return socket
        raise Exception("No socket with that identifier was found")


class GeometryNodesModifierHandler(NodeGroupHandlerBasic):
    node_group: bpy.types.GeometryNodeTree

    main_input_node: bpy.types.NodeGroupInput
    main_output_node: bpy.types.NodeGroupOutput

    def __init__(self, source, reset=False):
        """Creates a helper object for dealing with Geometry Node modifiers, or rather their node groups.

        Parameters
        ----------
        source : None, bpy.types.NodesModifier (geometry node modifier), bpy.types.GeometryNodeTree (node group) or str (name of node group)
            Source for already existing node data. Depending on the provided argument, these different things will happen:
            - None -> a new node group will be created
            - Geometry node modifier -> active node group of the modifier will be used
            - Node Group      -> node group will be used
            - Node Group name -> node group will be used

        reset : bool
            If True, all already existing nodes will be removed, and only a GroupInput and GroupOutput node will remain (not connected).
        """
        super().__init__()
        if source == None:
            node_group = bpy.data.node_groups.new(name='Geometry Nodes', type='GeometryNodeTree')
            node_group.nodes.new(type='NodeGroupInput')
            node_group.nodes.new(type='NodeGroupOutput')
        elif type(source) == bpy.types.NodesModifier:
            node_group = source.node_group  # this is the ACTIVE nodegroup of that modifier!
        elif type(source) == bpy.types.GeometryNodeTree:
            node_group = source
        elif type(source) == str:
            node_group = bpy.data.node_groups.get(source, "none found")
            if node_group == "none found":
                raise Exception("Couldn't find a node group with that name in bpy.data.node_groups")
        else:
            raise Exception("Couldnt get a node group from the provided source :(")
        self.nodes = node_group.nodes
        self.node_group = node_group
        if reset == True:
            self.clear_all_nodes()
            self.add_node('NodeGroupInput')
            self.add_node('NodeGroupOutput')
        self.reset_main_nodes()

    def clear_all_nodes(self):
        super().clear_all_nodes()
        self.reset_main_nodes()

    def reset_main_nodes(self):
        """Can be used to refresh main_input_node and main_output_node attributes of this instance if something changed.
        If multiple Group Input or Group Output nodes exist only one of them will be assigned. In that case it's better to manually change the attributes of this instance.
        """
        self.main_input_node = None
        self.main_output_node = None
        hits = 0
        for node in self.nodes:
            if hits == 2:
                break
            if type(node) == bpy.types.NodeGroupInput and self.main_input_node == None:
                self.main_input_node = node
                hits += 1
            if type(node) == bpy.types.NodeGroupOutput and self.main_output_node == None:
                self.main_output_node = node
                hits += 1

    def link_ng_to_modifier(self, modifier):
        """Makes a modifier use the node group of this instance.

        Parameters
        ----------
        modifier : bpy.types.NodesModifier (Geometry Node modifier)
            Geometry Node modifier that's supposed to use the node group of this instance.
        """
        modifier.node_group = self.node_group

    def add_input(self, bl_socket_idname, name):
        """Adds a group input socket. These are special because they appear in the panel of your Geometry Nodes modifiers that use this node group and allows you to choose
        other stuff from your object to use in your node group besides the default Geometry, such as values of a specific vertex group.

        Parameters
        ----------
        bl_socket_idname : str
            Specifies the type of input. To get the type of an already existing socket you need to use your_socket.bl_socket_idname, NOT your_socket.type
        name : str
            Name you want the socket to have.

        Returns
        -------
        bpy.types.NodeSocketInterface
            Created socket interface. This is a different type than normal sockets.
        """
        # ng.inputs['MyAttr'].bl_socket_idname
        # https://blender.stackexchange.com/questions/252791/set-group-input-to-attribute-in-geometry-nodes-python-without-ops
        # https://blender.stackexchange.com/questions/253292/cannot-set-geometrynode-attribute-value-on-creation-in-python?noredirect=1&lq=1
        new_socket = self.__add_socket(blend_collection=self.node_group.inputs, bl_socket_idname=bl_socket_idname, name=name)
        return new_socket

    def add_output(self, bl_socket_idname, name):
        """Adds a group output socket. These are special because they appear in the panel of your Geometry Nodes modifiers that use this node group and allows you to choose
        the destination of additional data from your node group besides the default Geometry.

        Parameters
        ----------
        bl_socket_idname : str
            Specifies the type of output. To get the type of an already existing socket you need to use your_socket.bl_socket_idname, NOT your_socket.type
        name : str
            Name you want the socket to have.

        Returns
        -------
        bpy.types.NodeSocketInterface
            Created socket interface. This is a different type than normal sockets.
        """
        # because only one main socket exists, but different group input nodes can have that socket
        new_socket = self.__add_socket(blend_collection=self.node_group.outputs, bl_socket_idname=bl_socket_idname, name=name)
        return new_socket

    def __add_socket(self, blend_collection, bl_socket_idname, name):
        # helper method
        new_socket = blend_collection.new(type=bl_socket_idname, name=name)
        if new_socket == None:
            raise Exception("'" + bl_socket_idname + "' is not a valid socket type. Remember that your_node_socket.bl_socket_idname needs to be used as the type.")
            # if a bad type was used you simply get a None value instead of an exception.
        return new_socket


# @classmethod
# def set_input_value(self, geo_modifier, attr_name, val):
#     # Setting the actual value is complicated for the following reasons:
#     # 1. Location: the basic value is different for each geometry node modifier that uses the node group
#     # and is accessed like a custom property mit geomod[InputSocket.identifier]
#     # 2. If your input is Type Object or Material or similar, that value above can be simply changed by setting geomod[InputSocket.identifer] = new_obj
#     #   But if your input is of type Float, Integer or similar, different things are the case:
#     #       - geomod[InputSocket.identifer] now is the number value set in the modifier
#     #       - switching the input from a number to something like a vertex group requires you to change geomod[InputSocket.identifier+"_use_attribute"] from 0 to 1
#     #       - There are different kind of things you can use as input, such as vertex groups, UV maps, Vertex Colors, etc
#     #           But the only thing you can set here is a single string, the name of such a property, not the type.
#     #           This means if you have a vertex group called "banana" and a vertex color group called "banana", Blender will choose itself which one to use when you provide the "banana" string.
#     #           You can change the string with geomod[InputSocket.identifer+"_attribute_name"] = name of your thing
#     ng = geo_modifier.node_group
#     input = ng.inputs[attr_name]
#     if type(val)==int or type(val)==float:
#         geo_modifier[input.identifier+"_use_attribute"] = 0 #this value switches between being able to give the input a simple number, or something more complex like vertex groups.
#         # Is the same as clicking on the "Swedish Flag" button to the left of an input
#     else:
#         geo_modifier[input.identifier+"_use_attribute"] = 1
