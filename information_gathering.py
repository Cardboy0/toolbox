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
import inspect

# Provides functions to get more information about things in Blender.
# Can be used for either personal investigations (i.e. "what the f*ck is this object, TELL ME") 
# or getting required information - such as the "string type" of an object - at runtime


def get_base_type(something):
    """Tries to give you the most basic type (but not bpy.types.ID or bpy.types.Struct) of an object, mesh, or similar.

    Parameters
    ----------
    something : any (or most of any) type Blender object you can come up with
        Examples, provided vs what you get:
        D.meshes[0] -> bpy.types.Mesh
        bpy.types.Object -> bpy.types.Object
        bpy.types.PointLight -> bpy.types.Light (Point lights are a subtype of lights, but you get the base class)

    Returns
    -------
    Some bpy.types. class
        The base class that isn't bpy.types.ID or bpy.types.Struct

    Raises
    ------
    Exception
        If the function failed to find a base type
    """
    # Okay, some information about the class system in Blender: it's a bit messed up.
    # First off, if you want the class of a a certain Blender object, you use the type() function. (For example: type(D.meshes[0]) )
    # In almost all cases, you will get a class of that starts with "bpy.types."
    # Meshes for instance are of type bpy.types.Mesh, normal viewport objects are bpy.types.Object, vertex groups are bpy.types.VertexGroup, etc.
    #
    # Using the .mro() method (like bpy.types.Mesh.mro()) will give you a list of parent classes of that class.
    # In most cases you will see both or one of bpy.types.Struct and bpy.types.ID in that list, because those are parent classes of many different object types in Blender.
    #
    # This sounds kinda complicated but understandable so far, but now to some of the messed up stuff:
    # - Although most of the classes start with bpy.types., they aren't necessarily of the same module.
    #       For example:
    #           - bpy.types.Object.__module__ will give you 'bpy_types' (underscore)
    #           - bpy.types.Particle.__module__ will result in 'bpy.types' (dot)
    #       Further inspection will show you that the code for bpy.types.Object is stored in a .py file called bpy_types.py that exists somewhere on your PC.
    #       But bpy.types.Particle will be in no such file, because its module is actually a "built-in" module.
    # - types of the classes themselves:
    #       - type(bpy.types.Object), type(bpy.types.Light), type(bpy.types.Mesh) will all give you <class 'bpy_struct_meta_idprop'>
    #       - type(bpy.types.Particle) will give you <class 'type'>, which is literally the class of the type() function itself. What the f*ck.
    #               type(bpy.types.Particle) == type(type) is True!
    #       - type(bpy.types.NodeGroup) will give you <class 'bpy_types.RNAMetaPropGroup'>
    # - parent classes struct and ID can have different variations.
    #       As said before, you get a list of base/parent classes of a class with the_class.mro()
    #       - There exists a class bpy.types.Struct
    #       - One of the shown base classes for bpy.types.Object is <class 'bpy_struct'>
    #       But those two struct classes aren't the same, they're (again) from different modules.
    # - There is probably more weird stuff, but that's the stuff I found out so far...

    # 1. Make sure we're dealing with a class and not an object, (example: D.meshes[0] is an object, bpy.types.Mesh is its class)
    if inspect.isclass(something) == False:
        something_clss = type(something)
    else:
        something_clss = something
    # 2. Go up the base class hierachy until we find bpy.types.ID or bpy.types.Struct
    current_clss = something_clss
    for next_clss in something_clss.mro():
        # bpy.types. classes have an .mro() method that returns a list of parent classes.
        if next_clss == bpy.types.ID or next_clss in {bpy.types.Struct, bpy.types.Object.mro()[2]} or next_clss == object:
            # object is the base class of almost any class
            # bpy.types.Object.mro()[2] is another variant of the Struct class, I just don't know how to call it directly
            # The last ones seem to almost always be bpy.types.ID and bpy.types.Struct (sometimes also only one of them exists), so we want the class before those two.
            return current_clss
        else:
            current_clss = next_clss
    print(something_clss)
    raise Exception("Wasn't able to find the base class")


# not guaranteed to actually give the correct result, i didnt test *everything*
def get_string_type(something, capitalized=True):
    """Sometimes you're asked to set the mode of a property, like 'OBJECT', 'LIGHT' or similar.
    This function tries to give you this from the "something" you provide.

    Parameters
    ----------
    something : object or bpy.types. class
        Something you want to get the 'string type' for.
    capitalized : True or False

    Returns
    -------
    str

    Examples
    -------
    get_string_type(D.lights['Sun']) -> 'LIGHT' \n
    get_string_type(bpy.types.Object) -> 'OBJECT'
    """
    obj_type = get_base_type(something=something)
    if obj_type == bpy.types.MetaBall:  # exceptions to the rule
        string_type = 'Meta'
    elif obj_type == bpy.types.FreestyleLineStyle:
        string_type = 'LineStyle'
    elif obj_type == bpy.types.VectorFont:
        string_type = 'Font'
    elif obj_type == bpy.types.LightProbe:
        string_type = 'Light_Probe'
    else:
        bl_rna = obj_type.bl_rna
        # note: there also exists bl_rna.name, but there are slight differences, like spaces being allowed for the name.
        string_type = bl_rna.identifier
    #
    if capitalized == True:
        return string_type.upper()
    else:
        return string_type
