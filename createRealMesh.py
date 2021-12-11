import bpy

D = bpy.data


def createRealMeshCopy(context, obj, frame="CURRENT", apply_transforms=True):
    """Creates a (static) copy of your chosen mesh where basically every deformation has been applied. This includes modifiers, shapekeys, etc.
    Transformations (size, scale, rotation) can be excluded by setting the apply_transforms parameter to False

    Parameters
    ----------
    context : bpy.types.Context
        Most likely bpy.context
    obj : bpy.types.Object
        The object with your mesh.
    frame : "CURRENT" or int, optional
        The frame where your mesh has the desired shape, by default "CURRENT"
    apply_transforms : bool, optional
        Whether you also want to apply transformations to your mesh (size, scale, rotation), by default True

    Returns
    -------
    bpy.types.Mesh
        The newly created mesh
    """
    # frame stuff
    orig_frame = context.scene.frame_current
    if frame != "CURRENT" and frame != orig_frame:
        context.scene.frame_set(frame)

    dpGraph = context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(dpGraph)
    realMesh = D.meshes.new_from_object(obj_eval)

    # some notes: depsgraph takes modifiers and shapekeys into account, but NOT object transformations
    # (i.e. changes to size, scale and rotation through various, different means)
    # Luckily however, the sum of all transformations are located at YourObject.matrix_world
    # We can then use YourMesh.transform(the_matrix_world) to "apply" all the transformations to the mesh
    # this is only valid for the current frame
    if apply_transforms == True:
        transformation_matrix = obj.matrix_world
        realMesh.transform(transformation_matrix)

    # resetting to original frame if we had changed it at the beginning
    if context.scene.frame_current != orig_frame:
        context.scene.frame_set(orig_frame)

    return realMesh


def createNewObjforMesh(context, name, mesh):
    """Creates a new object for a mesh and links it to the master collection of the current scene.

    Parameters
    ----------
    context : bpy.types.Context
        Most likely bpy.context
    name : str
        Desired name of your new object
    mesh : bpy.types.Mesh
        The mesh you want the object to have

    Returns
    -------
    bpy.types.Object
        The new object
    """
    newObj = D.objects.new(name, mesh)
    context.scene.collection.objects.link(newObj)
    return newObj
