import bpy
C = bpy.context
D = bpy.data


# https://blender.stackexchange.com/questions/27234/python-how-to-completely-remove-an-object


def deleteObjectAndMesh(obj):
    """Deletes the specified object AND its mesh.

    Vital for scripts where you create large amounts of objects and delete them again, as the "default" deleting does not remove meshes, meaning they would pile up your file.

    Parameters
    ----------
    obj : bpy.types.Object
        Object to delete
    """
    mesh = obj.data
    D.objects.remove(obj)
    D.meshes.remove(mesh)
