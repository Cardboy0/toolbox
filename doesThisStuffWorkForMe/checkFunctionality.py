# Really ugly script to test if the other functions and classes in this repository still work.
# obviously we can't cover every corner case, so take the results with a grain of salt.
# Additionally: this particular script uses bpy.ops. operators often - this is on purpose, because it's for testing. In your own scripts try to NOT use bpy.ops however.

# I apologize for the stroke you will have when trying to understand some of the logic I did here due to lacking documentation at points.


if __name__ == "__main__":

    import bpy
    import math
    import mathutils
    import warnings
    import os
    import contextlib
    import pathlib
    import sys
    import importlib

    def importStuff():
        # add the directory where the Blender file is located to sys.path so we can import the scripts that are in there
        scriptDirectory = pathlib.Path(bpy.data.filepath).parent.resolve()
        scriptParentDirectory = pathlib.Path(
            bpy.data.filepath).parent.parent.resolve()
        for pathStr in [str(scriptDirectory), str(scriptParentDirectory)]:
            if not pathStr in sys.path:
                sys.path.append(pathStr)

        global testHelpers
        import testHelpers
        importlib.reload(testHelpers)

    importStuff()

    C = bpy.context
    D = bpy.data

    """# https://blender.stackexchange.com/questions/51044/how-to-import-a-blender-python-script-in-another
    # importing other python scripts from inside your main script in Blender can be a hassle, so we use the - in my opinion - easiest method:
    # 1. Open all the scripts (main one and the ones to be imported) in the Blender Text Editor
    # 2. instead of writing "import yourScript", write yourScript = bpy.data.texts["yourScript.py"].as_module()
    # 3. It now works as if it had been imported"""

    C.scene.frame_set(100)
    bpy.ops.mesh.primitive_cube_add()
    cube = C.object
    print("\n\n"*3+"*"*200+"\nStart of new test run\n\n")

    def test_selectObjects():
        try:
            import selectObjects
            importlib.reload(selectObjects)
            # import selectObjects
            # selectObjects = bpy.data.texts["selectObjects.py"].as_module()
        except:
            print("Couldn't import selectObjects!")
            return False
        cube = testHelpers.createSubdivObj(subdivisions=0, type="CUBE")
        # selection depends on the scene
        testHelpers.messAround(switchScenes=False)
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
            import deleteStuff
            importlib.reload(deleteStuff)
            # deleteStuff = bpy.data.texts["deleteStuff.py"].as_module()
        except:
            print("COULDN'T IMPORT deleteStuff")
            return False
        testHelpers.messAround(switchScenes=True)
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
            import Collections
            importlib.reload(Collections)
            # Collections = bpy.data.texts["Collections.py"].as_module()
        except:
            print("COULDN'T IMPORT COLLECTIONS.py")
            return False
        testHelpers.messAround(switchScenes=True)
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
        testHelpers.messAround(switchScenes=True)
        # we aren't even IN the original scene when we do this stuff
        # that's how good this test is
        bpy.ops.mesh.primitive_ico_sphere_add()
        obj1 = C.object
        obj1.name = "obj1"
        coll_1 = Collections.createCollection(
            C, "coll_1", origScene.collection)
        coll_2 = Collections.createCollection(
            C, "coll_2", origScene.collection)
        # should only exist in current (wrong) scene
        coll_xxxx = Collections.createCollection(C, "coll_xxxx", "MASTER")
        coll_3 = Collections.createCollection(C, "coll_3", "MASTER")
        Collections.linkCollectionToCollections(
            C, coll_3, origScene.collection)
        coll_4 = Collections.createCollection(
            C, "coll_4", origScene.collection)
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
            import tagVertices
            importlib.reload(tagVertices)
            # tagVertices = bpy.data.texts["tagVertices.py"].as_module(
            # )
        except:
            print("COULDN'T IMPORT tagVertices")
            return False
        testHelpers.messAround(switchScenes=True)
        obj = testHelpers.createSubdivObj(subdivisions=2, type="PLANE")
        mesh = obj.data
        # preparing is a bool value that tracks if the preparations for the actual methods to test actually all went as planned
        # the plane should now have 25 vertices total
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

        testHelpers.messAround(switchScenes=True)  # very important

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
        testHelpers.messAround(switchScenes=True)
        if len(mesh.vertex_layers_int) != 0:
            print("data layer removal didn't work")
            return False

        return True

    # createRealMesh.py

    def test_createRealMesh():
        try:
            import createRealMesh
            importlib.reload(createRealMesh)
            #createRealMesh = bpy.data.texts["createRealMesh.py"].as_module()
        except:
            print("COULDN'T IMPORT createRealMesh")
            return False
        testHelpers.messAround(switchScenes=True)
        print("attention, createRealMesh doesn't have any testing implemented yet.")
        return True

    # deleteStuff.py

    def test_delete_VertsFacesEdges():
        try:
            import deleteStuff
            importlib.reload(deleteStuff)
            #deleteStuff = bpy.data.texts["deleteStuff.py"].as_module()
        except:
            print("COULDN'T IMPORT deleteStuff")
            return False

        def newPlane():
            obj = testHelpers.createSubdivObj(subdivisions=3, type="PLANE")
            obj.name = "testDeletionPlane_1"
            mesh = obj.data
            testHelpers.messAround(switchScenes=True)
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
            testHelpers.messAround(switchScenes=True)
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
            testHelpers.messAround(switchScenes=True)

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
            import coordinatesStuff
            importlib.reload(coordinatesStuff)
            # coordinatesStuff = bpy.data.texts["coordinatesStuff.py"].as_module(
            # )
        except:
            print("COULDN'T IMPORT coordinatesStuff")
            return False
        testHelpers.messAround(switchScenes=True)
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
            import everythingKeyFrames
            importlib.reload(everythingKeyFrames)
            # everythingKeyFrames = bpy.data.texts["everythingKeyFrames.py"].as_module(
            # )
        except:
            print("COULDN'T IMPORT everythingKeyFrames")
            return False
        testHelpers.messAround(switchScenes=True)
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

    def test_vertexGroups():
        try:
            import vertexGroups
            importlib.reload(vertexGroups)
            # vertexGroups = bpy.data.texts["vertexGroups.py"].as_module()
        except:
            print("COULDN'T IMPORT vertexGroups")
            return False
        testHelpers.messAround(switchScenes=True)
        """
        - Create 3 lists/dictionaries:
            1. list_uniform: Contains a bunch of vertex indices that are supposed to get a uniformal weight in the VG
            2. dict_specific: A dictionary that specified specific vertex indices to get specific weights
            3. list_unchanged: Similar to list_uniform, however these values are supposed to be kept by the VG in question until the end without any changes
            4. list_remove: Some vertex indices to remove
        Invalid indices (negative, duplicates and out of range) included for testing too
        Some of the indices in these lists should overlap
        Additionally, some overlaps in these lists needs to be saved as their own lists 

        - Create new subdivided plane
        - Make sure it's neither selected nor the active object
        - create VG1 and VG2
        - check: activeVG == None
        - create VG3, set it as active
            - only purpose is to make sure that manipulating other VGs does not accidently change this one
            - Assign it vertex weights from list_unchanged
        - VG1:
            1. Set/assign vertices via dict_specific
            2. Set/assign vertices via list_uniform
            # basically values of list_uniform override the ones of dict_specific, and with VG2 it's the other way around
        - VG2:
            - steps for VG1 but in reverse
        - VG1 & VG2:
            - remove verts from list_remove
            - get all vertex indices in VG
            - check: - both VGs have the same amount of assigned vertices
                    - amount of assigned vertices is the one expected when comparing the original lists/dicts
            - get all vertex weights in VG
            - compare with expected lists/dicts
        - check: VG3 still the active VG?
        - check: No changes in VG3's vertices?
        """
        # lists/dictionaries     Our plane is subdivided 3 times, giving it a total of 81 vertices
        list_uniform = [5, -1, 100, 65, 81, 8, 0, 2, 2, 2, 30]
        uniformValue = 0.455
        dict_specific = {0.3: [-1, 100], 0.5: [65, 2], 1: [4, 5, 6, 7, 8]}
        list_unchanged = [10, 11, 12, 45, 46, 47, 30, 5]
        unchaged_uniform_value = 0.111
        # some indices here are in none of the lists above
        list_remove = [-1, 100, 2, 8, 11, 12, ]

        def getOverlaps(list1, list2):
            intersections = set(list1).intersection(list2)
            return list(intersections)

        def removeInvalidIndices(list1):
            return list(vertexGroups.validateVertIndicesForVG(context=C, vertexGroupOrMesh=obj.data, vertIndices=list1, returnType="set"))

        obj = testHelpers.createSubdivObj(subdivisions=3, type="PLANE")
        # just to remove the selection and active status from the plane
        testHelpers.createSubdivObj(subdivisions=0, type="CUBE")
        if C.object == obj or obj.select_get() == True:
            return False  # this shouldnt happen but you never know

        vg1 = vertexGroups.createVertexGroup(context=C, obj=obj, vgName="VG1")
        vg2 = vertexGroups.createVertexGroup(context=C, obj=obj, vgName="VG2")
        if obj.vertex_groups.active != None:
            return False
        vg3 = vertexGroups.createVertexGroup(context=C, obj=obj, vgName="VG3")
        obj.vertex_groups.active = vg3
        vertexGroups.setVertexGroupValuesUniform(
            context=C, vertexGroup=vg3, vertexIndices=list_unchanged, value=unchaged_uniform_value)

        vertexGroups.setVertexGroupValuesSpecific(
            context=C, vertexGroup=vg1, weightsForVerts=dict_specific)
        vertexGroups.setVertexGroupValuesUniform(
            context=C, vertexGroup=vg1, vertexIndices=list_uniform, value=uniformValue)

        vertexGroups.setVertexGroupValuesUniform(
            context=C, vertexGroup=vg2, vertexIndices=list_uniform, value=uniformValue)
        vertexGroups.setVertexGroupValuesSpecific(
            context=C, vertexGroup=vg2, weightsForVerts=dict_specific)

        vertexGroups.removeVertsFromVertexGroup(
            context=C, vertexGroup=vg1, vertIndices=list_remove, validate=True)
        vertexGroups.removeVertsFromVertexGroup(
            context=C, vertexGroup=vg2, vertIndices=list_remove, validate=True)

        vertsVG1 = vertexGroups.getVertsInVertexGroup(
            context=C, vertexGroup=vg1)
        vertsVG2 = vertexGroups.getVertsInVertexGroup(
            context=C, vertexGroup=vg2)

        expectedVerts = list_uniform.copy()
        for weight, indexList in dict_specific.items():
            expectedVerts.extend(indexList)
        expectedVerts = set(expectedVerts)
        expectedVerts.difference_update(set(list_remove))
        expectedVerts = removeInvalidIndices(expectedVerts)
        expectedAmount = len(expectedVerts)

        if len(vertsVG1) != len(vertsVG2) or len(vertsVG1) != expectedAmount or len(vertsVG1) == 0:
            return False

        weightsVG1 = vertexGroups.getVertexWeights(
            context=C, vertexGroup=vg1, vertexIndices=vertsVG1)
        weightsVG2 = vertexGroups.getVertexWeights(
            context=C, vertexGroup=vg2, vertexIndices=vertsVG2)

        # vg1 weights
        for vertIndex in vertsVG1:
            weight = round(weightsVG1[vertIndex], 3)
            if vertIndex in list_remove:
                if weight != None:
                    return False
                else:
                    continue
            elif vertIndex in list_uniform:
                if weight != uniformValue:
                    return False
                else:
                    continue
            else:
                x = False
                for expectedWeight, indexList in dict_specific.items():
                    if vertIndex in indexList and weight == round(expectedWeight, 3):
                        x = True
                        break
                if x == True:
                    continue
                # print(str(vertIndex)+"\t"+str(weight))
                return False

        # vg2 weights
        for vertIndex in vertsVG2:
            weight = round(weightsVG2[vertIndex], 3)
            if vertIndex in list_remove:
                if weight != None:
                    return False
                else:
                    continue
            x = False
            for expectedWeight, indexList in dict_specific.items():
                if vertIndex in indexList:
                    if weight == round(expectedWeight, 3):
                        x = True
                        break
                    else:
                        return False
            if x == True:
                continue
            if vertIndex in list_uniform:
                if weight == round(uniformValue, 3):
                    continue
                else:
                    return False
            return False

        if obj.vertex_groups.active_index != vg3.index or obj.vertex_groups.active != vg3:
            return False

        vg3Verts = vertexGroups.getVertsInVertexGroup(
            context=C, vertexGroup=vg3)
        vg3Weights = vertexGroups.getVertexWeights(
            context=C, vertexGroup=vg3, vertexIndices=vg3Verts)

        if len(vg3Verts) != len(removeInvalidIndices(list_unchanged)):
            return False
        for vertIndex in vg3Verts:
            if round(vg3Weights[vertIndex], 3) != unchaged_uniform_value:
                return False
        return True

    def test_shapekeys():
        try:
            import shapekeys
            importlib.reload(shapekeys)
            # shapekeys = bpy.data.texts["shapekeys.py"].as_module()
        except:
            print("COULDN'T IMPORT shapekeys")
            return False
        testHelpers.messAround(switchScenes=True)
        subdivs = 0
        cube = testHelpers.createSubdivObj(subdivs, type="CUBE")
        """
        Testing createShapekey()
        1. Create basis shapekey as the function requires it
        2. createShapekey() accepts different types of reference
            - For each type, create an individual source (create different deformed copies of base object)
        3. Create a new shapekey for each reference type from their individual object references
        4. Test:
            - does the basis shapekey still display the expected original coordinates?
            - do the coordinates for each shapekey equal the ones of their individual reference object?
        5. mess stuff up and repeat step 4

        """
        C.view_layer.objects.active = cube
        bpy.ops.object.shape_key_add(from_mix=False)
        basisSK = cube.active_shape_key
        origCoordinates = dict()
        for vert in cube.data.vertices:
            origCoordinates[vert.index] = [vert.co.x, vert.co.y, vert.co.z]

        referenceDict = {"list": [1.9],
                         "mesh": [2.6],
                         "dictionary": [3.5]
                         }
        for refKey, smallList in referenceDict.items():
            referenceObj = testHelpers.createSubdivObj(subdivs, type="CUBE")
            smallList.append(referenceObj)
            C.view_layer.objects.active = referenceObj
            tValue = smallList[0]
            bpy.ops.transform.resize(value=(tValue, tValue, tValue), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False,
                                     use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.transform.translate(value=(tValue+1, tValue+1, tValue+1), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                        mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.object.transform_apply(
                location=True, rotation=True, scale=True)
            if refKey == "list":
                coList = []
                for vert in referenceObj.data.vertices:
                    coList.extend([vert.co.x, vert.co.y, vert.co.z])
                smallList.append(coList)
            elif refKey == "mesh":
                smallList.append(referenceObj.data)
            elif refKey == "dictionary":
                coDict = dict()
                for vert in referenceObj.data.vertices:
                    coDict[vert.index] = vert.co.copy()
                smallList.append(coDict)

        for refkey, smallList in referenceDict.items():
            tValue = smallList[0]
            #refObj = smallList[1]
            ref = smallList[2]
            newShapekey = shapekeys.createShapekey(
                context=C, obj=cube, reference=ref)
            smallList.append(newShapekey)

        for x in range(2):  # mess stuff up after the first loop was run
            for refkey, smallList in referenceDict.items():
                tValue = smallList[0]
                refObj = smallList[1]
                ref = smallList[2]
                shKey = smallList[3]
                # test if basis shapekey still holds the same coordinates as in the beginning
                for vert in cube.data.vertices:
                    basisSKvector = basisSK.data[vert.index].co.copy()
                    origVector = origCoordinates[vert.index]
                    for xyz in [0, 1, 2]:
                        if round(origVector[xyz], 3) != round(basisSKvector[xyz], 3):
                            return False

                # test if shapekey has the same coordinates as reference object mesh
                for vert in cube.data.vertices:
                    i = vert.index
                    SKVector = shKey.data[i].co.copy()
                    refMeshVector = refObj.data.vertices[i].co.copy()
                    for xyz in [0, 1, 2]:
                        if round(SKVector[xyz], 3) != round(refMeshVector[xyz], 3):
                            return False
            testHelpers.messAround(switchScenes=True)

        """
        Testing muteAllShapekeys()
        1. mute all shapekeys
            - check if all are muted (including basis shapekey)
        2. untmute all shapekeys
            - check if all are unmuted (including basis shapekey)
        3. mute all shapekeys except Basis and the second one we previously created
            - check for all mute status
        4. unmute all except first shapekey
            - check if all are unmuted except the first
        """
        referenceDictAsList = list(referenceDict.items(
        ))  # items() returns a set and you can't use indices on that
        firstSK = referenceDictAsList[0][1][3]
        secondSK = referenceDictAsList[1][1][3]
        thirdSK = referenceDictAsList[2][1][3]

        # mute all
        shapekeys.muteAllShapekeys(
            context=C, mesh=cube.data, mute=True, exclude=[])
        for sk in cube.data.shape_keys.key_blocks:
            if sk.mute == False:
                return False
        if basisSK.mute == False:  # if for some reason it isn't included in the previous for-loop
            return False
        # unmute all
        shapekeys.muteAllShapekeys(
            context=C, mesh=cube.data, mute=False, exclude=[])
        for sk in cube.data.shape_keys.key_blocks:
            if sk.mute == True:
                return False

        shapekeys.muteAllShapekeys(
            context=C, mesh=cube.data, mute=True, exclude=["BASIS", secondSK])
        if firstSK.mute == False or thirdSK.mute == False or basisSK.mute == True or secondSK.mute == True:
            return False

        shapekeys.muteAllShapekeys(
            context=C, mesh=cube.data, mute=False, exclude=[firstSK])
        if firstSK.mute == False or thirdSK.mute == True or basisSK.mute == True or secondSK.mute == True:
            return False

        return True

    def test_modifiers():
        try:
            import modifiers
            importlib.reload(modifiers)
            # modifiers = bpy.data.texts["modifiers.py"].as_module()
        except:
            print("COULDN'T IMPORT modifiers")
            return False
        testHelpers.messAround(switchScenes=True)
        """
        1. Add a few different modifiers
        2. get all their positions
        3. Check if the modifiers with first and last position are indeed at those positions
        4. Try to put another modifier in last position
        5. Check again
        6. repeat 4 and 5, but this time with a "negative" position
        """
        obj = testHelpers.createSubdivObj(subdivisions=0, type="CUBE")
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        bpy.ops.object.modifier_add(type='MASK')
        bpy.ops.object.modifier_add(type='MESH_SEQUENCE_CACHE')
        bpy.ops.object.modifier_add(type='MESH_SEQUENCE_CACHE')
        bpy.ops.object.modifier_add(type='MESH_SEQUENCE_CACHE')
        bpy.ops.object.modifier_add(type='MESH_SEQUENCE_CACHE')
        origScene = C.scene
        testHelpers.messAround(switchScenes=True)
        positions = dict()  # {position: modifier}
        for mod in obj.modifiers:
            positions[modifiers.getModifierPositionInStack(
                context=C, modifier=mod)] = mod
        firstMod = positions[0]
        lastMod = positions[len(obj.modifiers)-1]
        # need to switch back to original scene if we want to select the obj
        C.window.scene = origScene
        C.view_layer.objects.active = obj
        with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
            # hides any print statements
            # Because the Blender code below will try to print a warning, but we don't want the user to see that
            if bpy.ops.object.modifier_move_up(modifier=firstMod.name) != {'CANCELLED'} or bpy.ops.object.modifier_move_down(modifier=lastMod.name) != {'CANCELLED'}:
                # trying to move a modifier up or down returns {'FINISHED'} if it can move up/down, and {'CANCELLED'} if it can't. (Meaning it already is at first/last position)
                return False
        testHelpers.messAround(switchScenes=True)

        # setting the second modifier to last position in stack
        secondMod = positions[1]
        thirdMod = positions[2]
        modifiers.moveModiferToPositionInStack(
            context=C, modifier=secondMod, position=len(obj.modifiers)-1)
        lastPosPositive = modifiers.getModifierPositionInStack(
            context=C, modifier=secondMod)
        modifiers.moveModiferToPositionInStack(
            context=C, modifier=thirdMod, position=-1)
        lastPosNegative = modifiers.getModifierPositionInStack(
            context=C, modifier=thirdMod)
        if lastPosNegative != lastPosPositive or lastPosNegative != len(obj.modifiers)-1:
            return False
        return True

    x = True
    # fun as in function, not the joy I haven't experienced since attending highschool
    for fun in (test_selectObjects, test_deleteObjectAndMesh, test_tagVertices, test_createCollection, test_createRealMesh,
                test_delete_VertsFacesEdges, test_coordinateStuff, test_everythingKeyFrames, test_vertexGroups, test_shapekeys,
                test_modifiers):

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
