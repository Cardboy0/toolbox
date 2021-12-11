# tests if the other functions and classes in this repository still work.
# obviously we can't cover every corner case, so take the results with a grain of salt.
# Additionally: this particular script uses bpy.ops. operators often - this is on purpose, because it's for testing. In your own scripts try to NOT use bpy.ops however.

# I apologize for the stroke you will have when trying to understand some of the logic I did here due to lacking documentation at points.

import bpy
import math
C = bpy.context
D = bpy.data

# https://blender.stackexchange.com/questions/51044/how-to-import-a-blender-python-script-in-another
# importing other python scripts from inside your main script in Blender can be a hassle, so we use the - in my opinion - easiest method:
# 1. Open all the scripts (main one and the ones to be imported) in the Blender Text Editor
# 2. instead of writing "import yourScript", write yourScript = bpy.data.texts["yourScript.py"].as_module()
# 3. It now works as if it had been imported


C.scene.frame_set(100)
bpy.ops.mesh.primitive_cube_add()
cube = C.object
print("\n\nStart of new test run\n\n")


# changes some stuff, such as switching to different frames, to make sure our results get "updated" properly
def messStuffUp():
    global cube
    try:
        C.view_layer.objects.active = cube
        # if we change scenes this will lead to problems
    except:
        bpy.ops.mesh.primitive_cube_add()
        cube = C.object
        C.view_layer.objects.active = cube
    cube.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')
    C.scene.frame_set(C.scene.frame_current-4)
    C.scene.frame_set(C.scene.frame_current+8)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.mesh.primitive_cube_add()
    bpy.ops.object.delete(use_global=False)
    # after deleting no object will be active, so no mode can be set and will give us an error


# selectObjects.py
def test_selectObjects():
    try:
        # import selectObjects
        selectObjects = bpy.data.texts["selectObjects.py"].as_module()
    except:
        print("Couldn't import selectObjects!")
        return False
    messStuffUp()
    bpy.ops.mesh.primitive_plane_add()
    bpy.ops.mesh.primitive_plane_add()
    bpy.ops.object.select_all(action='SELECT')
    selectObjects.selectObjects([cube], True, cube)
    if cube in C.selected_objects and len(C.selected_objects) == 1 and C.object == cube and C.active_object == cube:
        return True
    else:
        print(cube in C.selected_objects)
        print(len(C.selected_objects) == 1)
        print(C.object == cube)
        print(C.active_object == cube)
        return False


# deleteObjectAndMesh.py
def test_deleteObjectAndMesh():
    try:
        # import deleteObjectAndMesh
        deleteObjectAndMesh = bpy.data.texts["deleteObjectAndMesh.py"].as_module(
        )
    except:
        print("COULDNT IMPORT deleteObjectAndMesh")
        return False
    messStuffUp()
    bpy.ops.mesh.primitive_ico_sphere_add()
    C.object.name = "kl152592"  # random number to identify
    C.object.data.name = "kl152592"
    obj = D.objects["kl152592"]
    mesh = D.meshes["kl152592"]
    objs = len(D.objects)
    meshes = len(D.meshes)
    deleteObjectAndMesh.deleteObjectAndMesh(C.object)
    if objs-1 == len(D.objects) and meshes-1 == len(D.meshes) and D.objects.find("kl152592") == -1 and D.meshes.find("kl152592") == -1:
        return True
    else:
        print(objs-1 == len(D.objects))
        print(meshes-1 == len(D.meshes))
        print(D.objects.find("kl152592") == -1)
        print(D.meshes.find("kl152592") == -1)
        return False


# Collections.py
def test_createCollection():
    # Try to create this:
    # master-collection (of scene)
    # ----coll_1
    # ----coll_2
    # --------coll_2_1
    # --------coll_2_2
    # ------------ obj1
    # ----coll_3
    # --------obj1
    # ----coll_4
    # --------coll_2_1
    # obj1 and coll_2_1 are both present twice because you can link collections and objects to more than one collection
    #
    try:
        #import Collections
        Collections = bpy.data.texts["Collections.py"].as_module(
        )
    except:
        print("COULDN'T IMPORT COLLECTIONS.py")
        return False
    messStuffUp()
    origScene = C.scene
    # delete pre-existing test-results
    deleteCollections = ["coll_1", "coll_2",
                         "coll_2_1", "coll_2_2", "coll_3", "coll_4"]
    for collName in deleteCollections:
        try:
            D.collections.remove(D.collections[collName])
        except:
            None
    try:
        D.objects.remove(D.objects["obj1"])
    except:
        None

    # create two new scenes
    bpy.ops.scene.new(type='NEW')
    bpy.ops.scene.new(type='NEW')
    messStuffUp()
    # we aren't even IN the original scene when we do this stuff
    # that's how good this test is
    bpy.ops.mesh.primitive_ico_sphere_add()
    obj1 = C.object
    obj1.name = "obj1"
    coll_1 = Collections.createCollection("coll_1", origScene.collection)
    coll_2 = Collections.createCollection("coll_2", origScene.collection)
    # should only exist in current (wrong) scene
    coll_xxxx = Collections.createCollection("coll_xxxx", "MASTER")
    coll_3 = Collections.createCollection("coll_3", "MASTER")
    Collections.linkCollectionToCollections(coll_3, origScene.collection)
    coll_4 = Collections.createCollection("coll_4", origScene.collection)
    coll_2_1 = Collections.createCollection("coll_2_1", coll_4)
    coll_2_2 = Collections.createCollection("coll_2_2", coll_2)
    Collections.linkCollectionToCollections(coll_2_1, [coll_4, coll_2])
    Collections.linkObjectToCollections(obj1, [coll_1, coll_4])
    Collections.linkObjectToCollections(obj1, [coll_2_2, coll_3])

    # reset the scene to original
    bpy.context.window.scene = origScene
    print("Attention, Collections.py needs manual supervision:")
    print("(The script also deletes these collections if they should already exist from a previous test run)")
    print("This is the correct result that you should appear in your scene:")
    text = [
        "master-collection (of scene)",
        "----coll_1",
        "----coll_2",
        "--------coll_2_1",
        "--------coll_2_2",
        "------------ obj1",
        "----coll_3",
        "--------obj1",
        "----coll_4",
        "--------coll_2_1"]
    for str in text:
        print(str)
    return True


