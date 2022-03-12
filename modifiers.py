import bpy
import warnings


def get_modifier_position_in_stack(context, modifier):
    """The index of a modifier in the stack of the object it belongs to. That's the thing you see in the "modifier properties" tab.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    modifier : any bpy.types.Modifier
        The modifier whose index you want to get

    Returns
    -------
    int
        index of modifier in stack
    """
    obj = modifier.id_data
    pos = 0
    for mod in obj.modifiers:
        if mod == modifier:
            return pos
        pos += 1


def move_modifer_to_position_in_stack(context, modifier, position):
    """Moves a modifier to a certain position in the object modifier stack it belongs to. That's the thing you see in the "modifier properties" tab.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    modifier : any bpy.types.Modifier
        The modifier you want to move to another position
    position : int
        Index of desired position. Negative values are allowed, with -1 == last position, as usual with lists.
    """
    obj = modifier.id_data
    if position < 0:  # negative position of for example -1 gets intepreted as the last position in the stack
        position += len(obj.modifiers)
    # I don't like using bpy.ops here, but don't know of a better alternative right now
    override = {"scene": context.scene, "object": obj, "active_object": obj}
    bpy.ops.object.modifier_move_to_index(
        override, modifier=modifier.name, index=position)


def try_to_bind(context, modifier):
    """A few modifiers require you to press a *bind* button. Doing that from within Python is harder than you think
    because there are like a dozen of things that can go wrong, which is why I created this function to do it instead.

    Trying to use this to unbind modifiers should be possible too, but it might give unexpected results.

    Also note: Try to not access the bind operator yourself before you use this function.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    modifier : bpy.types.Modifier
        The modifier where you want to simulate pressing the bind button.

        Currently only these three modifiers are supported:
        - Surface Deform
        - Mesh Deform
        - Laplacian Deform


    Returns
    -------
    bool
        True if binding was successful, or False on fail (or on unbind).

    Raises
    ------
    Exception
        When a modifier of a different type than the three above is supplied

    Additional Information
    ----------------------
    - You shouldnt access the bind operator yourself because on a fail the modifier behaves the same way as if it succeded: You have to "unbind" the failed state by using the operator once again.
    Only then can you attempt another attempt to bind something. There's, as far as I know, no way to check if a modifier is currently in that "failed" state.
    So this function always assumes that the modifier is NOT in that state because it hasn't been attempted (by you) to bind yet.
    - The binding works even if your main object is in another scene or no scene at all. But be aware that in the latter case, the object will be put in a temporary (empty) scene to make binding possible.
    - The Laplacian Deform modifier behaves weird (as of 3.0). Not even just in Python, but in default Blender itself. As an example:
    Trying to bind an empty vertex group will fail. But if you add a filled vertex group and *then* try to bind the empty vertex group it suddenly works. 
    I once even managed to have an error message that the binding failed while the modifier showed the "unbind" button as a success at the same time. 
    """

    valid_types = {'MESH_DEFORM', 'SURFACE_DEFORM', 'LAPLACIANDEFORM'}
    # I didn't forget the underscore in LAPLACIANDEFORM, there simply is none
    mod_type = modifier.type
    if (mod_type in valid_types) == False:
        raise Exception(
            "This method can only bind modifiers of the following types:\n" + str(valid_types))

    obj = modifier.id_data  # the object the modifier belongs to

    temp_scene = None
    if (len(obj.users_scene) == 0):
        # binding an object that is in no scene doesn't work, so we temporarily add it to a new scene.
        temp_scene = bpy.data.scenes.new("temporary scene for binding")
        temp_scene.collection.objects.link(obj)

    override = {'object': obj,
                'active_object': obj,
                'scene': obj.users_scene[0]
                # any scene the main object is in suffices, any target objects dont matter. At least for surface deform.
                # if you don't include a scene in the override and do the binding while you're in the scene the object isn't part of,
                # the is_bound property of the mod will not refresh and make things more complicated
                }
    # Apart from these three items in the override no context properties seem to be of any importance, including the viewlayer(s)
    # Read this for more information on overriding: https://docs.blender.org/api/current/bpy.ops.html#overriding-context

    if mod_type == 'SURFACE_DEFORM':
        op = bpy.ops.object.surfacedeform_bind
        bound = "is_bound"
    elif mod_type == 'MESH_DEFORM':
        op = bpy.ops.object.meshdeform_bind
        bound = "is_bound"
    elif mod_type == 'LAPLACIANDEFORM':
        op = bpy.ops.object.laplaciandeform_bind
        bound = "is_bind"  # not a spelling mistake

    was_already_bound = getattr(modifier, bound)

    # call the bind operator with the override
    op(override, modifier=modifier.name)

    is_bound = getattr(modifier, bound)

    if is_bound == False and was_already_bound == False:
        op(override, modifier=modifier.name)  # resetting the "failed" state

    if temp_scene != None:
        # created at the beginning and no longer needed, so we remove it again
        bpy.data.scenes.remove(temp_scene)

    return is_bound
