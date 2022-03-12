import bpy
import mathutils

# for things related to coordinates (and vectors) in Blender


# main reason I created isVectorClose and getVertexCoordinates here even though they're so small
# is as a reminder to use the vector class when dealing with vertices rather than trying to do your own shit with highschool mathematics
# because the former has been coded for performance and thus faster that what you might come up with.


def is_vector_close(context, vector1, vector2, ndigits=6):
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
    length = (vector1 - vector2).length
    return 0 == round(length, ndigits)


def get_vertex_coordinates(context, mesh, vert_indices="ALL"):
    """Returns the coordinate vectors of all specified vertices.

    Parameters
    ----------
    context : bpy.types.Context
        Probably bpy.context
    mesh : bpy.types.Mesh
        The mesh in question
    vert_indices : list or "ALL"
        Specifiy your vertices by index, by default "ALL"

    Returns
    -------
    list
        List where listIndex == vertIndex, and the value at that index == coordinateVector\n
        Vertices that weren't specified get a value of None
    """
    vert_coordinates = [None] * len(mesh.vertices)
    if vert_indices == "ALL":
        vert_indices = list(range(len(mesh.vertices)))
    for vert_index in vert_indices:
        vert_coordinates[vert_index] = mesh.vertices[vert_index].co.copy()
    # If my old notes are correct, doing it like this (iterating trough all vertices and using co.copy()) is approx. 30% faster than using foreach_get() to get the x,y,z values and then creating new Vectors from each of those triplets.
    return vert_coordinates


