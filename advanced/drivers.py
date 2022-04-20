import bpy
import importlib
from .. import (information_gathering)
for modu in [information_gathering]:
    importlib.reload(modu)

# Deals with drivers, or rather is supposed to make dealing with them easier.

# Note: By default, created Drivers can be found at the animation data of the blender object that has the drivers, 
# so for example: "C.object.animation_data.drivers[0].driver"

class DriverHelper():
    fcurve: bpy.types.FCurve
    driver: bpy.types.Driver
    __property_name: str
    __boss: None
    linked_custom_property_variables: list  # contains bpy.types.DriverVariable
    linked_normal_property_variables: list  # contains bpy.types.DriverVariable

    def __init__(self, boss_object, property_name, index=-1): 
        """Helps creating new drivers and dealing with them. 

        Also provides easy (relatively) linking to properties of other Blender objects, including custom properties.


        Important: 
        - This class lacks a lot of features and is only barely tested. 
        - If an old driver for your chosen property already exists, it will be overwritten.
        - The property value your driver is for might only update once your script has finished running. Try to avoid depending on that.

        Parameters
        ----------
        boss_object : any Blender instance that supports drivers, such as an actual Object, a Mesh or something more exotic like D.worlds[0]
            An instance that the property that's supposed to get a driver belongs to.
        property_name : str 
            Name of the property. Do not use indices in the name (like "location[1]"), 
            but instead use the name without the index and then use the function index parameter instead (like property_name="location", index=1)
        index : int, by default -1
            Only required if your property is an array-like object (like a location vector, where x_loc=vector[0], y_loc=vector[1], z_loc=vector[2])\\
            Using the default index (-1) for array-like properties will raise an Exception.

        Examples
        --------
        dhelper_mod_hide = DriverHelper( boss_object=C.object.modifiers['Wave'], property_name="show_viewport" )\\
        dhelper_z_loc = DriverHelper( boss_object=C.object, property_name="location", index=2 )
        """
        self.__boss = boss_object
        self.__property_name = property_name
        created_fcurves = boss_object.driver_add(property_name, index)
        if type(created_fcurves) == list:
            raise Exception("This type of property requires the use of an index.")
            # If you try to create a driver for array-like properties with an index of -1 (like obj.driver_add("location",-1)
            #   a different driver will be created for each of the array contents (in this example, one for the x location, one for y location and one for z location)
            #   and you'll get all of them in a list, but this class is only supposed to work with a single driver
            #   so we raise an Exception.
        self.fcurve = created_fcurves
        # the fcurve seems to always be a new one, even if one already exists?
        self.driver = self.fcurve.driver
        self.driver.expression = ""
        self.linked_custom_property_variables = []
        self.linked_normal_property_variables = []

    def refresh_driver_value(self, context):
        """Drivers change the value of a property. In some cases however, that change only takes place after your script has finished running.\\
        If you want to try to refresh it during runtime, use this. Even then it's not guaranteed to work for all cases though.\\
        As such, better try to avoid depending on it altogether.

        Parameters
        ----------
        context : bpy.types.Context
            Most likely bpy.context
        """
        # I didn't manage to find a better way. Things such as update_tag() don't work. Also, what do you do for example if the driver is on the property of a world?
        # And for objects it has some requirements to work as well.
        scene = context.scene
        scene.frame_set(scene.frame_current)

    def add_variable(self, name) -> bpy.types.DriverVariable:
        """Adds a variable to the driver of this instance

        Parameters
        ----------
        name : str
            Name of the variable

        Returns
        -------
        bpy.types.DriverVariable
            Created variable
        """
        var = self.driver.variables.new()
        var.name = name
        return var

    def get_variables(self) -> dict:
        """Get all variables of the driver as a dictionary.\\
        You can also access them normally with your_driver.variables

        Returns
        -------
        dict
            variable names as keys, their objects as values.
        """
        var_dict = {}
        for var in self.driver.variables:
            var_dict[var.name] = var
        return var_dict

    def add_variable_linked_to_property(self, prop_owner, property_name, is_custom_property=False) -> bpy.types.DriverVariable:
        """
        Adds a variable to the driver that links to the value of a certain property of another object. Object can be a normal Blender Object but also something like a mesh,
        a scene, etc.
        The name for the variable is chosen by this function automatically.


        Parameters
        ----------
        prop_owner : Subclass of bpy.types
            The "owner" object of the property. If you for instance wanted to use the power value of a certain light (located at your_light.energy), 
            the light would be the owner.
        property_name : str
            Name of the property, basically everything that comes after the prop_owner. In the example above (your_light.energy), the property name is "energy".\\
            You can also do stuff like "property.sub_property" or "property[2]"
        is_custom_property : bool
            Set this to True if your property is a custom property.

        Returns
        -------
        bpy.types.DriverVariable
            The created variable

        Examples
        --------
        new_var = add_variable_linked_to_property(prop_owner=C.scene,  property_name="gravity.z") # property_name="gravity[2]" would work too\\
        new_var = add_variable_linked_to_property(prop_owner=C.object, property_name="custom property name", is_custom_property=True)
        """
        if is_custom_property == True:
            var_name = "l_prop_custom"
            data_path = '["' + property_name + '"]'  # the datapath for custom properties like obj["prop name"] is like ["prop name"], and you even need to make sure double quotes are used instead of single ones
            add_to = self.linked_custom_property_variables
        else:
            var_name = "l_prop"
            data_path = property_name
            add_to = self.linked_normal_property_variables
        while self.driver.variables.find(var_name) != -1:
            # variables with the same names can exists, but that's obviously a bad idea.
            # find() returns -1 when no variable with our name was found
            var_name += str(len(self.driver.variables))
        var = self.add_variable(name=var_name)
        add_to += [var]
        target = var.targets[0]
        target.id_type = information_gathering.get_string_type(prop_owner, capitalized=True)
        target.id = prop_owner
        target.data_path = data_path
        return var




