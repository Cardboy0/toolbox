import bpy

D = bpy.data


def createRealMeshCopy(context, obj, frame="CURRENT", apply_transforms=True, keepVertexGroups=False, keepMaterials=False):
    """Creates a (static) copy of your chosen mesh where basically every deformation has been applied. This includes modifiers, shapekeys, etc.
    You can choose to keep certain properties (see function parameters)
    Transformations (size, scale, rotation) can be excluded by setting the apply_transforms parameter to False

    Parameters
    ----------
    context : bpy.types.Context
        Most likely bpy.context
    obj : bpy.types.Object
        The object with your mesh.
    frame : "CURRENT" or int
        The frame where your mesh has the desired shape, by default "CURRENT"
    apply_transforms : bool
        Whether you also want to apply transformations to your mesh (size, scale, rotation), by default True
    keepVertexGroups : bool
        Whether you want the mesh to keep the data of any vertex groups it currentely possesses. If True, vertex groups will reappear automatically when you assign the mesh to an object.
    keepMaterials : bool
        Whether you want to keep any material links the mesh has, by default False

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
    # IMPORTANT: Do not try to make changes to obj_eval in any way. They will (somehow) very likely persist even after this function is finished or you try to create it again.
    # For example deleting vertex groups would delete them from future obj_evals as well (but not the original object) - until you restart Blender.

    realMesh = D.meshes.new_from_object(obj_eval)

    if apply_transforms == True or keepVertexGroups == False or keepMaterials == False:
        # TODO: Check how much more time creating tempObj requires. I did some testing and got weird, unusable results, but it seems like without tempObj it's at least in some cases twice as fast.
        tempObj = D.objects.new("temporary object", realMesh)
        # As written above, we should only use obj_eval for getting information, not changing anything.
        # So we create a temporary object to act as a substitute for certain operations, and delete it afterwards again.

        if apply_transforms == True:
            # some notes: depsgraph takes modifiers and shapekeys into account, but NOT object transformations
            # (i.e. changes to size, scale and rotation through various, different means)
            # Luckily however, the sum of all transformations are located at YourObject.matrix_world
            # We can then use YourMesh.transform(the_matrix_world) to "apply" all the transformations to the mesh
            # this is only valid for the current frame
            transformation_matrix = obj.matrix_world
            realMesh.transform(transformation_matrix)

        if keepVertexGroups == False:
            tempObj.vertex_groups.clear()
            # believe it or not, but by default any vertex groups will stay with the mesh and reappear when you assign it to an object
            # probably because every vertex has a .groups attribute with any vertex group data.

        if keepMaterials == False:
            # similar to Vertex Groups, materials also stay with the mesh by default
            realMesh.materials.clear()

        D.objects.remove(tempObj)

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
