import bpy

D = bpy.data


# deals with all (or most) things keyframes (-> fcurves)

def getOrCreateAction(context, something):
    """Get the action of the provided class instance or create a new one if it doesn't exist yet

    This should work on anything that is able to have the animation_data attribute. 

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    something : anything that can have a animation_data attribute
        The "object" for which you want to get the action

    Returns
    -------
    bpy.types.Action
        found or created action

    Raises
    ------
    Exception
        When something went wrong
    """
    # based on these two posts:
    # https://blender.stackexchange.com/questions/234463/scripting-f-curves
    # https://blender.stackexchange.com/questions/41484/how-do-i-change-actions-in-python

    try:
        if something.animation_data == None:
            something.animation_data_create()
        if hasattr(something.animation_data, 'action') == False or something.animation_data.action == None:
            # create new action
            newAction = D.actions.new("custom created action")
            something.animation_data.action = newAction
            # this feels dirty, but I don't have a better alternative
        return something.animation_data.action
    except:
        raise Exception(
            "Something went wrong when trying to get the action of "+something.__str__())


def createKeyFramesFast(context, fcurve, values, ignoreNegativeFrames=False):
    """If you want to create keyframes for a fcurve in a fast way.

    Attention: Should not be used to add keyframes to an fcurve if any keyframes already exist.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    fcurve : bpy.types.FCurve
        The fcurve for which you want keyframes to be created.
        fcurves are part of actions (bpy.types.Action)
    values : list or dictionary
        If list: [frame1,value1, frame2,value2, ...] \n
        If dict: {frame1: value1, frame2: value2, ...} \n
        Using a list is faster than using a dictionary
    ignoreNegativeFrames : bool
        If True, any frame of the supplied values that is negative will get ignored.
        This might decrease the speed of this function.
    """

    # based on https://blender.stackexchange.com/questions/92287/editing-fcurve-keyframe-points-in-fast-mode

    if type(values) == dict:
        x = []
        for key, value in values.items():
            x.extend([key, value])
        values = x

    if ignoreNegativeFrames == True:
        positiveValues = []
        for i in range(0, len(values), 2):
            frame = values[i]
            value = values[i+1]
            if values[i] >= 0:
                positiveValues.extend([frame, value])
        values = positiveValues

    fcurve.keyframe_points.add(count=len(values)/2)
    fcurve.keyframe_points.foreach_set("co", values)
    fcurve.update()
