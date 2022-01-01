from typing import Text
import bpy
import time


D = bpy.data

#########################################################################################
###############                                                  ########################
###############Functions you may want to use for testing purposes########################
###############                                                  ########################
#########################################################################################

# DISCLAIMER:
# These functions are only for "throwaway" testing.
# After using some of these, your Blender Project will likely become clogged up with random objects, scenes, other Stuff.
# Things might just get deleted or changed
# Maybe even some bugs happen that will leave the Project unusable.
# THIS MEANS: DO NOT USE THESE ON ANY PROJECT YOU DON'T PLAN ON THROWING AWAY ANYWAY ( ctrl+z should still work though ).

# Additionally:
# Unlike the other scripts in this repository, some of the functions in this particular file are badly coded, for instance heavily relying on bpy.ops - something the internet will tell you is a bad thing.
# That's because this file is only supposed to be used for simple testing, and a few other reasons


def createSubdivObj(subdivisions=0, type="PLANE"):
    """Creates a primitive mesh object, optionally with subdvisions applied.

    Parameters
    ----------
    subdivisions : int
        Amount of times you want the mesh to be suvdivided.
    type : one of {"PLANE","CUBE","UV_SPHERE","ICO_SPHERE","CYLINDER","CONE","TORUS","MONKEY"}
        The type of primitive Mesh you want to have created

    Returns
    -------
    bpy.types.Object
        Created object
    """
    def raiseErr():
        raise Exception(str(type)+" not a valid value.")
    possibleOps = {
        "PLANE":      bpy.ops.mesh.primitive_plane_add,
        "CUBE":       bpy.ops.mesh.primitive_cube_add,
        "UV_SPHERE":  bpy.ops.mesh.primitive_uv_sphere_add,
        "ICO_SPHERE": bpy.ops.mesh.primitive_ico_sphere_add,
        "CYLINDER":   bpy.ops.mesh.primitive_cylinder_add,
        "CONE":       bpy.ops.mesh.primitive_cone_add,
        "TORUS":      bpy.ops.mesh.primitive_torus_add,
        "MONKEY":     bpy.ops.mesh.primitive_monkey_add,

    }
    possibleOps.get(type, raiseErr)()
    obj = bpy.context.object
    #mesh = obj.data
    bpy.ops.object.mode_set(mode='EDIT')
    for subdivs in range(subdivisions):
        bpy.ops.mesh.subdivide()
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj


def messAround(switchScenes=True):
    """If you generally just want to f*ck up your project to see if your functions still work when settings change.
    Currently includes:
    - Creating a new object (gets deleted again)
    - Switches to Edit Mode at least once (returns to Object Mode at the end)
    - deselecting all objects
    - changing frames
    - (optional) switching to another scene

    Parameters
    ----------
    switchScenes : bool
        If True, your active scene will be switched. If no other scenes exist yet, a new one will be created. Note that to change scenes you can use "C.window.scene = yourScene"
    """
    bpy.ops.mesh.primitive_cube_add()
    newObj = bpy.context.object
    for selectedObjs in bpy.context.selected_objects.copy():
        if selectedObjs != newObj:
            selectedObjs.select_set(False)
    newObj.select_set(True)
    bpy.context.view_layer.objects.active = newObj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.frame_set(bpy.context.scene.frame_current+8)
    bpy.context.scene.frame_set(bpy.context.scene.frame_current-4)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = newObj
    bpy.ops.object.delete(use_global=False)
    # after deleting no object will be selected or active, so no mode can be set and will give us an error
    if switchScenes == True:
        currentScene = bpy.context.scene
        if len(D.scenes) == 1:
            bpy.ops.scene.new(type='NEW')
        for scene in D.scenes:
            if scene != currentScene:
                bpy.context.window.scene = scene
        bpy.ops.mesh.primitive_cube_add()
        bpy.ops.object.delete(use_global=False)


class Timing:

    @staticmethod
    def printTime(timeToPrint, roundDigits=2, Text=""):
        """Prints the supplied value as time in seconds to the console.

        Parameters
        ----------
        timeToPrint : float
            Time in seconds
        roundDigits : int
            The digit you want the print statement to be rounded to.
            Regardless of choice, it will always include the first digit that isn't zero.
        Text : str
            Any text you want to have printed at the first, e.g. "my cake required" -> "my cake required: 300.0 seconds"
        """
        if Text != "":
            Text += ":\t"

        # Get the position of the first digit that isnt 0
        firstDigitNotZero = 0
        timeToTest = timeToPrint
        while int(timeToTest) == 0:
            firstDigitNotZero += 1
            timeToTest = timeToTest*10
        if firstDigitNotZero > roundDigits:
            roundDigits = firstDigitNotZero

        print(Text + str(round(timeToPrint, roundDigits))+" seconds")

    @classmethod
    def measureTimeNeededToRun(cls, function, printTime=True, printDigits=2):
        """Returns the time a function needed to run. Optionally prints the result into the console.

        Parameters
        ----------
        function : function
            The function to test. NOTE THAT NO PARAMETERS CAN BE USED, so you might have to create a "temporary" function.
        printTime : bool
            Whether you want to have the result be printed to the console.
        printDigits : int
            If printTime==True, decides about the amount of digits that will be printed (e.g. 3 digits -> "functionX needed 0.128 seconds").
            Regardless, it will always include the first digit that isn't zero.

        Returns
        -------
        float
            The required time in seconds (not rounded).
        """
        t = -time.time()
        function()
        t += time.time()
        if printTime == True:
            cls.printTime(timeToPrint=t, roundDigits=printDigits,
                          Text=function.__name__)
        return t
