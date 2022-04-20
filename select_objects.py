import bpy


def select_objects(context, object_list, deselect_others=True, active=None):
    """Use this to select multiple objects and set a specific object as active.

    You can also use this to deselect all objects by giving an empty list.
    The object to be set as active doesn't have to be selected.
    Note that this should only be used with visible objects.

    Currently only works with objects in the current scene.

    Parameters
    ----------
    context : bpy.types.Context
        probably bpy.context
    object_list : list
        List of all objects you want to select.
    deselect_others : bool, optional
        Whether you want to clear the selection of all (visible) objects that are not in object_list, by default True
    active : bpy.types.Object or None, optional
        The object you want to be set as "active", i.e. be the main focus of Blender. If == None, the first object in the list will be set active., by default None
    """
    # selecting and active objects seems to be heavily dependant on viewlayers, this might be something to look into.
    # e.g. select_set() accepts a viewlayer parameter
    # https://docs.blender.org/api/2.93/bpy.types.LayerObjects.html?highlight=objects%20active#bpy.types.LayerObjects.active
    if deselect_others == True:
        selected_objs = context.selected_objects.copy()
        # uncomfortable with using the list itself since the elements will disappear with each iteration
        for obj in selected_objs:
            obj.select_set(False)
    for obj in object_list:
        obj.select_set(True)
    # this value accepts None as well
    # Does NOT work from other scenes.
    if active == None:
        context.view_layer.objects.active = object_list[0]
    else:
        context.view_layer.objects.active = active

#only allow for one object at a time because of return value
def duplicate_object(obj, keep_mesh=False):
    """Creates a duplicate of an object. The duplicate will be in the same collections and scenes as the original one.
    
    Stuff that will also be duplicated include, but are not limited to:
        - parent
        - modifiers
        - constraints
        - transformations

    Parameters
    ----------
    obj : bpy.types.Object
        Blender Object you want to create a duplicate for
    keep_mesh : True or False
        If you want the object to use the same "Data" (in most cases that's a mesh) as the original keep this True.
        Otherwise, the object data will be duplicated too, creating a new mesh (or light, camera, whatever) for the object to use.
        
    Returns
    -------
    bpy.types.Object
        The new object
    """
    obj_new = obj.copy()
    if keep_mesh==False and obj.data!=None: #object data is None when it is an empty
        data_new = obj.data.copy()
        obj_new.data = data_new
    else:
        pass #apparently it already has the .data value of the original object by default
    
    for collection in obj.users_collection:
        collection.objects.link(obj_new) #link object to same collections. This automatically makes it appear in the same scenes too.
    
    return obj_new