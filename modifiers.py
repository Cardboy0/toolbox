import bpy


def getModifierPositionInStack(context, modifier):
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


def moveModiferToPositionInStack(context, modifier, position):
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
