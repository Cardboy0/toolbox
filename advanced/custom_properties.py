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
import rna_prop_ui

# Deals with custom properties. Custom properties are special (but also kind of unstable and weird) properties of something Blender-related.
# Because of their weird behaviour, I created a helper class that's supposed to decrease the weirdness you will encounter.

# To create one for a simple Object manually, select an object, go to the 'object properties' tab (not 'object data properties'!)
# and you should find the 'Custom Properties' panel right at the bottom.
# Create a new one and check out its properties if you want. If you make sure the object is still selected and access the side menu in the viewport (press N),
# you will also see the new property appear there.

# Using code, custom properties can be accessed by writing some_blender_object["name of custom property"]
# This works for a lot of different types of Blender objects, such as normal Objects, Scenes, Meshes, etc.


# Some links for more information:
#   search https://wiki.blender.org/wiki/Reference/Release_Notes/3.0/Python_API for "_RNA_UI"
#   https://blender.stackexchange.com/a/224284
#   https://blender.stackexchange.com/questions/43785/adding-other-types-of-custom-properties/43786#43786


class CustomPropertyHandler():
    """Has a few subclasses that are supposed to help with dealing with custom properties.
    Note however that the abilities of it are pretty limited.



    Personal note: I hate custom properties. 
    """

    @classmethod
    def just_set_val(clss, blend_obj, prop_name, value, test_for_success=False):
        """Just (try to) add a new custom property with a value of whatever type you want.

        Note that you can assign more than just numbers or strings to custom properties, exotic stuff like Meshes, Lights, Objects etc. work too.
        They'll just be unchangable for the user in the viewport, greyed out.


        Parameters
        ----------
        blend_obj : Some subclass of bpy.types that supports custom properties
            Blender object that's supposed to get the custom property.
        prop_name : str
            New name of the custom property
        value : any
            Can be a number, a string, a Mesh object or a lot more. Even lists of Blender objects are possible.
            Go ham.
        test_for_success : True or False
            If True, the function will check if assigning the value actually worked.
            By default False

        Returns
        -------
        None, True or False
            Returns True or False if test_for_success (success->True) was enabled,
            None otherwise.

        """
        blend_obj[prop_name] = value
        blend_obj.update_tag()
        # without this, the created property might not be usable by other things such as drivers until you somehow refresh it doing something else.
        # For example, the datapath in a driver variable to a custom property would be '["prop_name"]', but without calling update_tag() it cannot read that data.
        # Got it from https://blenderartists.org/t/force-ui-custom-property-refresh-update/621586
        if test_for_success == True:
            return blend_obj[prop_name] == value

    @classmethod
    def just_get_val(clss, blend_obj, prop_name):
        """Get the current value of a custom property.
        Literally just uses: return blend_obj[prop_name]

        Parameters
        ----------
        blend_obj : Some subclass of bpy.types that supports custom properties
            Blender object that has the custom property.
        prop_name : str
            Name of the custom property of the Blender object.

        Returns
        -------
        Current value of the custom property
        """
        return blend_obj[prop_name]

    @classmethod
    def change_description(clss, blend_obj, prop_name, description):
        """Changes the description of a custom property.

        Parameters
        ----------
        blend_obj : Some subclass of bpy.types that supports custom properties
            Blender object that has the custom property.
        prop_name : str
            Name of the custom property of the Blender object.
        description : str
            New description
        """
        prop_manager = blend_obj.id_properties_ui(prop_name)
        prop_manager.update(description=description)

    class _BasicProp():
        """Base class for the other classes. Should not be used by itself.
        """
        __blend_obj: any
        __name: str
        prop_manager: any  # bpy.types.IDPropertyUIManager, but type somehow doesn't actually exist
        type: None

        # Note: while the manager does have an .update() method, it cannot really change the type of a property

        def __init__(self, blend_obj, name, prop_type):
            self.__blend_obj = blend_obj
            self.__name = name
            self.type = prop_type
            # rna_prop_ui.rna_idprop_ui_create(obj, name, default=0.0, description=description)
            # self.__reset_prop_manager()

        # FIXME: Disabled because neither properly implemented nor tested:
        # @classmethod
        # def from_existing(clss, obj, name):
        #     new = clss(obj=obj, name=name, prop_type=None)
        #     new._reset_prop_manager()
        #     new.type = type(new.get_value())
        #     return new

        def _reset_prop_manager(self):
            """Internal method to set the .prop_manager attribute of this instance.
            """
            self.prop_manager = self.__blend_obj.id_properties_ui(self.__name)

        def get_dict(self):
            """
            Returns
            -------
            dict
                Dictionary containing some information about the custom property, such as its description or default value.
                Contents can vary depending on which type of custom property you have.
            """
            # kinda useless, but whatever
            return self.prop_manager.as_dict()

        def get_value(self):
            """Get the curren't value of your custom property.
            """
            val = self.__blend_obj.get(self.__name, "I am empty")  # "I am empty" is the default value that gets returned if no match is found
            if val == "I am empty":
                # why, I don't know
                raise Exception("This property doesn't exist!")
            else:
                return val

        def get_name(self):
            return self.__name

        def get_blend_obj(self):
            return self.__blend_obj

    class SimpleBool(_BasicProp):
        def __init__(self, blend_obj, name, description, default):
            """Creates an int custom property that acts as a bool property.

            Boolean custom properties cannot be done as far as I know, 
            so instead often a integer custom property that can only assume the values 0 (False) or 1 (True) is used.
            Just trust me on this and don't waste your time trying to find a better solution.

            Parameters
            ----------
            blend_obj : Some subclass of bpy.types that supports custom properties
                Blender object that's supposed to get the custom property.
            name : str
                Name you want the custom property to have.
            description : str
                Description you want the custom property to have
            default : True (1 or True) or False (0 or False)
                Default value of the custom property
            """
            if not int(default) in (0, 1):
                raise Exception("Only 0 or 1 are allowed as values (or True or False)")
            super().__init__(blend_obj=blend_obj, name=name, prop_type=bool)
            rna_prop_ui.rna_idprop_ui_create(
                blend_obj, name, default=default, min=0, max=1, description=description)
            self._reset_prop_manager()

    class SimpleFloat(_BasicProp):
        def __init__(self, blend_obj, name, description, default, min, max, soft_min=None, soft_max=None):
            """Creates a float custom property.

            Parameters
            ----------
            blend_obj : Some subclass of bpy.types that supports custom properties
                Blender object that's supposed to get the custom property.
            name : str
                Name you want the custom property to have.
            description : str
                Description you want the custom property to have
            default : float or int
                default value of the custom property
            min : float or int
                the smallest allowed value
            max : float or int
                the largest allowed value
            soft_min : float, int or None
                Caps the range for the custom property slider for the user, but they can still manually input a lower value.
            soft_max : float, int or None
                See soft_min
            """
            super().__init__(blend_obj=blend_obj, name=name, prop_type=float)
            # custom property functions are one of the only functions I know about where it actually matters if you provide an integer (like 1) or a float (1.0)
            default = default + 0.0
            min = min + 0.0
            max = max + 0.0
            if soft_min != None:
                soft_min = soft_min + 0.0
            if soft_max != None:
                soft_max = soft_max + 0.0
            rna_prop_ui.rna_idprop_ui_create(
                blend_obj, name, default=default, min=min, max=max, soft_min=soft_min, soft_max=soft_max, description=description)
            self._reset_prop_manager()

    class SimpleInteger(_BasicProp):
        def __init__(self, blend_obj, name, description, default, min, max, soft_min=None, soft_max=None):
            """Creates an integer custom property.

            Parameters
            ----------
            blend_obj : Some subclass of bpy.types that supports custom properties
                Blender object that's supposed to get the custom property.
            name : str
                Name you want the custom property to have.
            description : str
                Description you want the custom property to have
            default : int
                default value of the custom property
            min : int
                the smallest allowed value
            max : int
                the largest allowed value
            soft_min : int or None
                Caps the range for the custom property slider for the user, but they can still manually input a lower value.
            soft_max : int or None
                See soft_min
            """
            super().__init__(blend_obj=blend_obj, name=name, prop_type=int)
            rna_prop_ui.rna_idprop_ui_create(
                blend_obj, name, default=default, min=min, max=max, soft_min=soft_min, soft_max=soft_max, description=description)
            self._reset_prop_manager()