# tagVertices.py
def test_tagVertices():
    try:
        # import tagVertices
        tagVertices = bpy.data.texts["tagVertices.py"].as_module(
        )
    except:
        print("COULDNT IMPORT tagVertices")
        return False
    messStuffUp()
    bpy.ops.mesh.primitive_plane_add()
    obj = C.object
    mesh = obj.data
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide()
    bpy.ops.mesh.subdivide()
    # preparing is a bool value that tracks if the preparations for the actual methods to test actually all went as planned
    # the plane should now have 25 vertices total
    # allow the actual mesh object to update
    bpy.ops.object.mode_set(mode='OBJECT')
    preparing = len(mesh.vertices) == 25
    vertsToTag = [22, 18, 15, 2, 23, 17, 11]
    dictCoords = {}
    for i in range(len(mesh.vertices)):
        dictCoords[i] = mesh.vertices[i].co.copy()
    # we will later identify vertices by their coordinates as comparison

    resultDict = tagVertices.TagVertices.tag(mesh, "test", vertsToTag)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    vertsToDelete = [7, 16, 23, 11, 19, 22, 21]
    # deleting vertices changes the indices of almost all other vertices. We also delete some tagged vertices.
    for index in vertsToDelete:
        mesh.vertices[index].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='VERT')  # delete the (selected) verts
    bpy.ops.object.mode_set(mode='OBJECT')
    preparing = preparing and len(mesh.vertices) == 18
    # print(len(mesh.vertices))
    # only 18 vertices should exist now

    messStuffUp()  # very important

    comparisonDict = {}  # oldIndex is which newIndex?
    for i in range(25):
        comparisonDict[i] = -1  # Default, Vertex has been deleted
    for newIndex in range(len(mesh.vertices)):

        newCoordinate = mesh.vertices[newIndex].co.copy()
        for oldIndex in range(25):
            oldCoordinate = dictCoords[oldIndex]
            distance = (newCoordinate-oldCoordinate).length

            if math.isclose((newCoordinate-oldCoordinate).length, 0, abs_tol=0.01):
                comparisonDict[oldIndex] = newIndex
                # print(distance)
                # print(comparisonDict[oldIndex])
                break

    # print(comparisonDict)

    tagResultList = tagVertices.TagVertices.identifyVerts(
        mesh, resultDict["LAYERNAME"], resultDict["LAYERVALUES"])

    if preparing == False:
        print("preparing for vertex tagging didnt work as planned")
        return False

    # final test
    # print(tagResultList)
    # print(comparisonDict)

    # for i in vertsToTag:
    #    # old index: new index from method vs. new index from coordinate comparison
    #    print(str(i)+": " +
    #          str(tagResultList[i]) + " vs "+str(comparisonDict[i]))

    for oldIndex in vertsToTag:
        if tagResultList[oldIndex] != comparisonDict[oldIndex]:
            return False

    # everything is fine
    # bonus: test if datalayer is deletable
    tagVertices.TagVertices.removeLayer(mesh, resultDict["LAYERNAME"])
    messStuffUp()
    if len(mesh.vertex_layers_int) != 0:
        print("data layer removal didn't work")
        return False

    return True


# createRealMesh.py
def test_createRealMesh():
    try:
        import createRealMesh
        #createRealMesh = bpy.data.texts["createRealMesh.py"].as_module()
    except:
        print("COULDNT IMPORT createRealMesh")
        return False
    messStuffUp()
    print("attention, createRealMesh doesn't have any testing implemented yet.")
    return True


x = True
# fun as in function, not the joy I haven't experienced since attending highschool
for fun in (test_selectObjects, test_deleteObjectAndMesh, test_tagVertices, test_createCollection, test_createRealMesh):
    print("\n\n")
    if fun() == True:
        None
    else:
        print("Error in "+fun.__name__+" !")
        x = False

if x == True:
    print("\nEvery test succeeded! (That's good)")
