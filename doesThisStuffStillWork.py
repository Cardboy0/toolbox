# tests if the other functions and classes in this repository still work.
# obviously we can't cover every corner case, so take the results with a grain of salt.
# Additionally: this particular script uses bpy.ops. operators often - this is on purpose, because it's for testing. In your own scripts try to NOT use bpy.ops however.

# I apologize for the stroke you will have when trying to understand some of the logic I did here due to lacking documentation at points.

import bpy
import math
import mathutils
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
print("\n\n"*3+"*"*200+"\nStart of new test run\n\n")


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
    selectObjects.selectObjects(C, [cube], True, cube)
    if cube in C.selected_objects and len(C.selected_objects) == 1 and C.object == cube and C.active_object == cube:
        return True
    else:
        print(cube in C.selected_objects)
        print(len(C.selected_objects) == 1)
        print(C.object == cube)
        print(C.active_object == cube)
        return False


# deleteStuff.py
def test_deleteObjectAndMesh():
    try:
        # import deleteStuff
        deleteStuff = bpy.data.texts["deleteStuff.py"].as_module(
        )
    except:
        print("COULDN'T IMPORT deleteStuff")
        return False
    messStuffUp()
    bpy.ops.mesh.primitive_ico_sphere_add()
    C.object.name = "kl152592"  # random number to identify
    C.object.data.name = "kl152592"
    obj = D.objects["kl152592"]
    mesh = D.meshes["kl152592"]
    objs = len(D.objects)
    meshes = len(D.meshes)
    deleteStuff.deleteObjectAndMesh(C, C.object)
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
    coll_1 = Collections.createCollection(C, "coll_1", origScene.collection)
    coll_2 = Collections.createCollection(C, "coll_2", origScene.collection)
    # should only exist in current (wrong) scene
    coll_xxxx = Collections.createCollection(C, "coll_xxxx", "MASTER")
    coll_3 = Collections.createCollection(C, "coll_3", "MASTER")
    Collections.linkCollectionToCollections(C, coll_3, origScene.collection)
    coll_4 = Collections.createCollection(C, "coll_4", origScene.collection)
    coll_2_1 = Collections.createCollection(C, "coll_2_1", coll_4)
    coll_2_2 = Collections.createCollection(C, "coll_2_2", coll_2)
    Collections.linkCollectionToCollections(C, coll_2_1, [coll_4, coll_2])
    Collections.linkObjectToCollections(C, obj1, [coll_1, coll_4])
    Collections.linkObjectToCollections(C, obj1, [coll_2_2, coll_3])

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
        print("COULDN'T IMPORT tagVertices")
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

    resultDict = tagVertices.TagVertices.tag(C, mesh, "test", vertsToTag)

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

    tagResultList = tagVertices.TagVertices.identifyVerts(C,
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
    tagVertices.TagVertices.removeLayer(C, mesh, resultDict["LAYERNAME"])
    messStuffUp()
    if len(mesh.vertex_layers_int) != 0:
        print("data layer removal didn't work")
        return False

    return True


# createRealMesh.py
def test_createRealMesh():
    try:
        #import createRealMesh
        createRealMesh = bpy.data.texts["createRealMesh.py"].as_module()
    except:
        print("COULDN'T IMPORT createRealMesh")
        return False
    messStuffUp()
    print("attention, createRealMesh doesn't have any testing implemented yet.")
    return True

# deleteStuff.py


def test_delete_VertsFacesEdges():
    try:
        #import deleteStuff
        deleteStuff = bpy.data.texts["deleteStuff.py"].as_module()
    except:
        print("COULDN'T IMPORT deleteStuff")
        return False

    def newPlane():
        bpy.ops.mesh.primitive_plane_add()
        obj = C.object
        obj.name = "testDeletionPlane_1"
        mesh = obj.data
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide()
        bpy.ops.mesh.subdivide()
        bpy.ops.mesh.subdivide()
        bpy.ops.object.mode_set(mode='OBJECT')
        messStuffUp()
        return mesh

    # test if vectors are approx. the same while allowing some precision offset
    def vectorMatch(v1, v2):
        if math.isclose((v1-v2).length, 0, abs_tol=0.01):
            return True
        else:
            return False

    def findEdgeFromCoordinates(co1, co2, mesh):
        co1 = mathutils.Vector(co1)
        co2 = mathutils.Vector(co2)
        for edge in mesh.edges:
            edgeVert1 = mesh.vertices[edge.vertices[0]]
            edgeVert2 = mesh.vertices[edge.vertices[1]]
            if vectorMatch(edgeVert1.co, co1) or vectorMatch(edgeVert1.co, co2):
                if vectorMatch(edgeVert2.co, co1) or vectorMatch(edgeVert2.co, co2):
                    return edge.index
        return -1  # when no match was found

    def findFaceFromCoordinates(center_co, mesh):
        center_co = mathutils.Vector(center_co)
        for face in mesh.polygons:
            if vectorMatch(center_co, face.center):
                return face.index
        return -1

    def findVertexFromCoordinates(co, mesh):
        co = mathutils.Vector(co)
        for vert in mesh.vertices:
            if vectorMatch(vert.co, co):
                return vert.index
        return -1

    # We do this test with a plane that's been subdivided three times.
    # this plane has 81 verts, 144 edges and 64 faces
    # in the following tests, we check if the assumed amount of verts/edges/faces gets deleted
    # the actual indices we give for deletion are only two each time
    # To make things easier, we create a new plane for each "run"
    # To make things more complicated, we identify/compare edges/verts/faces by their coordinates

    # 2 Edges (identified by their two vert coordinates)
    edges = [((-0.25, 0.25, 0.0), (-0.25, 0.5, 0.0)),  # 92
             ((0.5, -0.5, 0.0), (0.5, -0.25, 0.0))]  # 64
    # 2. Faces (center coordinate)
    faces = [(0.375, -0.125, 0.0), (-0.625, 0.375, 0.0)]  # 4, 11
    # 3. Vertices
    vertices = [(0.5, 0.25, 0.0), (-0.5, -0.25, 0.0)]  # 62, 53
    # 4. Another Face (center coordinate)
    totalVerts = 81
    totalEdges = 144
    totalFaces = 64

    # To be able to do this test stuff in a loop, we create dictionaries for each run
    vertInformationONE = {"type": "VERTEX", "coordinatesToDelete": vertices, "deleteChildElements": False, "expectedResults": {
        "verts": totalVerts-2, "edges": totalEdges-8, "faces": totalFaces-8}}
    edgeInformationONE = {"type": "EDGE", "coordinatesToDelete": edges, "deleteChildElements": False, "expectedResults": {
        "verts": totalVerts-0, "edges": totalEdges-2, "faces": totalFaces-4}}
    edgeInformationTWO = {"type": "EDGE", "coordinatesToDelete": edges, "deleteChildElements": True, "expectedResults": {
        "verts": totalVerts-4, "edges": totalEdges-14, "faces": totalFaces-12}}
    faceInformationONE = {"type": "FACE", "coordinatesToDelete": faces, "deleteChildElements": False, "expectedResults": {
        "verts": totalVerts-0, "edges": totalEdges-0, "faces": totalFaces-2}}
    faceInformationTWO = {"type": "FACE", "coordinatesToDelete": faces, "deleteChildElements": True, "expectedResults": {
        "verts": totalVerts-8, "edges": totalEdges-24, "faces": totalFaces-18}}

    for specificDict in [vertInformationONE, edgeInformationONE, edgeInformationTWO, faceInformationONE, faceInformationTWO]:
        messStuffUp()
        mesh = newPlane()
        # getting the indices of the elements
        indices = []
        for something in specificDict["coordinatesToDelete"]:
            if specificDict["type"] == "VERTEX":
                indices.append(findVertexFromCoordinates(something, mesh))
            elif specificDict["type"] == "EDGE":
                indices.append(findEdgeFromCoordinates(
                    something[0], something[1], mesh))
            elif specificDict["type"] == "FACE":
                indices.append(findFaceFromCoordinates(something, mesh))

        deleteStuff.delete_VertsFacesEdges(
            C, mesh, indices, specificDict["type"], specificDict["deleteChildElements"])
        messStuffUp()

        if len(mesh.vertices) != specificDict["expectedResults"]["verts"] or len(mesh.edges) != specificDict["expectedResults"]["edges"] or len(mesh.polygons) != specificDict["expectedResults"]["faces"]:
            print("\nError: see data below")
            print("parameters:  " + specificDict["type"] + ", " +
                  str(specificDict["deleteChildElements"])+"\n")
            print("expected / actualResult")
            print(
                "verts: "+str(specificDict["expectedResults"]["verts"])+"/"+str(len(mesh.vertices)))
            print(
                "edges: "+str(specificDict["expectedResults"]["edges"])+"/"+str(len(mesh.edges)))
            print(
                "faces: "+str(specificDict["expectedResults"]["faces"])+"/"+str(len(mesh.polygons)))
            print("\nmesh name: "+mesh.name)

            return False

        # check if the elements we wanted to delete really have been deleted
        for something in specificDict["coordinatesToDelete"]:
            if specificDict["type"] == "VERTEX":
                index = findVertexFromCoordinates(something, mesh)
            elif specificDict["type"] == "EDGE":
                index = findEdgeFromCoordinates(
                    something[0], something[1], mesh)
            elif specificDict["type"] == "FACE":
                index = findFaceFromCoordinates(something, mesh)

            if index != -1:  # no element with those coordinates should be found, since we deleted them
                return False

    return True


def test_coordinateStuff():
    try:
        #import coordinatesStuff
        coordinatesStuff = bpy.data.texts["coordinatesStuff.py"].as_module()
    except:
        print("COULDN'T IMPORT coordinatesStuff")
        return False
    messStuffUp()
    bpy.ops.mesh.primitive_plane_add()
    obj = C.object
    mesh = obj.data
    coordinates = coordinatesStuff.getVertexCoordinates(C, mesh, [1, 3])
    if coordinatesStuff.isVectorClose(C, coordinates[1], coordinates[3], 6) == True:
        return False
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.translate(value=(-0.2, 0.5, 10), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.transform.rotate(value=0.6, orient_axis='Z', orient_type='VIEW', orient_matrix=((0.7, 0.8, -0.1), (-0.3, 0.2, 0.9), (0.6, -0.6, 0.3)), orient_matrix_type='VIEW',
                             mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.transform.resize(value=(0.001, 0.001, 0.001), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True,
                             use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    coordinates = coordinatesStuff.getVertexCoordinates(C, mesh, "ALL")
    # after resizing, two vertices of the plane (if not diagonal) should have a distance of 0.002 meters
    if coordinatesStuff.isVectorClose(C, coordinates[1], coordinates[3], 6) == True or coordinatesStuff.isVectorClose(C, coordinates[1], coordinates[3], 2) == False:
        return False
    return True


def test_everythingKeyFrames():
    try:
        #import everythingKeyFrames
        everythingKeyFrames = bpy.data.texts["everythingKeyFrames.py"].as_module(
        )
    except:
        print("COULDN'T IMPORT everythingKeyFrames")
        return False
    messStuffUp()
    frame = 199
    C.scene.frame_set(frame)

    # 1. getOrCreate action
    # 2. create keyframes for new fcurves (x and y location)
    # 3. Check if values for object actually change at specified frames

    bpy.ops.mesh.primitive_cube_add()
    obj = C.object
    origLocations = [obj.location.x, obj.location.y]
    # [0,1] are the indices of x and y in vectors
    for (listOrDict, axis) in zip([[frame-8, 0.5555, frame+8, 1, frame-12, 0], {frame-8: 0.5555, frame+8: 1, frame-12: 0}], [0, 1]):

        action = everythingKeyFrames.getOrCreateAction(C, obj)
        fcurve = action.fcurves.new("location", index=axis)
        everythingKeyFrames.createKeyFramesFast(C, fcurve, listOrDict)
        for (changedFrame, value) in zip([frame-8, frame+8, frame-12], [0.5555, 1, 0]):
            C.scene.frame_set(changedFrame)
            currentLocation = round(obj.location[axis], 5)
            expectedLocation = round(origLocations[axis]+value, 5)
            if currentLocation != expectedLocation:
                print("Wrong locations found:" +
                      str(currentLocation)+" "+str(expectedLocation))
                return False
    return True


x = True
# fun as in function, not the joy I haven't experienced since attending highschool
for fun in (test_selectObjects, test_deleteObjectAndMesh, test_tagVertices, test_createCollection, test_createRealMesh,
            test_delete_VertsFacesEdges, test_coordinateStuff, test_everythingKeyFrames):

    if fun() == True:
        None
    else:
        print("\n\n")
        print("Error in "+fun.__name__+" !")
        x = False

if x == True:
    print("\nEvery test succeeded! (That's good)")
else:
    print("\nAt least one test failed. (That's not good)")
