import bpy
import mathutils

# for things related to coordinates (and vectors) in Blender


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
    rotTypeQuaternion = 'QUATERNION'
    rotTypeEulerXYZ = "XYZ"
    rotTypeEulerXZY = "XZY"
    rotTypeEulerYXZ = "YXZ"
    rotTypeEulerYZX = "YZX"
    rotTypeEulerZXY = "ZXY"
    rotTypeEulerZYX = "ZYX"
    rotTypeAxisAngle = 'AXIS_ANGLE'

    __allEulers = (
        rotTypeEulerXYZ,
        rotTypeEulerXZY,
        rotTypeEulerYXZ,
        rotTypeEulerYZX,
        rotTypeEulerZXY,
        rotTypeEulerZYX,
    )

    source_RotType = None
    source_isEuler = False
    source_EulerAsTuple = None
    source_AxisAngleIsTupleOrList = False
    source_AxisAngleIsPair = False

    target_RotType = None
    target_isEuler = False

    __listForAxisAngles = [0, 0, 0, 0]

    @classmethod
    def getRotationType(clss, context, rotationVector):
        """Gets the rotation type of a vector, meaning one of the values an objects rotation_mode accepts.
        Notice that the actual contents (the number values) of the rotationVector don't matter.

        Parameters
        ----------
        context : bpy.types.Context
            Probably bpy.context
        rotationVector : The following types can be recognised:
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

        def isNumber(number):
            try:
                int(number)
                return True
            except:
                return False

        vType = type(rotationVector)
        if vType == mathutils.Quaternion:
            return clss.rotTypeQuaternion
        elif vType == mathutils.Euler:
            return rotationVector.order
        elif len(rotationVector) == 4:
            # luckily this covers both the case where it's a tuple/list or a bpy_float array, because the latter also only has a length of 4.
            return clss.rotTypeAxisAngle
        elif len(rotationVector) == 2 and type(rotationVector[0]) == mathutils.Vector and isNumber(rotationVector[1]) == True:
            return clss.rotTypeAxisAngle
        else:
            try:
                stringRepresentation = str(rotationVector)
            except:
                stringRepresentation = "(values cannot be displayed because it's not convertable to string)"
            raise Exception(
                "Couldn't recognise rotation vector of type " + str(vType) + " with values:\n"+stringRepresentation+"\n")

    def setRotationTypeOfSourceVector(self, context, rotationVector):
        """With this you tell this instance what type of rotation vectors you will later feed it.

        Parameters
        ----------
        context : bpy.types.Context
            Probably bpy.context
        rotationVector : see getRotationType() method description
        """
        self.source_RotType = self.getRotationType(
            context=context, rotationVector=rotationVector)
        if self.source_RotType in self.__allEulers:
            self.source_isEuler = True
            self.source_EulerAsTuple = tuple(
                rotationVector.order.lower())  # turns "XYZ" into ['x', 'y', 'z']
        elif self.source_RotType == self.rotTypeAxisAngle and (type(rotationVector) == tuple or type(rotationVector) == list):
            if len(rotationVector) == 4:
                self.source_AxisAngleIsTupleOrList = True
            elif len(rotationVector) == 2:
                self.source_AxisAngleIsPair = True

    def setRotationTypeOfTargetVector(self, context, rotationVector):
        """With this you tell this instance what type of rotation vectors you later expect to gain from it.

        Parameters
        ----------
        context : bpy.types.Context
            Probably bpy.context
        rotationVector : see getRotationType() method description
        """
        self.target_RotType = self.getRotationType(
            context=context, rotationVector=rotationVector)
        if self.target_RotType in self.__allEulers:
            self.target_isEuler = True

    def convertRotationVectorToTarget(self, context, rotationVector):
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
        if self.source_isEuler == True:
            # 1 Euler to Quaternion
            if self.target_RotType == self.rotTypeQuaternion:
                return rotationVector.to_quaternion()
            # 2 Euler to Euler
            elif self.target_isEuler == True:
                # sadly we cannot just reorder the xyz values, there's actual math involved.
                return rotationVector.to_quaternion().to_euler(self.target_RotType)
            # 3 Euler to Axis Angle
            else:
                toBadVector = rotationVector.to_quaternion().to_axis_angle()
                return (toBadVector[1],)+toBadVector[0][:]  # returns (w,x,y,z)

        # 4-6 Quaternion to x:
        elif self.source_RotType == self.rotTypeQuaternion:
            # 4 Quaternion to Quaternion
            if self.target_RotType == self.rotTypeQuaternion:
                return rotationVector.copy()
            # 5 Quaternion to Euler
            elif self.target_isEuler == True:
                return rotationVector.to_euler(self.target_RotType)
            # 6 Quaternion to Axis Angle
            else:
                toBadVector = rotationVector.to_axis_angle()
                return (toBadVector[1],)+toBadVector[0][:]  # returns (w,x,y,z)

        # 7-9 Axis Angle to x:
        else:
            # we first need to fill our __listForAxisAngles list with the correct values
            if self.source_AxisAngleIsTupleOrList == True:
                # fancy code for "replace all values of first list with all values of second list"
                self.__listForAxisAngles[:] = rotationVector[:]
            elif self.source_AxisAngleIsPair == True:
                self.__listForAxisAngles[:] = (
                    rotationVector[1],)+rotationVector[0][:]  # translates to (w,x,y,z)
            else:
                # puts w,x,y,z values into the list using the bpy foreach_get method
                # foreach_get is probably faster than the stuff above, but only works on bpy_arrays and not default tuples or lists
                rotationVector.foreach_get(self.__listForAxisAngles)

            # 7 Axis Angle to Quaternion
            if self.target_RotType == self.rotTypeQuaternion:
                matrix = mathutils.Matrix.Rotation(
                    self.__listForAxisAngles[0], 4, self.__listForAxisAngles[1:])  # angle = w, axis = [x,y,z]
                return matrix.to_quaternion()
            # 8 Axis Angle to Euler
            elif self.target_isEuler == True:
                matrix = mathutils.Matrix.Rotation(
                    self.__listForAxisAngles[0], 4, self.__listForAxisAngles[1:])  # angle = w, axis = [x,y,z]
                return matrix.to_euler(self.target_RotType)
            # 9 Axis Angle to Axis Angle
            else:
                return tuple(self.__listForAxisAngles)