class RotationHandling():
    """Can (or should) turn any supplied rotation vector into the desired type once an instance has been created and calibrated.

    What this means is (for example):
    If your object is in euler rotation mode and you switch to another mode (such as quaternion) the rotation normally gets lost (or more exactly: isn't used).
    With this class however you can get the same vector converted to the new mode, 
    so that - if you set it as the objects quaternion rotation vector - it will look like it has the same rotation as before in euler mode.
    Note that if you want to switch from one subtype of Euler vector (like xyz) to another (like zxy), you must *first* change the rotation mode of the Blender object and *then* assign the new vector. 

    How to use:
    1. Create a new instance of this class.
    2. Calibrate:
        2.1 Call the setRotationTypeOfSourceVector() method for the object to know what type of rotation vectors you will be feeding it
        2.2 Call the setRotationTypeOfTargetVector() method for the object to know what type the returned rotation vector should have.
    3. Use: You can now call the convertRotationVectorToTarget() method to get the same vector you give it, but in the calibrated desired type.
    Repeat step 3 as often as you want.

    hint: if you know what you're doing you can also manually set the properties of the instance instead of calling these setXYZ() methods.


    Explanation of rotation vectors:
    Rotation vectors are different from the usual vectors, such as location and scale vectors because they have their own classes.
    Objects (and maybe certain other things) in Blender have three different rotation vectors assigned to them, each with their own class.
    What decides about which vector of those three is actually used is the object.rotation_mode
    1. Quaternion 
        location: object.rotation_quaternion 
        type: mathutils.Quaternion
        rotation_mode: 'QUATERNION'
    2. Euler (with subcategories XYZ, YXZ, ZYX, etc.) 
        location: object.rotation_euler
        type: mathutils.Euler
        rotation_mode: One of 'XYZ','XZY','YXZ','YZX','ZXY' or 'ZYX'
    3. Axis Angle  
        location: object.rotation_axis_angle
        type: some weird bpy_float array.
        rotation_mode: 'AXIS_ANGLE'


    Raises
    ------
    Exception
        If an unrecognized rotation vector type is given.
    """

    # these are the allowed values for a bpy.Objects object.rotation_mode
    rot_type_quaternion = 'QUATERNION'
    rot_type_euler_xyz = "XYZ"
    rot_type_euler_xzy = "XZY"
    rot_type_euler_yxz = "YXZ"
    rot_type_euler_yzx = "YZX"
    rot_type_euler_zxy = "ZXY"
    rot_type_euler_zyx = "ZYX"
    rot_type_axis_angle = 'AXIS_ANGLE'

    __all_eulers = (
        rot_type_euler_xyz,
        rot_type_euler_xzy,
        rot_type_euler_yxz,
        rot_type_euler_yzx,
        rot_type_euler_zxy,
        rot_type_euler_zyx,
    )

    source_rot_type = None
    source_is_euler = False
    source_euler_as_tuple = None
    source_axis_angle_is_tuple_or_list = False
    source_axis_angle_is_pair = False

    target_rot_type = None
    target_is_euler = False

    __list_for_axis_angles = [0, 0, 0, 0]

    @classmethod
    def get_rotation_type(clss, context, rotation_vector):
        """Gets the rotation type of a vector, meaning one of the values an objects rotation_mode accepts.
        Notice that the actual contents (the number values) of the rotationVector don't matter.

        Parameters
        ----------
        context : bpy.types.Context
            Probably bpy.context
        rotation_vector : The following types can be recognised:
            - Quaternion:
                - mathutils.Quaternion
            - Euler:
                - mathutils.Euler
            - Axis Angle:
                - the type it has when assigned to an object (bpy_float array or similar)
                - a tuple or list with 4 numbers
                - a tuple or list pair: First element is of type mathutils.Vector, second is a simple float number
                    - This is what you receive if you use the to_axis_angle() method of a Quaternion vector. Funny enough, you cannot even assign that to the rotation_axis_angle property of an object.

        Returns
        -------
        string
            The type of the rotationVector, as it's accepted by an objects .rotation_mode

        Raises
        ------
        Exception
            If an unrecognized rotation vector type is given.
        """

        def is_number(number):
            try:
                int(number)
                return True
            except:
                return False

        v_type = type(rotation_vector)
        if v_type == mathutils.Quaternion:
            return clss.rot_type_quaternion
        elif v_type == mathutils.Euler:
            return rotation_vector.order
        elif len(rotation_vector) == 4:
            # luckily this covers both the case where it's a tuple/list or a bpy_float array, because the latter also only has a length of 4.
            return clss.rot_type_axis_angle
        elif len(rotation_vector) == 2 and type(rotation_vector[0]) == mathutils.Vector and is_number(rotation_vector[1]) == True:
            return clss.rot_type_axis_angle
        else:
            try:
                string_representation = str(rotation_vector)
            except:
                string_representation = "(values cannot be displayed because it's not convertable to string)"
            raise Exception(
                "Couldn't recognise rotation vector of type " + str(v_type) + " with values:\n" + string_representation + "\n")

    def set_rotation_type_of_source_vector(self, context, rotation_vector):
        """With this you tell this instance what type of rotation vectors you will later feed it.

        Parameters
        ----------
        context : bpy.types.Context
            Probably bpy.context
        rotation_vector : see get_rotation_type() method description
        """
        self.source_rot_type = self.get_rotation_type(
            context=context, rotation_vector=rotation_vector)
        if self.source_rot_type in self.__all_eulers:
            self.source_is_euler = True
            self.source_euler_as_tuple = tuple(
                rotation_vector.order.lower())  # turns "XYZ" into ['x', 'y', 'z']
        elif self.source_rot_type == self.rot_type_axis_angle and (type(rotation_vector) == tuple or type(rotation_vector) == list):
            if len(rotation_vector) == 4:
                self.source_axis_angle_is_tuple_or_list = True
            elif len(rotation_vector) == 2:
                self.source_axis_angle_is_pair = True

    def set_rotation_type_of_target_vector(self, context, rotation_vector):
        """With this you tell this instance what type of rotation vectors you later expect to gain from it.

        Parameters
        ----------
        context : bpy.types.Context
            Probably bpy.context
        rotation_vector : see get_rotation_type() method description
        """
        self.target_rot_type = self.get_rotation_type(
            context=context, rotation_vector=rotation_vector)
        if self.target_rot_type in self.__all_eulers:
            self.target_is_euler = True

    def convert_rotation_vector_to_target(self, context, rotation_vector):
        """Converts a rotation vector (being the type you set as the source type earlier) into the equivalent of the target type.

        Important 
        ---------
        The rotationVector has to be the exact same type you provided when setting the source vector - if you for example used a length 4 tuple, you now also need to provide a length 4 tuple.
        The returned rotation vector however will always be just one of the three types described below.

        Parameters
        ----------
        context : bpy.types.Context
            Probably bpy.context
        rotationVector : type depends on what source vector type you set earlier
            Rotation vector you want to see converted to target type.

        Returns
        -------
        The equivalent of the rotationVector converted to the target type.
        These are the only types it can be, depending on the target type you set earlier:
            - quaternion : mathutils.Quaternion
            - euler : mathutils.Euler (with the correct order of XYZ values)
            - axis angle : a tuple containing 4 floats, representing (w,x,y,z)

        Note: The returned vector will never hold a reference to the provided vector and as such is safe to be manipulated.
        """
        # 9 (3*3) different cases
        # dealing with axis angle type was taken from https://blender.stackexchange.com/questions/212700/how-to-convert-rotation-axis-angle-to-euler-or-quaternion-via-python

        # 1-3 Euler to x:
        if self.source_is_euler == True:
            # 1 Euler to Quaternion
            if self.target_rot_type == self.rot_type_quaternion:
                return rotation_vector.to_quaternion()
            # 2 Euler to Euler
            elif self.target_is_euler == True:
                # sadly we cannot just reorder the xyz values, there's actual math involved.
                return rotation_vector.to_quaternion().to_euler(self.target_rot_type)
            # 3 Euler to Axis Angle
            else:
                to_bad_vector = rotation_vector.to_quaternion().to_axis_angle()
                # returns (w,x,y,z)
                return (to_bad_vector[1],) + to_bad_vector[0][:]

        # 4-6 Quaternion to x:
        elif self.source_rot_type == self.rot_type_quaternion:
            # 4 Quaternion to Quaternion
            if self.target_rot_type == self.rot_type_quaternion:
                return rotation_vector.copy()
            # 5 Quaternion to Euler
            elif self.target_is_euler == True:
                return rotation_vector.to_euler(self.target_rot_type)
            # 6 Quaternion to Axis Angle
            else:
                to_bad_vector = rotation_vector.to_axis_angle()
                # returns (w,x,y,z)
                return (to_bad_vector[1],) + to_bad_vector[0][:]

        # 7-9 Axis Angle to x:
        else:
            # we first need to fill our __listForAxisAngles list with the correct values
            if self.source_axis_angle_is_tuple_or_list == True:
                # fancy code for "replace all values of first list with all values of second list"
                self.__list_for_axis_angles[:] = rotation_vector[:]
            elif self.source_axis_angle_is_pair == True:
                self.__list_for_axis_angles[:] = (
                    rotation_vector[1],) + rotation_vector[0][:]  # translates to (w,x,y,z)
            else:
                # puts w,x,y,z values into the list using the bpy foreach_get method
                # foreach_get is probably faster than the stuff above, but only works on bpy_arrays and not default tuples or lists
                rotation_vector.foreach_get(self.__list_for_axis_angles)

            # 7 Axis Angle to Quaternion
            if self.target_rot_type == self.rot_type_quaternion:
                matrix = mathutils.Matrix.Rotation(
                    self.__list_for_axis_angles[0], 4, self.__list_for_axis_angles[1:])  # angle = w, axis = [x,y,z]
                return matrix.to_quaternion()
            # 8 Axis Angle to Euler
            elif self.target_is_euler == True:
                matrix = mathutils.Matrix.Rotation(
                    self.__list_for_axis_angles[0], 4, self.__list_for_axis_angles[1:])  # angle = w, axis = [x,y,z]
                return matrix.to_euler(self.target_rot_type)
            # 9 Axis Angle to Axis Angle
            else:
                return tuple(self.__list_for_axis_angles)
