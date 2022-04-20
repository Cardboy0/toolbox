# Really ugly script to test if the other functions and classes in this repository still work.
# obviously we can't cover every corner case, so take the results with a grain of salt.
# Additionally: this particular script uses bpy.ops. operators often - this is on purpose, because it's for testing. In your own scripts try to NOT use bpy.ops however.

# I apologize for the stroke you will have when trying to understand some of the logic I did here due to lacking documentation at points.

def run(context=None):
    import bpy
    import math
    import mathutils
    import warnings
    import os
    import contextlib
    import pathlib
    import sys
    import importlib
    import traceback

    if context == None:
        C = bpy.context
    else:
        C = context
    D = bpy.data
    o = bpy.ops  # please don't hurt me for this

    def import_stuff():
        # enable relative imports for when this file is opened directly:
        if __name__ == '__main__':  # makes sure this only happens when you run the script from inside Blender

            # INCREASE THIS VALUE IF YOU WANT TO ACCESS MODULES IN PARENT FOLDERS (for using something like "from ... import someModule")
            number_of_parents = 2  # default = 1

            original_path = pathlib.Path(bpy.data.filepath)
            parent_path = original_path.parent

            for i in range(number_of_parents):
                parent_path = parent_path.parent

            # remember, paths only work if they're strings
            str_parent_path = str(parent_path.resolve())
            # print(str_parent_path)
            if not str_parent_path in sys.path:
                sys.path.append(str_parent_path)

            # building the correct __package__ name
            relative_path = original_path.parent.relative_to(parent_path)
            with_dots = '.'.join(relative_path.parts)
            # print(with_dots)
            global __package__
            __package__ = with_dots

        global test_helpers
        from .. import test_helpers
        importlib.reload(test_helpers)

    import_stuff()

    C.scene.frame_set(100)
    bpy.ops.mesh.primitive_cube_add()
    cube = C.object
    print("\n\n" * 3 + "*" * 200 + "\nStart of new test run\n\n")

    ##########################################
    ###############Some Classes###############
    ##########################################

    class AllObjectTypes():

        # Warning: these dictionaries do not contain the object type "Collection Instance"

        locations = {
            "Mesh": D.meshes,
            "Armature": D.armatures,
            "Camera": D.cameras,
            "Curve": D.curves,
            "GreasePencil": D.grease_pencils,
            "Image": D.images,
            "Lattice": D.lattices,
            "Light": D.lights,
            "LightProbe": D.lightprobes,
            "MetaBall": D.metaballs,
            "Speaker": D.speakers,
            "Volume": D.volumes,
            "Empty": None  # an "Empty" object has no data, so there also exists no location
        }

        create_functions = {
            "Mesh": [o.mesh.primitive_cone_add],
            "Armature": [o.object.armature_add],
            "Camera": [o.object.camera_add],
            "Curve": [
                # different subtypes of curve
                o.curve.primitive_bezier_curve_add,
                o.surface.primitive_nurbs_surface_torus_add,
                o.object.text_add,
            ],
            "GreasePencil": [o.object.gpencil_add],
            # lambda because otherwise we can't use own class name within an attribute
            "Image": [lambda: AllObjectTypes.create_image()],
            "Lattice": [lambda: o.object.add(type='LATTICE')],
            "Light": [
                # these have different subtypes of light
                lambda: o.object.light_add(type='POINT'),
                lambda: o.object.light_add(type='SUN'),
                lambda: o.object.light_add(type='SPOT'),
                lambda: o.object.light_add(type='AREA'),
            ],
            "LightProbe": [o.object.lightprobe_add],
            "MetaBall": [o.object.metaball_add],
            "Speaker": [o.object.speaker_add],
            "Volume": [o.object.volume_add],
            "Empty": [
                o.object.empty_add,
                lambda: o.object.effector_add(type='WIND')]
        }

        @classmethod
        def get_all_keys(clss) -> set:
            first_key_set = set(clss.locations.keys())
            second_key_set = set(clss.create_functions.keys())
            if first_key_set != second_key_set:
                raise Exception("We have wrong attributes!")
            return first_key_set

        @classmethod
        def get_all_creation_functions(clss):
            all_functions = list(clss.create_functions.values())
            # that's gonna be a multidimensional list, like so: [ [x,y],  [1,2,3,4], ]
            # convert it to one dimensional:
            # weird, but it seems to work. Got it from here: https://stackoverflow.com/questions/2961983/convert-multi-dimensional-list-to-a-1d-list-in-python
            one_dimensional = sum(all_functions, [])
            # counted them myself to make sure that this one-dimensional stuff is actually working correctly
            if len(one_dimensional) < 19 or len(one_dimensional) > 50:
                raise Exception("Bad value")
            return one_dimensional

        @classmethod
        def create_image(clss):
            # Image creation requires us to first create a new image and then assign that to an empty object
            # We can't use bpy.ops.object.load_reference_image(), because that requires us to choose an image file from our drive
            simple_image = D.images.new(
                name="testImage292318", width=10, height=10)
            # right now has no data (None)
            bpy.ops.object.empty_add(type='IMAGE')
            image_obj = C.object
            image_obj.data = simple_image

    def test_select_objects():
        try:
            from .. import select_objects
            importlib.reload(select_objects)
            # import selectObjects
            # selectObjects = bpy.data.texts["selectObjects.py"].as_module()
        except:
            print("Couldn't import selectObjects!")
            return False
        cube = test_helpers.create_subdiv_obj(subdivisions=0, type="CUBE")
        # selection depends on the scene
        test_helpers.mess_around(switch_scenes=False)
        bpy.ops.mesh.primitive_plane_add()
        plane_one = C.object
        bpy.ops.mesh.primitive_plane_add()
        plane_two = C.object
        bpy.ops.mesh.primitive_plane_add()
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.select_all(action='DESELECT')
        select_objects.select_objects(C, [cube], True, None)
        if C.object != cube:
            print(1)
            return False
        select_objects.select_objects(
            C, [plane_one, plane_two], False, plane_two)

        if C.object != plane_two or C.active_object != plane_two:
            print(C.view_layer.active.name)
            print(C.object.name)
            print(C.active_object.name)
            print(2)
            return False
        if len(C.selected_objects) != 3:
            print(3)
            return False
        for obj in (cube, plane_one, plane_two):
            if not (obj in C.selected_objects):
                print(4)
                return False

        ###############################
        # testing duplication function#
        ###############################
        # Things tested:
        # different types (mesh, camera, empty, etc.)?
        # same location, rotation, scale?
        # same scenes/collections?
        # same constrainst?
        # same mods?
        # same parents?
        # TODO: (maybe) (remember to change function description for what it was tested for)
        # materials
        # vertex groups
        # ?

        def test_transforms(obj_orig, obj_dupl):
            # checks all three transform types for same values
            for type in ("location", "rotation_euler", "scale"):
                for index in (0, 1, 2):
                    val_orig = getattr(obj_orig, type)[index]
                    val_dupl = getattr(obj_dupl, type)[index]
                    difference = round(val_orig - val_dupl, 4)
                    if difference != 0:
                        print("Different values for " + type + " index " +
                              str(index) + " : " + str(val_orig) + " vs " + str(val_dupl))
                        return False
            return True

        def test_users_collection(obj_orig, obj_dupl):
            if set(obj_orig.users_collection) != set(obj_dupl.users_collection):
                return False
            return True

        def test_mods_and_constraints(obj_orig, obj_dupl):
            # speakers,metaballs, cameras and some other objects have a modifiers attribute but adding stuff does nothing, so it's always empty
            if hasattr(obj_orig, "modifiers") == True:
                if len(obj_orig.modifiers) != len(obj_dupl.modifiers):
                    print("Different amount of modifiers")
                    print(len(obj_orig.modifiers))
                    print(type(obj_orig.data))
                    return False
                for mod in obj_orig.modifiers:
                    if obj_dupl.modifiers.find(mod.name) == -1:
                        print("Different modifier names!")
                        return False
            if hasattr(obj_orig, "constraints") == True:
                if len(obj_orig.constraints) != len(obj_dupl.constraints) or len(obj_orig.constraints) == 0:
                    print("Different amount of constraints")
                    print(len(obj_orig.constraints))
                    print(len(obj_dupl.constraints))
                    print(type(obj_orig.data))
                    return False
                for constraint in obj_orig.constraints:
                    if obj_dupl.constraints.find(constraint.name) == -1:
                        print("Different constraint names!")
                        return False
            return True

        loc = [1, 2, 3]
        rot = [4, 5, 6]
        scale = [7, 8, 9]
        orig_scene = bpy.context.scene
        mods = ['WAVE', 'SMOOTH', 'SUBSURF']
        cons = ['COPY_ROTATION', 'STRETCH_TO', 'TRANSFORM']
        general_parent = test_helpers.create_subdiv_obj(
            subdivisions=0, type="PLANE")

        for change_scenes in (False, True):
            for object_type in AllObjectTypes.get_all_keys():
                data_collection = AllObjectTypes.locations[object_type]
                creation_functions = AllObjectTypes.create_functions[object_type]
                for fun in creation_functions:
                    C.window.scene = orig_scene
                    current_objs = list(D.objects)
                    if object_type != "Empty":
                        current_datas = list(data_collection)
                    fun()
                    obj_orig = C.object
                    if obj_orig in current_objs:
                        print("Didn't get the correct object, sorry.")
                        return False
                    obj_orig.location = loc.copy()
                    obj_orig.rotation_euler = rot.copy()
                    obj_orig.scale = scale.copy()
                    obj_orig.parent = general_parent
                    if hasattr(obj_orig, "modifiers") == True:
                        for modname in mods:
                            obj_orig.modifiers.new(name=modname, type=modname)
                    if hasattr(obj_orig, "constraints") == True:
                        for constraintname in cons:
                            obj_orig.constraints.new(constraintname)

                    test_helpers.mess_around(switch_scenes=change_scenes)

                    # with original object data
                    obj_copy = select_objects.duplicate_object(
                        context=C, obj=obj_orig, keep_mesh=True)
                    if obj_copy == obj_orig or obj_copy is obj_orig:
                        return False
                    if test_transforms(obj_orig=obj_orig, obj_dupl=obj_copy) != True:
                        return False
                    if test_mods_and_constraints(obj_orig=obj_orig, obj_dupl=obj_copy) != True:
                        return False
                    if test_users_collection(obj_orig=obj_orig, obj_dupl=obj_copy) != True:
                        return False
                    if obj_orig.parent != obj_copy.parent:
                        return False
                    if object_type != "Empty":
                        if obj_orig.data != obj_copy.data or (obj_orig.data is obj_copy.data) == False:
                            print("Empty problem")
                            return False

                    test_helpers.mess_around(
                        switch_scenes=change_scenes, scenes_to_avoid=[orig_scene])

                    # with duplicate object data
                    obj_copy = select_objects.duplicate_object(
                        context=C, obj=obj_orig, keep_mesh=False)
                    if obj_copy == obj_orig or obj_copy is obj_orig:
                        return False
                    if test_transforms(obj_orig=obj_orig, obj_dupl=obj_copy) != True:
                        return False
                    if test_mods_and_constraints(obj_orig=obj_orig, obj_dupl=obj_copy) != True:
                        return False
                    if test_users_collection(obj_orig=obj_orig, obj_dupl=obj_copy) != True:
                        return False
                    if obj_orig.parent != obj_copy.parent:
                        return False
                    if object_type != "Empty":
                        if obj_orig.data == obj_copy.data or obj_orig.data is obj_copy.data:
                            return False
                        if type(obj_orig.data) != type(obj_copy.data):
                            return False

        return True

    # deleteStuff.py

    def test_delete_object_and_mesh():
        # TODO: use newly created class instead of the dictionaries below
        try:
            from .. import delete_stuff
            importlib.reload(delete_stuff)
            # deleteStuff = bpy.data.texts["deleteStuff.py"].as_module()
        except:
            print("COULDN'T IMPORT deleteStuff")
            return False
        test_helpers.mess_around(switch_scenes=True)

        def create_image():
            # Image creation requires us to first create a new image and then assign that to an empty object
            # We can't use bpy.ops.object.load_reference_image(), because that requires us to choose an image file from our drive
            simple_image = D.images.new(
                name="testImage292318", width=10, height=10)
            # right now has no data (None)
            bpy.ops.object.empty_add(type='IMAGE')
            image_obj = C.object
            image_obj.data = simple_image

        o = bpy.ops
        # the dictionary below contains different examples for objects with specific object.data types
        # the first value is for later to know where the new object.data will be listed in bpy.data, such as bpy.data.meshes
        # the second value is a list of operators that create such objects
        #
        # Some operators are inside "lambda" functions, which is required because those operators need arguments to work
        # https://www.w3schools.com/python/python_lambda.asp for more
        type_dict = {
            "Mesh": (D.meshes,
                     [o.mesh.primitive_cone_add]),
            "Armature": (D.armatures,
                         [o.object.armature_add]),
            "Camera": (D.cameras,
                       [o.object.camera_add]),
            "Curve": (D.curves,
                      [
                          # different subtypes of curve
                          o.curve.primitive_bezier_curve_add,
                          o.surface.primitive_nurbs_surface_torus_add,
                          o.object.text_add,
                      ]),
            "GreasePencil": (D.grease_pencils,
                             [o.object.gpencil_add]),
            "Image": (D.images,
                      [create_image]),
            "Lattice": (D.lattices,
                        [lambda: o.object.add(type='LATTICE')]),
            "Light": (D.lights,
                      [
                          # these have different subtypes of light
                          lambda: o.object.light_add(type='POINT'),
                          lambda: o.object.light_add(type='SUN'),
                          lambda: o.object.light_add(type='SPOT'),
                          lambda: o.object.light_add(type='AREA'),
                      ]),
            "LightProbe": (D.lightprobes,
                           [o.object.lightprobe_add]),
            "MetaBall": (D.metaballs,
                         [o.object.metaball_add]),
            "Speaker": (D.speakers,
                        [o.object.speaker_add]),
            "Volume": (D.volumes,
                       [o.object.volume_add]),

            # we do not test Collection Instances
        }

        # Empties need to be tested slightly different because unlike with all the others types,
        # the object.data isn't saved anywhere, because it's simply None
        empties = [
            # these count as empties because their object.data is None
            o.object.empty_add,
            lambda: o.object.effector_add(type='WIND')
        ]

        orig_objs = set(D.objects)

        # testing the big type dict
        for some_type, property_tuple in type_dict.items():
            collection_to_check = property_tuple[0]
            operators_to_run = property_tuple[1]
            if len(operators_to_run) == 0:
                raise Exception("operator list is empty, aborting test...")
            for op in operators_to_run:
                old_obj = C.object
                op()
                new_obj = C.object
                if old_obj == new_obj:
                    raise Exception(
                        "object creation failed, aborting test...\n" + op.__name__)
                new_data = new_obj.data
                name = new_data.name
                # the .find method returns -1 if no match was found
                if collection_to_check.find(name) == -1:
                    raise Exception(
                        "object creation failed, aborting test...\n" + op.__name__)
                test_helpers.mess_around(switch_scenes=True)
                delete_stuff.delete_object_together_with_data(
                    context=C, obj=new_obj)
                # means data object still exists
                if collection_to_check.find(name) != -1:
                    return False

        # doing the seperate test for empties
        for op in empties:
            old_obj = C.object
            op()
            new_obj = C.object
            if old_obj == new_obj or new_obj.data != None:
                raise Exception(
                    "object creation failed, aborting test...\n" + op.__name__)
            delete_stuff.delete_object_together_with_data(
                context=C, obj=new_obj)
            # there is no result to check here, the only thing that can go wrong is that the object itself isn't deleted or an exception happens

        current_objs = set(D.objects)
        if current_objs != orig_objs:
            return False

        return True

    # information_gathering.py

    def test_information_gathering():
        try:
            from .. import information_gathering
            importlib.reload(information_gathering)
            # deleteStuff = bpy.data.texts["deleteStuff.py"].as_module()
        except:
            print("COULDN'T IMPORT information_gathering")
            return False

        expectedTypes = {
            bpy.types.Object: 'OBJECT',
            bpy.types.Mesh: 'MESH',
            bpy.types.Camera: 'CAMERA',
            bpy.types.Light: 'LIGHT',  # test subtypes and real objects #use .base in function
            bpy.types.Armature: 'ARMATURE',
            bpy.types.Curve: 'CURVE',
            bpy.types.Collection: 'COLLECTION',
            bpy.types.Image: 'IMAGE',
            bpy.types.Material: 'MATERIAL',
            bpy.types.Speaker: 'SPEAKER',
            bpy.types.World: 'WORLD',
            bpy.types.Scene: 'SCENE',
            bpy.types.LightProbe: 'LIGHT_PROBE',
            bpy.types.Material: 'MATERIAL',
            bpy.types.Action: 'ACTION',
            bpy.types.Brush: 'BRUSH',
            bpy.types.CacheFile: 'CACHEFILE',
            bpy.types.VectorFont: 'FONT',
            bpy.types.GreasePencil: 'GREASEPENCIL',
            bpy.types.Key: 'KEY',
            bpy.types.Library: 'LIBRARY',
            bpy.types.FreestyleLineStyle: 'LINESTYLE',
            bpy.types.Lattice: 'LATTICE',
            bpy.types.Mask: 'MASK',
            bpy.types.MetaBall: 'META',
            bpy.types.MovieClip: 'MOVIECLIP',
            bpy.types.NodeTree: 'NODETREE',
            bpy.types.PaintCurve: 'PAINTCURVE',
            bpy.types.Palette: 'PALETTE',
            bpy.types.Particle: 'PARTICLE',
            # bpy.types.Simulation:'SIMULATION', # bpy.types.Simulation doesn't even exist
            bpy.types.Sound: 'SOUND',
            bpy.types.Text: 'TEXT',
            bpy.types.Texture: 'TEXTURE',
            # bpy.types.Hair:'HAIR', # see comment above
            # bpy.types.PointCloud:'POINTCLOUD', # see comment above
            bpy.types.Volume: 'VOLUME',
            bpy.types.WindowManager: 'WINDOWMANAGER',
            bpy.types.WorkSpace: 'WORKSPACE'
        }

        driver = D.objects[0].driver_add("location", 0).driver
        var = driver.variables.new()

        # just testing by types:
        for class_type, expected in expectedTypes.items():
            try:
                var.targets[0].id_type = expected
            except:
                print("'" + expected + "' no longer is a valid value, update " + test_information_gathering.__name__)
                return False
            result = information_gathering.get_string_type(class_type, capitalized=True)
            if result != expected:
                print("Unexpected result: " + expected + " vs " + result)
                return False
        # test not with a type but actual object
        mesh = bpy.data.meshes.new("my mesh")
        if information_gathering.get_string_type(mesh, capitalized=True) != "MESH":
            print("Mesh identification failed")
            return False
        # test with a subtype of a main type
        o.object.light_add(type='POINT')
        point_light = C.object.data
        if type(point_light) != bpy.types.PointLight:
            print("point light creation failed")
            return False
        if information_gathering.get_string_type(point_light, capitalized=True) != "LIGHT":
            print("Point Light identification failed")
            print(information_gathering.get_string_type(point_light, capitalized=True))
            return False

        return True

    # Collections.py

    def test_create_collection():
        # Try to create this:
        # master-collection (of scene)
        # ----coll_apple
        # --------obj2
        # --------coll_blueberry
        # ----coll_banana
        # --------coll_blueberry
        # --------coll_babaco
        # -------------obj1
        # -------------obj2
        # ----coll_cherry
        # --------obj1
        # --------obj2
        # ----coll_dewberry
        # --------obj2
        # --------coll_blueberry
        #
        # obj1, obj2 and coll_blueberry present multiple times because you can link collections and objects to more than one collection
        #
        # For testing, we only look at the parents an object/collection has.
        # From the sketch above, we can assume the following facts for testing:
        # coll_apple has 1 parent: master-collection
        # coll_banana has 1 parent: master-collection
        # coll_cherry has 1 parent: master-collection
        # coll_dewberry has 1 parent: master-collection
        #
        # coll_blueberry has 3 parents: coll_apple, coll_banana, coll_dewberry
        # coll_babaco has 1 parent: coll_banana
        #
        # obj1 has 2 parents: coll_cherry, coll_babaco
        # obj2 has 4 parents: coll_apple, coll_cherry, coll_dewberry, coll_babaco
        #

        try:
            from .. import collectionz
            importlib.reload(collectionz)
            # Collections = bpy.data.texts["Collections.py"].as_module()
        except:
            print("COULDN'T IMPORT COLLECTIONS.py")
            return False
        test_helpers.mess_around(switch_scenes=True)
        orig_scene = C.scene
        # delete pre-existing test-results
        delete_collections = ["coll_apple", "coll_banana",
                              "coll_blueberry", "coll_babaco", "coll_cherry", "coll_dewberry"]
        for coll_name in delete_collections:
            try:
                D.collections.remove(D.collections[coll_name])
            except:
                None
        try:
            D.objects.remove(D.objects["obj1"])
        except:
            None

        # create two new scenes
        bpy.ops.scene.new(type='NEW')
        bpy.ops.scene.new(type='NEW')
        test_helpers.mess_around(switch_scenes=True)
        # we aren't even IN the original scene when we do this stuff
        # that's how good this test is
        bpy.ops.mesh.primitive_ico_sphere_add()
        obj1 = C.object
        obj1.name = "obj1"
        bpy.ops.mesh.primitive_ico_sphere_add()
        obj2 = C.object
        obj2.name = "obj2"

        coll_apple = collectionz.create_collection(
            C, "coll_apple", orig_scene.collection)
        coll_banana = collectionz.create_collection(
            C, "coll_banana", orig_scene.collection)
        # should only exist in current (wrong) scene
        coll_xxxx = collectionz.create_collection(C, "coll_xxxx", "MASTER")
        coll_cherry = collectionz.create_collection(C, "coll_cherry", "MASTER")

        collectionz.link_collection_to_collections(
            C, coll_cherry, orig_scene.collection, keep_links=False)

        coll_dewberry = collectionz.create_collection(
            C, "coll_dewberry", orig_scene.collection)
        coll_blueberry = collectionz.create_collection(
            C, "coll_blueberry", coll_dewberry)
        coll_babaco = collectionz.create_collection(
            C, "coll_babaco", coll_banana)

        collectionz.link_collection_to_collections(
            C, coll_blueberry, [coll_dewberry, coll_banana], keep_links=False)
        collectionz.link_collection_to_collections(
            C, coll_blueberry, coll_apple, keep_links=True)

        collectionz.link_object_to_collections(
            C, obj1, [coll_apple, coll_dewberry], keep_links=False)
        collectionz.link_object_to_collections(
            C, obj2, [coll_apple, coll_dewberry], keep_links=False)
        collectionz.link_object_to_collections(
            C, obj1, [coll_babaco, coll_cherry], keep_links=False)
        collectionz.link_object_to_collections(
            C, obj2, [coll_babaco, coll_cherry], keep_links=True)

        master_coll = orig_scene.collection  # of the current scene

        # reset the scene to original
        # for some reason doesn't work anymore: it will show you that it successfully switched, but after the script has finished you will see it hasn't. But it isn't important, so ignore it.
        C.window.scene = orig_scene

        # testing - this is based on the assumptions in the notes at the beginning
        # note that you can't test "collectionX in collectionY.children". Instead you need to write "collectionX.name in collectionY.children"
        for coll in [coll_apple, coll_banana, coll_cherry, coll_dewberry]:
            if (coll.name in master_coll.children) == False or coll.users != 1:
                return False

        for coll in [coll_apple, coll_banana, coll_dewberry]:
            if (coll_blueberry.name in coll.children) == False or coll_blueberry.users != 3:
                return False

        if (coll_babaco.name in coll_banana.children) == False or coll_babaco.users != 1:
            return False

        if set(obj1.users_collection) != set([coll_cherry, coll_babaco]):
            return False

        if set(obj2.users_collection) != set([coll_apple, coll_cherry, coll_dewberry, coll_babaco]):
            return False

        # print("Attention, Collections.py needs manual supervision:")
        # print("(The script also deletes these collections if they should already exist from a previous test run)")
        # print("This is the correct result that you should appear in scene '" +
        #       origScene.name+"':")
        # text = [
        #     "master-collection (of scene)",
        #     "----coll_1",
        #     "----coll_2",
        #     "--------coll_2_1",
        #     "--------coll_2_2",
        #     "------------ obj1",
        #     "----coll_3",
        #     "--------obj1",
        #     "----coll_4",
        #     "--------coll_2_1"]
        # for str in text:
        #     print(str)
        return True

    # tagVertices.py

    def test_tag_vertices():
        try:
            from .. import tag_vertices
            importlib.reload(tag_vertices)
            # tagVertices = bpy.data.texts["tagVertices.py"].as_module(
            # )
        except:
            print("COULDN'T IMPORT tagVertices")
            return False
        test_helpers.mess_around(switch_scenes=True)
        obj = test_helpers.create_subdiv_obj(subdivisions=2, type="PLANE")
        mesh = obj.data
        # preparing is a bool value that tracks if the preparations for the actual methods to test actually all went as planned
        # the plane should now have 25 vertices total
        preparing = len(mesh.vertices) == 25
        verts_to_tag = [22, 18, 15, 2, 23, 17, 11]
        dict_coords = {}
        for i in range(len(mesh.vertices)):
            dict_coords[i] = mesh.vertices[i].co.copy()
        # we will later identify vertices by their coordinates as comparison

        result_dict = tag_vertices.TagVertices.tag(
            C, mesh, "test", verts_to_tag)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        verts_to_delete = [7, 16, 23, 11, 19, 22, 21]
        # deleting vertices changes the indices of almost all other vertices. We also delete some tagged vertices.
        for index in verts_to_delete:
            mesh.vertices[index].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='VERT')  # delete the (selected) verts
        bpy.ops.object.mode_set(mode='OBJECT')
        preparing = preparing and len(mesh.vertices) == 18
        # print(len(mesh.vertices))
        # only 18 vertices should exist now

        test_helpers.mess_around(switch_scenes=True)  # very important

        comparison_dict = {}  # oldIndex is which newIndex?
        for i in range(25):
            comparison_dict[i] = -1  # Default, Vertex has been deleted
        for new_index in range(len(mesh.vertices)):

            new_coordinate = mesh.vertices[new_index].co.copy()
            for old_index in range(25):
                old_coordinate = dict_coords[old_index]
                distance = (new_coordinate - old_coordinate).length

                if math.isclose((new_coordinate - old_coordinate).length, 0, abs_tol=0.01):
                    comparison_dict[old_index] = new_index
                    # print(distance)
                    # print(comparisonDict[oldIndex])
                    break

        # print(comparisonDict)

        tag_result_list = tag_vertices.TagVertices.identify_verts(C,
                                                                  mesh, result_dict["LAYERNAME"], result_dict["LAYERVALUES"])

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

        for old_index in verts_to_tag:
            if tag_result_list[old_index] != comparison_dict[old_index]:
                return False

        # everything is fine
        # bonus: test if datalayer is deletable
        tag_vertices.TagVertices.remove_layer(
            C, mesh, result_dict["LAYERNAME"])
        test_helpers.mess_around(switch_scenes=True)
        if len(mesh.vertex_layers_int) != 0:
            print("data layer removal didn't work")
            return False

        return True

    # createRealMesh.py

    def test_create_real_mesh():
        try:
            from .. import create_real_mesh
            importlib.reload(create_real_mesh)
            #createRealMesh = bpy.data.texts["createRealMesh.py"].as_module()
        except:
            print("COULDN'T IMPORT createRealMesh")
            return False
        """
        What to test:
            - do materials, textures, shapekeys, vertex groups, - basically everything that isn't a vertex, edge or polygon - get fully removed from the new mesh? Including these:
                - materials
                - textures              - TODO not yet implemented
                - shapekeys
                - vertex groups
                - parents
                - constraints
                - UV layers             - TODO not yet implemented (C.object.data.uv_layers)
                - vertex colors         - TODO not yet implemented (C.object.data.vertex_colors)
                - normals               - TODO not yet implemented
                - transformations     
                - custom properties
                - (ignore particles and hair)
            - Does, no matter the source of animation, the result truly match to what geometry you see in viewport, and at that exact frame?
            - Do vertex indices change?

        How to test:
            - for each different "type" of deformation listed above check
                1. Did the property disappear
                2. Does the result mesh look like the original one with that property?
                    3. By comparing the coordinates per vertex index we already can be sure that vertex indices didn't change

        """
        def is_vector_close(v1, v2):
            length = (v1 - v2).length
            return 0 == round(length, 3)

        def are_same_mesh(mesh1, mesh2):
            if len(mesh1.vertices) != len(mesh2.vertices):
                return False
            for (v1, v2) in zip(mesh1.vertices, mesh2.vertices):
                if is_vector_close(v1.co, v2.co) == False:
                    return False
            return True

        def select_objs(objs=[]):
            # first in list will be set as active
            bpy.ops.object.select_all(action='DESELECT')
            for obj in objs:
                obj.select_set(True)
            C.view_layer.objects.active = objs[0]

        test_helpers.mess_around(switch_scenes=True)

        def check_materials(obj):
            select_objs([obj])
            mat = D.materials.new("test")
            obj.data.materials.append(mat)
            # bpy.ops.material.new() #this doesn't work to create materials, probably some issue with context
            if len(obj.material_slots) != 1 and len(obj.data.materials) != 1:
                print(list(obj.material_slots))
                print(list(obj.data.materials))
                return False
            new_mesh_without_mat = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, frame="CURRENT", apply_transforms=True, keep_vertex_groups=False, keep_materials=False)
            new_obj_without_mat = create_real_mesh.create_new_obj_for_mesh(
                context=C, name="newObj", mesh=new_mesh_without_mat)
            new_mesh_with_mat = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, frame="CURRENT", apply_transforms=True, keep_vertex_groups=False, keep_materials=True)
            new_obj_with_mat = create_real_mesh.create_new_obj_for_mesh(
                context=C, name="newObj", mesh=new_mesh_with_mat)

            if len(new_obj_without_mat.material_slots) != 0 or len(new_mesh_without_mat.materials) != 0:
                return False
            if len(new_obj_with_mat.material_slots) == 0 or len(new_mesh_with_mat.materials) == 0:
                return False
            if (are_same_mesh(obj.data, new_mesh_without_mat) == False) or (are_same_mesh(obj.data, new_mesh_with_mat) == False):
                return False
            return True

        def check_textures(obj):
            # I know so little about textures that I didn't even manage to create a single one
            return True

        def check_shape_keys(obj):
            bpy.ops.object.shape_key_add(from_mix=False)  # Basis
            bpy.ops.object.shape_key_add(from_mix=False)  # new One
            sk_basis = obj.data.shape_keys.reference_key
            for sk in obj.data.shape_keys.key_blocks:
                if sk != sk_basis:
                    sk2 = sk
            sk2.data[1].co = [1.3, 41, 2.7]  # coordinate of vertex #1
            sk2.data[3].co = [0, 1, 67]
            sk2.value = 1
            new_mesh = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, frame="CURRENT", apply_transforms=True, keep_vertex_groups=False)
            new_obj = create_real_mesh.create_new_obj_for_mesh(
                context=C, name="newObj", mesh=new_mesh)
            select_objs([obj])
            C.object.active_shape_key_index = 0  # index of BasisSK
            bpy.ops.object.shape_key_remove(all=False)
            bpy.ops.object.shape_key_remove(all=False)
            # both shapekeys removed, but no obj shape = shape of sk2
            if are_same_mesh(obj.data, new_mesh) == False:
                return False
            return True

        def check_vertex_groups(obj):
            bpy.ops.object.vertex_group_add()
            bpy.ops.object.mode_set_with_submode(
                mode='EDIT', mesh_select_mode={"VERT"})
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.vertex_group_assign()
            bpy.ops.object.mode_set(mode='OBJECT')
            if len(obj.data.vertices[0].groups) == 0:
                return False
            obj.data.vertices[0].groups[0].weight = 0.5
            for b in (True, False, True, False):  # test if keepVertexGroups parameter works as well
                new_mesh = create_real_mesh.create_real_mesh_copy(
                    context=C, obj=obj, frame="CURRENT", apply_transforms=True, keep_vertex_groups=b)
                new_obj = create_real_mesh.create_new_obj_for_mesh(
                    context=C, name="newObj", mesh=new_mesh)
                if (not (len(new_mesh.vertices[0].groups) == 0 and len(new_obj.vertex_groups) == 0)) == (not b):
                    print("B")
                    return False
                if are_same_mesh(obj.data, new_mesh) == False:
                    print("C")
                    return False
                if b == True and (round(new_mesh.vertices[0].groups[0].weight, 4) != round(0.5, 4)):
                    print("D")
                    return False
            return True

        def check_parents(obj):
            parent_obj = test_helpers.create_subdiv_obj(
                subdivisions=0, type="PLANE")
            select_objs([parent_obj, obj])
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
            parent_obj.location = [1, 2, 3]
            if obj.parent != parent_obj:
                return False
            new_mesh = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, frame="CURRENT", apply_transforms=True, keep_vertex_groups=False)
            new_obj = create_real_mesh.create_new_obj_for_mesh(
                context=C, name="newObj", mesh=new_mesh)
            if new_obj.parent != None:
                return False
            select_objs([obj])
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            bpy.ops.object.transform_apply(
                location=True, rotation=True, scale=True)
            if are_same_mesh(new_mesh, obj.data) == False:
                return False
            return True

        def check_constraints(obj):
            constrain_obj = test_helpers.create_subdiv_obj(
                subdivisions=0, type="CUBE")
            constrain_obj.location = [2, 3, 4]
            select_objs([obj])
            bpy.ops.object.constraint_add(type='COPY_LOCATION')
            new_constraint = obj.constraints[0]
            new_constraint.target = constrain_obj
            new_mesh = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, frame="CURRENT", apply_transforms=True, keep_vertex_groups=False)
            new_obj = create_real_mesh.create_new_obj_for_mesh(
                context=C, name="newObj", mesh=new_mesh)
            select_objs([obj])
            bpy.ops.constraint.apply(
                constraint=new_constraint.name, owner='OBJECT')
            bpy.ops.object.transform_apply(
                location=True, rotation=True, scale=True)
            if len(new_obj.constraints) != 0:
                return False
            if are_same_mesh(new_mesh, obj.data) == False:
                return False
            return True

        def check_transformations(obj):
            obj.location = [3, 4, 5]
            obj.delta_location = [1, 1.5, 7]
            obj.rotation_euler = [2, 5, 1]
            obj.delta_rotation_euler = [9, 8, 0]
            obj.scale = [5, 6, 7]
            obj.delta_scale = [0.5, 0.2, 0.1]
            new_mesh = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, frame="CURRENT", apply_transforms=True, keep_vertex_groups=False)
            new_obj = create_real_mesh.create_new_obj_for_mesh(
                context=C, name="newObj", mesh=new_mesh)
            select_objs([obj])
            bpy.ops.object.transforms_to_deltas(mode='ALL')
            obj.location = obj.delta_location.copy()
            obj.delta_location = [0, 0, 0]
            obj.rotation_euler = obj.delta_rotation_euler.copy()
            obj.delta_rotation_euler = [0, 0, 0]
            obj.scale = obj.delta_scale.copy()
            obj.delta_scale = [1, 1, 1]
            bpy.ops.object.transform_apply(
                location=True, rotation=True, scale=True)
            # believe it or not, but it seems like you cannot just "apply" delta transforms like with normal transforms
            if are_same_mesh(obj.data, new_mesh) == False:
                return False
            return True

        def check_custom_properties(obj):
            # "cycles" seems to be standart property, so at least a length of 1
            original_amount = len(C.object.data.keys())
            bpy.ops.wm.properties_add(data_path="object.data")
            new_mesh = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, frame="CURRENT", apply_transforms=True, keep_vertex_groups=False)
            new_obj = create_real_mesh.create_new_obj_for_mesh(
                context=C, name="newObj", mesh=new_mesh)
            if len(new_mesh.keys()) != original_amount:
                return False
            return True

        for func in (check_materials, check_textures, check_shape_keys, check_vertex_groups, check_parents, check_constraints, check_transformations, check_custom_properties):
            test_helpers.mess_around(switch_scenes=False)
            obj = test_helpers.create_subdiv_obj(subdivisions=3, type="CUBE")
            obj.location = [0, 0, 0]
            obj.rotation_euler = [0, 0, 0]
            obj.scale = [1, 1, 1]
            if func(obj) == False:
                print("subTest of " + func.__name__ + " failed!")
                return False

        return True

    # deleteStuff.py

    def test_delete_verts_faces_edges():
        try:
            from .. import delete_stuff
            importlib.reload(delete_stuff)
            #deleteStuff = bpy.data.texts["deleteStuff.py"].as_module()
        except:
            print("COULDN'T IMPORT deleteStuff")
            return False

        def new_plane():
            obj = test_helpers.create_subdiv_obj(subdivisions=3, type="PLANE")
            obj.name = "testDeletionPlane_1"
            mesh = obj.data
            test_helpers.mess_around(switch_scenes=True)
            return mesh

        # test if vectors are approx. the same while allowing some precision offset
        def vector_match(v1, v2):
            if math.isclose((v1 - v2).length, 0, abs_tol=0.01):
                return True
            else:
                return False

        def find_edge_from_coordinates(co1, co2, mesh):
            co1 = mathutils.Vector(co1)
            co2 = mathutils.Vector(co2)
            for edge in mesh.edges:
                edge_vert1 = mesh.vertices[edge.vertices[0]]
                edge_vert2 = mesh.vertices[edge.vertices[1]]
                if vector_match(edge_vert1.co, co1) or vector_match(edge_vert1.co, co2):
                    if vector_match(edge_vert2.co, co1) or vector_match(edge_vert2.co, co2):
                        return edge.index
            return -1  # when no match was found

        def find_face_from_coordinates(center_co, mesh):
            center_co = mathutils.Vector(center_co)
            for face in mesh.polygons:
                if vector_match(center_co, face.center):
                    return face.index
            return -1

        def find_vertex_from_coordinates(co, mesh):
            co = mathutils.Vector(co)
            for vert in mesh.vertices:
                if vector_match(vert.co, co):
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
        total_verts = 81
        total_edges = 144
        total_faces = 64

        # To be able to do this test stuff in a loop, we create dictionaries for each run
        vert_information_ONE = {"type": "VERTEX", "coordinatesToDelete": vertices, "deleteChildElements": False, "expectedResults": {
            "verts": total_verts - 2, "edges": total_edges - 8, "faces": total_faces - 8}}
        edge_information_ONE = {"type": "EDGE", "coordinatesToDelete": edges, "deleteChildElements": False, "expectedResults": {
            "verts": total_verts - 0, "edges": total_edges - 2, "faces": total_faces - 4}}
        edge_information_TWO = {"type": "EDGE", "coordinatesToDelete": edges, "deleteChildElements": True, "expectedResults": {
            "verts": total_verts - 4, "edges": total_edges - 14, "faces": total_faces - 12}}
        face_information_ONE = {"type": "FACE", "coordinatesToDelete": faces, "deleteChildElements": False, "expectedResults": {
            "verts": total_verts - 0, "edges": total_edges - 0, "faces": total_faces - 2}}
        face_information_TWO = {"type": "FACE", "coordinatesToDelete": faces, "deleteChildElements": True, "expectedResults": {
            "verts": total_verts - 8, "edges": total_edges - 24, "faces": total_faces - 18}}

        for specific_dict in [vert_information_ONE, edge_information_ONE, edge_information_TWO, face_information_ONE, face_information_TWO]:
            test_helpers.mess_around(switch_scenes=True)
            mesh = new_plane()
            # getting the indices of the elements
            indices = []
            for something in specific_dict["coordinatesToDelete"]:
                if specific_dict["type"] == "VERTEX":
                    indices.append(
                        find_vertex_from_coordinates(something, mesh))
                elif specific_dict["type"] == "EDGE":
                    indices.append(find_edge_from_coordinates(
                        something[0], something[1], mesh))
                elif specific_dict["type"] == "FACE":
                    indices.append(find_face_from_coordinates(something, mesh))

            delete_stuff.delete_verts_faces_edges(
                C, mesh, indices, specific_dict["type"], specific_dict["deleteChildElements"])
            test_helpers.mess_around(switch_scenes=True)

            if len(mesh.vertices) != specific_dict["expectedResults"]["verts"] or len(mesh.edges) != specific_dict["expectedResults"]["edges"] or len(mesh.polygons) != specific_dict["expectedResults"]["faces"]:
                print("\nError: see data below")
                print("parameters:  " + specific_dict["type"] + ", " +
                      str(specific_dict["deleteChildElements"]) + "\n")
                print("expected / actualResult")
                print(
                    "verts: " + str(specific_dict["expectedResults"]["verts"]) + "/" + str(len(mesh.vertices)))
                print(
                    "edges: " + str(specific_dict["expectedResults"]["edges"]) + "/" + str(len(mesh.edges)))
                print(
                    "faces: " + str(specific_dict["expectedResults"]["faces"]) + "/" + str(len(mesh.polygons)))
                print("\nmesh name: " + mesh.name)

                return False

            # check if the elements we wanted to delete really have been deleted
            for something in specific_dict["coordinatesToDelete"]:
                if specific_dict["type"] == "VERTEX":
                    index = find_vertex_from_coordinates(something, mesh)
                elif specific_dict["type"] == "EDGE":
                    index = find_edge_from_coordinates(
                        something[0], something[1], mesh)
                elif specific_dict["type"] == "FACE":
                    index = find_face_from_coordinates(something, mesh)

                if index != -1:  # no element with those coordinates should be found, since we deleted them
                    return False

        return True

    def test_coordinateStuff():
        try:
            from .. import coordinates_stuff
            importlib.reload(coordinates_stuff)
            # coordinatesStuff = bpy.data.texts["coordinatesStuff.py"].as_module(
            # )
        except Exception as exception:
            print("COULDN'T IMPORT coordinatesStuff")
            print("Exception message:\n" + str(exception))
            return False
        test_helpers.mess_around(switch_scenes=True)
        bpy.ops.mesh.primitive_plane_add()
        obj = C.object
        mesh = obj.data
        coordinates = coordinates_stuff.get_vertex_coordinates(C, mesh, [1, 3])
        if coordinates_stuff.is_vector_close(C, coordinates[1], coordinates[3], 6) == True:
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
        coordinates = coordinates_stuff.get_vertex_coordinates(C, mesh, "ALL")
        # after resizing, two vertices of the plane (if not diagonal) should have a distance of 0.002 meters
        if coordinates_stuff.is_vector_close(C, coordinates[1], coordinates[3], 6) == True or coordinates_stuff.is_vector_close(C, coordinates[1], coordinates[3], 2) == False:
            return False

        try:
            # I ain't gonna code another function with bpy.ops that does this stuff
            # because I tried
            # and ran into weird and annoying bugs
            from .. import create_real_mesh
            importlib.reload(create_real_mesh)
        except:
            print("Couldn't import a required module (createRealMesh)")
            return False

        # Testing the rotation handler class
        Rot_Handler = coordinates_stuff.RotationHandling

        obj_suzanne_basic = test_helpers.create_subdiv_obj(
            0, "MONKEY")  # without any rotations

        different_rotations = {"ZXY": ("rotation_euler", mathutils.Euler((1, 5, 2), "ZXY"), False),
                               "QUATERNION": ("rotation_quaternion", mathutils.Quaternion(
                                   (0.5, 2.5112, 0.003), 7), False),
                               "XZY": ("rotation_euler", mathutils.Euler((7, 2, 6), "XZY"), False),
                               "AXIS_ANGLE": ("rotation_axis_angle", (9, 6, 3.512, 4.4444), False),
                               "AXIS_ANGLE": ("rotation_axis_angle", (mathutils.Vector((5, 7, 1)), 9), True)
                               }

        for i in [True, False]:

            for (rotation_mode, vector_name_and_values) in different_rotations.items():
                attr_name = vector_name_and_values[0]
                r_vector = vector_name_and_values[1]
                special_axis_angle = vector_name_and_values[2]
                # requires special handling because otherwise exceptions will arise

                obj_suzanne_comparison = test_helpers.create_subdiv_obj(
                    0, "MONKEY")
                obj_suzanne_comparison.rotation_mode = rotation_mode
                if special_axis_angle == False:
                    setattr(obj_suzanne_comparison, attr_name, r_vector)
                else:
                    setattr(obj_suzanne_comparison,
                            "rotation_axis_angle", (9, 5, 7, 1))

                if test_helpers.are_objs_the_same(context=C, obj1=obj_suzanne_basic, obj2=obj_suzanne_comparison, mute=True) == True:
                    # if hasSameTransformations(objSuzanneBasic, objSuzanneComparison) == True:
                    print("x")
                    return False

                for (rotation_mode_inner, vector_name_and_values) in different_rotations.items():
                    new_attr_name = vector_name_and_values[0]
                    new_vector = vector_name_and_values[1]

                    obj_suzanne_with_converted_rotation = test_helpers.create_subdiv_obj(
                        0, "MONKEY")
                    obj_suzanne_with_converted_rotation.rotation_mode = rotation_mode_inner

                    if test_helpers.are_objs_the_same(context=C, obj1=obj_suzanne_comparison, obj2=obj_suzanne_with_converted_rotation, mute=True) == True:
                        return False

                    rot_handler = Rot_Handler()
                    rot_handler.set_rotation_type_of_source_vector(C, r_vector)
                    rot_handler.set_rotation_type_of_target_vector(
                        C, new_vector)
                    if i == False and special_axis_angle == False:
                        # important especially in the context of axis_angle, because we supply a tuple but the object will have a bpy_float array instead
                        real_r_vector = getattr(
                            obj_suzanne_comparison, attr_name)
                    else:
                        real_r_vector = r_vector
                    converted_vector = rot_handler.convert_rotation_vector_to_target(
                        C, real_r_vector)
                    setattr(obj_suzanne_with_converted_rotation,
                            new_attr_name, converted_vector)
                    if test_helpers.are_objs_the_same(context=C, obj1=obj_suzanne_comparison, obj2=obj_suzanne_with_converted_rotation, mute=False) == False:
                        return False
                    D.objects.remove(obj_suzanne_with_converted_rotation)

                    if special_axis_angle == False:
                        setattr(obj_suzanne_comparison, attr_name, r_vector)
                    else:
                        setattr(obj_suzanne_comparison,
                                attr_name, (9, 5, 7, 1))

        return True

    def test_everything_key_frames():
        try:
            from .. import everything_key_frames
            importlib.reload(everything_key_frames)
            # everythingKeyFrames = bpy.data.texts["everythingKeyFrames.py"].as_module(
            # )
        except:
            print("COULDN'T IMPORT everythingKeyFrames")
            return False
        test_helpers.mess_around(switch_scenes=True)
        frame = 199
        C.scene.frame_set(frame)

        # 1. getOrCreate action
        # 2. create keyframes for new fcurves (x and y location)
        # 3. Check if values for object actually change at specified frames

        bpy.ops.mesh.primitive_cube_add()
        obj = C.object
        orig_locations = [obj.location.x, obj.location.y]
        # [0,1] are the indices of x and y in vectors
        for (list_or_dict, axis) in zip([[frame - 8, 0.5555, frame + 8, 1, frame - 12, 0], {frame - 8: 0.5555, frame + 8: 1, frame - 12: 0}], [0, 1]):

            action = everything_key_frames.get_or_create_action(C, obj)
            fcurve = action.fcurves.new("location", index=axis)
            everything_key_frames.create_key_frames_fast(
                C, fcurve, list_or_dict)
            for (changed_frame, value) in zip([frame - 8, frame + 8, frame - 12], [0.5555, 1, 0]):
                C.scene.frame_set(changed_frame)
                current_location = round(obj.location[axis], 5)
                expected_location = round(orig_locations[axis] + value, 5)
                if current_location != expected_location:
                    print("Wrong locations found:" +
                          str(current_location) + " " + str(expected_location))
                    return False

        return True

    def test_vertex_groups():
        try:
            from .. import vertex_groups
            importlib.reload(vertex_groups)
            # vertexGroups = bpy.data.texts["vertexGroups.py"].as_module()
        except:
            print("COULDN'T IMPORT vertexGroups")
            return False
        test_helpers.mess_around(switch_scenes=True)
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
        uniform_value = 0.455
        dict_specific = {0.3: [-1, 100], 0.5: [65, 2], 1: [4, 5, 6, 7, 8]}
        list_unchanged = [10, 11, 12, 45, 46, 47, 30, 5]
        unchaged_uniform_value = 0.111
        # some indices here are in none of the lists above
        list_remove = [-1, 100, 2, 8, 11, 12, ]

        def get_overlaps(list1, list2):
            intersections = set(list1).intersection(list2)
            return list(intersections)

        def remove_invalid_indices(list1):
            return list(vertex_groups.validate_vert_indices_for_vg(context=C, vertex_group_or_mesh=obj.data, vert_indices=list1, return_type="set"))

        obj = test_helpers.create_subdiv_obj(subdivisions=3, type="PLANE")
        # just to remove the selection and active status from the plane
        test_helpers.create_subdiv_obj(subdivisions=0, type="CUBE")
        if C.object == obj or obj.select_get() == True:
            return False  # this shouldnt happen but you never know

        vg1 = vertex_groups.create_vertex_group(
            context=C, obj=obj, vg_name="VG1")
        vg2 = vertex_groups.create_vertex_group(
            context=C, obj=obj, vg_name="VG2")
        if obj.vertex_groups.active != None:
            return False
        vg3 = vertex_groups.create_vertex_group(
            context=C, obj=obj, vg_name="VG3")
        obj.vertex_groups.active = vg3
        vertex_groups.set_vertex_group_values_uniform(
            context=C, vertex_group=vg3, vertex_indices=list_unchanged, value=unchaged_uniform_value)

        vertex_groups.set_vertex_group_values_specific(
            context=C, vertex_group=vg1, weights_for_verts=dict_specific)
        vertex_groups.set_vertex_group_values_uniform(
            context=C, vertex_group=vg1, vertex_indices=list_uniform, value=uniform_value)

        vertex_groups.set_vertex_group_values_uniform(
            context=C, vertex_group=vg2, vertex_indices=list_uniform, value=uniform_value)
        vertex_groups.set_vertex_group_values_specific(
            context=C, vertex_group=vg2, weights_for_verts=dict_specific)

        vertex_groups.remove_verts_from_vertex_group(
            context=C, vertex_group=vg1, vert_indices=list_remove, validate=True)
        vertex_groups.remove_verts_from_vertex_group(
            context=C, vertex_group=vg2, vert_indices=list_remove, validate=True)

        verts_vg1 = vertex_groups.get_verts_in_vertex_group(
            context=C, vertex_group=vg1)
        verts_vg2 = vertex_groups.get_verts_in_vertex_group(
            context=C, vertex_group=vg2)

        expected_verts = list_uniform.copy()
        for weight, index_list in dict_specific.items():
            expected_verts.extend(index_list)
        expected_verts = set(expected_verts)
        expected_verts.difference_update(set(list_remove))
        expected_verts = remove_invalid_indices(expected_verts)
        expected_amount = len(expected_verts)

        if len(verts_vg1) != len(verts_vg2) or len(verts_vg1) != expected_amount or len(verts_vg1) == 0:
            return False

        weights_vg1 = vertex_groups.get_vertex_weights(
            context=C, vertex_group=vg1, vertex_indices=verts_vg1)
        weights_vg2 = vertex_groups.get_vertex_weights(
            context=C, vertex_group=vg2, vertex_indices=verts_vg2)

        # vg1 weights
        for vert_index in verts_vg1:
            weight = round(weights_vg1[vert_index], 3)
            if vert_index in list_remove:
                if weight != None:
                    return False
                else:
                    continue
            elif vert_index in list_uniform:
                if weight != uniform_value:
                    return False
                else:
                    continue
            else:
                x = False
                for expected_weight, index_list in dict_specific.items():
                    if vert_index in index_list and weight == round(expected_weight, 3):
                        x = True
                        break
                if x == True:
                    continue
                # print(str(vertIndex)+"\t"+str(weight))
                return False

        # vg2 weights
        for vert_index in verts_vg2:
            weight = round(weights_vg2[vert_index], 3)
            if vert_index in list_remove:
                if weight != None:
                    return False
                else:
                    continue
            x = False
            for expected_weight, index_list in dict_specific.items():
                if vert_index in index_list:
                    if weight == round(expected_weight, 3):
                        x = True
                        break
                    else:
                        return False
            if x == True:
                continue
            if vert_index in list_uniform:
                if weight == round(uniform_value, 3):
                    continue
                else:
                    return False
            return False

        if obj.vertex_groups.active_index != vg3.index or obj.vertex_groups.active != vg3:
            return False

        vg3_verts = vertex_groups.get_verts_in_vertex_group(
            context=C, vertex_group=vg3)
        vg3_weights = vertex_groups.get_vertex_weights(
            context=C, vertex_group=vg3, vertex_indices=vg3_verts)

        if len(vg3_verts) != len(remove_invalid_indices(list_unchanged)):
            return False
        for vert_index in vg3_verts:
            if round(vg3_weights[vert_index], 3) != unchaged_uniform_value:
                return False

        """Check the VGroupsWithModifiers class that does stuff with modifers"""
        from .. import create_real_mesh

        def has_0_weight_assignments(obj, vg_name):
            vg_exists(obj=obj, vg_name=vg_name)
            # this method is based on the fact that the mask modifier will affect any vertex with a weight that's not exactly zero
            # Using a vertex weight mix modifier, we will be able to increase the weight of *all* vertices that are assigned to that vertex group, including those with a weight of exactly 0
            # Only vertices that aren't assigned will be untouched
            # After increasing, we can try the mask modifier again and see if more gets masked now, which means there were assigned vertices with a weight of 0 originally somewhere
            mod_mask = obj.modifiers.new(name="Mask modifier", type="MASK")
            mod_mask.vertex_group = vg_name
            mod_mask.invert_vertex_group = True
            orig_shape = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, apply_transforms=False)
            obj.modifiers.remove(mod_mask)
            mod_vw_mix = obj.modifiers.new(
                name='Check for zero weight vertices', type="VERTEX_WEIGHT_MIX")
            mod_vw_mix.vertex_group_a = vg_name
            mod_vw_mix.default_weight_b = 0.5
            mod_vw_mix.mix_set = 'A'  # only affect vertices in vertex group a
            mod_vw_mix.mix_mode = 'SET'  # is displayed as 'Replace'

            mod_mask = obj.modifiers.new(name="Mask modifier", type="MASK")
            mod_mask.vertex_group = vg_name
            mod_mask.invert_vertex_group = True
            new_shape = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, apply_transforms=False)
            obj.modifiers.remove(mod_mask)
            obj.modifiers.remove(mod_vw_mix)
            are_the_same = (len(orig_shape.vertices)
                            == len(new_shape.vertices))
            return are_the_same == False

        def has_any_weights_over_zero_at_all(obj, vg_name):
            # a mask modifier only affects assigned vertices with a weight bigger (but not equal to) than 0
            vg_exists(obj=obj, vg_name=vg_name)
            orig_mesh = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, apply_transforms=False)
            mod_mask = obj.modifiers.new(name="Mask modifier", type="MASK")
            mod_mask.vertex_group = vg_name
            mod_mask.invert_vertex_group = True
            new_mesh = create_real_mesh.create_real_mesh_copy(
                context=C, obj=obj, apply_transforms=False)
            obj.modifiers.remove(mod_mask)
            are_the_same = len(orig_mesh.vertices) == len(new_mesh.vertices)
            return are_the_same == False

        def have_the_same_weights(obj1, obj2, vg1_name, vg2_name):
            # use a displace modifier to have an easy way to translate weights to changes in geometry
            vg_exists(obj=obj1, vg_name=vg1_name)
            vg_exists(obj=obj2, vg_name=vg2_name)
            if has_any_weights_over_zero_at_all(obj=obj1, vg_name=vg1_name) == False:
                print(have_the_same_weights.__name__ + ": " +
                      vg1_name + " has no weights over 0")
                return False
            if test_helpers.are_objs_the_same(context=C, obj1=obj1, obj2=obj2, apply_transforms_obj1=False, apply_transforms_obj2=False, mute=False) == False:
                print(have_the_same_weights.__name__ + ".line alpha")
                return False
            mod_displace1 = obj1.modifiers.new(
                name="displace test", type="DISPLACE")
            mod_displace1.vertex_group = vg1_name

            mod_displace2 = obj2.modifiers.new(
                name="displace test 2", type="DISPLACE")
            mod_displace2.vertex_group = vg2_name
            are_the_same = test_helpers.are_objs_the_same(
                context=C, obj1=obj1, obj2=obj2, apply_transforms_obj1=False, apply_transforms_obj2=False, mute=False)
            obj1.modifiers.remove(mod_displace1)
            obj2.modifiers.remove(mod_displace2)
            return are_the_same

        def vg_exists(obj, vg_name):
            # just raises an Exception if a vertex group doesn't even exist
            if obj.vertex_groups.find(vg_name) == -1:
                raise Exception(
                    "Couldnt find any vertex group with that name!")

        original_scene = C.scene

        def create_monkey():
            current_scene = C.scene
            # always create the new monkey in the original scene so all monkeys are in there.
            C.window.scene = original_scene
            # monkey because we use topology for datatransfer
            monky = test_helpers.create_subdiv_obj(
                subdivisions=0, type="MONKEY")
            C.window.scene = current_scene
            return monky

        # basic_monkey will used for comparisons
        basic_monkey = create_monkey()
        # different location than new monkeys.
        basic_monkey.location = [5, 8, 1]

        # following are different tests in functions

        def test_uniform_weight_setting():
            # test if the class method is able to change any set of weights (0, smaller, 1) to the chosen value
            vg_all_0_5 = vertex_groups.create_vertex_group(
                context=C, obj=basic_monkey, vg_name="ALL VERTICES 0.5")
            vertex_groups.set_vertex_group_values_uniform(
                context=C, vertex_group=vg_all_0_5, vertex_indices="ALL", value=0.5)
            vg_some_0_5 = vertex_groups.create_vertex_group(
                context=C, obj=basic_monkey, vg_name="SOME VERTICES 0.5")
            vertex_groups.set_vertex_group_values_uniform(
                context=C, vertex_group=vg_some_0_5, vertex_indices=[1, 7, 23, 83], value=0.5)
            for weight in (0, 0.2, 1):
                new_monkey = create_monkey()
                test_helpers.mess_around(switch_scenes=False)
                vg_some_values = vertex_groups.create_vertex_group(
                    context=C, obj=new_monkey, vg_name="SOME VERTICES " + str(weight))
                vertex_groups.set_vertex_group_values_uniform(
                    context=C, vertex_group=vg_some_values, vertex_indices=[1, 7, 23, 83], value=weight)

                # test with only_assigned = False
                mod_uniform = vertex_groups.VGroupsWithModifiers.vertex_weight_uniform(
                    context=C, obj=new_monkey, vg_name=vg_some_values.name, only_assigned=False, weight=0.5)
                if have_the_same_weights(obj1=basic_monkey, obj2=new_monkey, vg1_name=vg_all_0_5.name, vg2_name=vg_some_values.name) == False:
                    print(
                        "Testing vg_uniform failed. Current weight that was tested: " + str(weight))
                    print("Object doesn't have the excepted weights.")
                    print("Alpha")
                    return False
                if has_0_weight_assignments(obj=new_monkey, vg_name=vg_some_values.name) == True:
                    print(
                        "Testing vg_uniform failed. Current weight that was tested: " + str(weight))
                    print("Object has weights with 0 weights")
                    print("Alpha")
                    return False

                new_monkey.modifiers.remove(mod_uniform)

                # test with only_assigned = True
                mod_uniform = vertex_groups.VGroupsWithModifiers.vertex_weight_uniform(
                    context=C, obj=new_monkey, vg_name=vg_some_values.name, only_assigned=True, weight=0.5)
                if have_the_same_weights(obj1=basic_monkey, obj2=new_monkey, vg1_name=vg_some_0_5.name, vg2_name=vg_some_values.name) == False:
                    print(
                        "Testing vg_uniform failed. Current weight that was tested: " + str(weight))
                    print("Object doesn't have the excepted weights.")
                    print("Beta")
                    return False
                if has_0_weight_assignments(obj=new_monkey, vg_name=vg_some_values.name) == True:
                    print(
                        "Testing vg_uniform failed. Current weight that was tested: " + str(weight))
                    print("Object has weights with 0 weights")
                    print("Beta")
                    return False
                bpy.data.objects.remove(new_monkey)
            return True

        def test_vg_duplication():
            # test if the class method is able to properly duplicate a vertex group.
            # this must include that unassigned vertices do not get assigned with a weight of 0, which can sometimes happen with modifiers.
            new_monkey = create_monkey()
            test_helpers.mess_around(switch_scenes=False)
            some_weights = {0.2: [1, 5, 8], 0.8: [7, 2, 11], 1: [20]}

            vg_specific = vertex_groups.create_vertex_group(
                context=C, obj=basic_monkey, vg_name="Specific vg")
            vertex_groups.set_vertex_group_values_specific(
                context=C, vertex_group=vg_specific, weights_for_verts=some_weights)

            vg_specific_new_monkey = vertex_groups.create_vertex_group(
                context=C, obj=new_monkey, vg_name="Specific vg")
            vertex_groups.set_vertex_group_values_specific(
                context=C, vertex_group=vg_specific_new_monkey, weights_for_verts=some_weights)

            dict_copy = vertex_groups.VGroupsWithModifiers.mimic_vertex_group(
                context=C, obj=new_monkey, vg_to_duplicate=vg_specific_new_monkey.name)
            vg_copy = dict_copy["new vg"]
            new_mod = dict_copy["mod"]

            C.window.scene = original_scene
            if vg_copy.name == vg_specific_new_monkey.name:
                print("Search for line '61235'")
                return False

            if have_the_same_weights(obj1=basic_monkey, obj2=new_monkey, vg1_name=vg_specific.name, vg2_name=vg_copy.name) == False:
                print("Search for line '61236'")
                return False

            if has_0_weight_assignments(obj=new_monkey, vg_name=vg_copy.name) == True:
                print("Search for line '61237'")
                return False

            bpy.data.objects.remove(new_monkey)

            return True

        def test_mimic_vg_of_external_objects():
            # test if the class method is able to mimic a vertex group of another object
            new_monkey = create_monkey()
            test_helpers.mess_around(switch_scenes=False)
            other_weights = {0.3: [6, 1], 0.9: [7, 0], 1: [11, 12, 23]}

            vg_specific = vertex_groups.create_vertex_group(
                context=C, obj=basic_monkey, vg_name="Specific vg another")
            vertex_groups.set_vertex_group_values_specific(
                context=C, vertex_group=vg_specific, weights_for_verts=other_weights)

            new_mod = vertex_groups.VGroupsWithModifiers.mimic_external_vertex_group(
                context=C, main_obj=new_monkey, target_obj=basic_monkey, vg_of_target=vg_specific.name)

            C.window.scene = original_scene
            if have_the_same_weights(obj1=new_monkey, obj2=basic_monkey, vg1_name=vg_specific.name, vg2_name=vg_specific.name) == False:
                print("Search for word '61241'")
            if has_0_weight_assignments(obj=new_monkey, vg_name=vg_specific.name) == True:
                print("Search for word '612342'")
                return False

            bpy.data.objects.remove(new_monkey)

            return True

        def test_removing_zero_weights():
            # test the class method that's supposed to unassign 0 weight vertices.
            have_zero_weights = [7, 1, 9]
            weight_dict_old = {0.0000001: [10, 61, 23, 5], 1: [50, 51, 52]}
            weight_dict_new = {0.0000001: [10, 61, 23, 5], 1: [
                50, 51, 52], 0: have_zero_weights}
            new_monkey = create_monkey()
            test_helpers.mess_around(switch_scenes=False)
            vg_specific = vertex_groups.create_vertex_group(
                context=C, obj=basic_monkey, vg_name="Specific vg")
            vertex_groups.set_vertex_group_values_specific(
                context=C, vertex_group=vg_specific, weights_for_verts=weight_dict_old)

            vg_specific_new = vertex_groups.create_vertex_group(
                context=C, obj=new_monkey, vg_name="Specific vg antother")
            vertex_groups.set_vertex_group_values_specific(
                context=C, vertex_group=vg_specific_new, weights_for_verts=weight_dict_new)

            mod = vertex_groups.VGroupsWithModifiers.remove_0_weights(
                context=C, obj=new_monkey, vg_name=vg_specific_new.name)
            if have_the_same_weights(obj1=basic_monkey, obj2=new_monkey, vg1_name=vg_specific.name, vg2_name=vg_specific_new.name) == False:
                print("Failed to remove 0 weight vertices")
                return False

            if has_0_weight_assignments(obj=basic_monkey, vg_name=vg_specific.name):
                print("Comparison object should not have 0 weights")
                return False
            if has_0_weight_assignments(obj=new_monkey, vg_name=vg_specific_new.name):
                print("Object should not have 0 weights anymore at this point.")
                return False

            bpy.data.objects.remove(new_monkey)
            return True

        ######
        # run all test functions
        ######
        for fun in (test_uniform_weight_setting, test_vg_duplication, test_mimic_vg_of_external_objects, test_removing_zero_weights):
            result = fun()
            if result == False or result != True:
                return False

        ############
        ###finish###
        ############
        return True

    def test_shapekeys():
        try:
            from .. import shapekeys
            importlib.reload(shapekeys)
            # shapekeys = bpy.data.texts["shapekeys.py"].as_module()
        except:
            print("COULDN'T IMPORT shapekeys")
            return False
        test_helpers.mess_around(switch_scenes=True)
        subdivs = 0
        cube = test_helpers.create_subdiv_obj(subdivs, type="CUBE")
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
        basis_sk = cube.active_shape_key
        orig_coordinates = dict()
        for vert in cube.data.vertices:
            orig_coordinates[vert.index] = [vert.co.x, vert.co.y, vert.co.z]

        reference_dict = {"list": [1.9],
                          "mesh": [2.6],
                          "dictionary": [3.5]
                          }
        for ref_key, small_list in reference_dict.items():
            reference_obj = test_helpers.create_subdiv_obj(
                subdivs, type="CUBE")
            small_list.append(reference_obj)
            C.view_layer.objects.active = reference_obj
            t_value = small_list[0]
            bpy.ops.transform.resize(value=(t_value, t_value, t_value), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False,
                                     use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.transform.translate(value=(t_value + 1, t_value + 1, t_value + 1), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
                                        mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.object.transform_apply(
                location=True, rotation=True, scale=True)
            if ref_key == "list":
                co_list = []
                for vert in reference_obj.data.vertices:
                    co_list.extend([vert.co.x, vert.co.y, vert.co.z])
                small_list.append(co_list)
            elif ref_key == "mesh":
                small_list.append(reference_obj.data)
            elif ref_key == "dictionary":
                co_dict = dict()
                for vert in reference_obj.data.vertices:
                    co_dict[vert.index] = vert.co.copy()
                small_list.append(co_dict)

        for refkey, small_list in reference_dict.items():
            t_value = small_list[0]
            #refObj = smallList[1]
            ref = small_list[2]
            new_shapekey = shapekeys.create_shapekey(
                context=C, obj=cube, reference=ref)
            small_list.append(new_shapekey)

        for x in range(2):  # mess stuff up after the first loop was run
            for refkey, small_list in reference_dict.items():
                t_value = small_list[0]
                ref_obj = small_list[1]
                ref = small_list[2]
                sh_key = small_list[3]
                # test if basis shapekey still holds the same coordinates as in the beginning
                for vert in cube.data.vertices:
                    basis_sk_vector = basis_sk.data[vert.index].co.copy()
                    orig_vector = orig_coordinates[vert.index]
                    for xyz in [0, 1, 2]:
                        if round(orig_vector[xyz], 3) != round(basis_sk_vector[xyz], 3):
                            return False

                # test if shapekey has the same coordinates as reference object mesh
                for vert in cube.data.vertices:
                    i = vert.index
                    sk_vector = sh_key.data[i].co.copy()
                    ref_mesh_vector = ref_obj.data.vertices[i].co.copy()
                    for xyz in [0, 1, 2]:
                        if round(sk_vector[xyz], 3) != round(ref_mesh_vector[xyz], 3):
                            return False
            test_helpers.mess_around(switch_scenes=True)

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
        reference_dict_as_list = list(reference_dict.items(
        ))  # items() returns a set and you can't use indices on that
        first_sk = reference_dict_as_list[0][1][3]
        second_sk = reference_dict_as_list[1][1][3]
        third_sk = reference_dict_as_list[2][1][3]

        # mute all
        shapekeys.mute_all_shapekeys(
            context=C, mesh=cube.data, mute=True, exclude=[])
        for sk in cube.data.shape_keys.key_blocks:
            if sk.mute == False:
                return False
        if basis_sk.mute == False:  # if for some reason it isn't included in the previous for-loop
            return False
        # unmute all
        shapekeys.mute_all_shapekeys(
            context=C, mesh=cube.data, mute=False, exclude=[])
        for sk in cube.data.shape_keys.key_blocks:
            if sk.mute == True:
                return False

        shapekeys.mute_all_shapekeys(
            context=C, mesh=cube.data, mute=True, exclude=["BASIS", second_sk])
        if first_sk.mute == False or third_sk.mute == False or basis_sk.mute == True or second_sk.mute == True:
            return False

        shapekeys.mute_all_shapekeys(
            context=C, mesh=cube.data, mute=False, exclude=[first_sk])
        if first_sk.mute == False or third_sk.mute == True or basis_sk.mute == True or second_sk.mute == True:
            return False

        return True

    def test_modifiers():
        try:
            from .. import modifiers
            importlib.reload(modifiers)
            # modifiers = bpy.data.texts["modifiers.py"].as_module()
        except:
            print("COULDN'T IMPORT modifiers")
            return False
        test_helpers.mess_around(switch_scenes=True)
        """
        1. Add a few different modifiers
        2. get all their positions
        3. Check if the modifiers with first and last position are indeed at those positions
        4. Try to put another modifier in last position
        5. Check again
        6. repeat 4 and 5, but this time with a "negative" position
        """
        obj = test_helpers.create_subdiv_obj(subdivisions=0, type="CUBE")
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        bpy.ops.object.modifier_add(type='MASK')
        bpy.ops.object.modifier_add(type='MESH_SEQUENCE_CACHE')
        bpy.ops.object.modifier_add(type='MESH_SEQUENCE_CACHE')
        bpy.ops.object.modifier_add(type='MESH_SEQUENCE_CACHE')
        bpy.ops.object.modifier_add(type='MESH_SEQUENCE_CACHE')
        orig_scene = C.scene
        test_helpers.mess_around(switch_scenes=True)
        positions = dict()  # {position: modifier}
        for mod in obj.modifiers:
            positions[modifiers.get_modifier_position_in_stack(
                context=C, modifier=mod)] = mod
        first_mod = positions[0]
        last_mod = positions[len(obj.modifiers) - 1]
        # need to switch back to original scene if we want to select the obj
        C.window.scene = orig_scene
        C.view_layer.objects.active = obj
        with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
            # hides any print statements
            # Because the Blender code below will try to print a warning, but we don't want the user to see that
            if bpy.ops.object.modifier_move_up(modifier=first_mod.name) != {'CANCELLED'} or bpy.ops.object.modifier_move_down(modifier=last_mod.name) != {'CANCELLED'}:
                # trying to move a modifier up or down returns {'FINISHED'} if it can move up/down, and {'CANCELLED'} if it can't. (Meaning it already is at first/last position)
                return False
        test_helpers.mess_around(switch_scenes=True)

        # setting the second modifier to last position in stack
        second_mod = positions[1]
        third_mod = positions[2]
        modifiers.move_modifer_to_position_in_stack(
            context=C, modifier=second_mod, position=len(obj.modifiers) - 1)
        last_pos_positive = modifiers.get_modifier_position_in_stack(
            context=C, modifier=second_mod)
        modifiers.move_modifer_to_position_in_stack(
            context=C, modifier=third_mod, position=-1)
        last_pos_negative = modifiers.get_modifier_position_in_stack(
            context=C, modifier=third_mod)
        if last_pos_negative != last_pos_positive or last_pos_negative != len(obj.modifiers) - 1:
            return False

        # testing the tryToBind() function

        def object_in_current_scene(obj):
            C.window.scene = obj.users_scene[0]

        def object_in_other_scene(obj):
            new_scene = bpy.data.scenes.new("59123519")
            C.window.scene = new_scene
            if C.scene in list(obj.users_scene):
                raise Exception("Scene context setting failed, aborting test")

        def object_in_no_scene(obj):
            for coll in tuple(obj.users_collection):
                coll.objects.unlink(obj)
            if len(obj.users_scene) != 0:
                raise Exception("Scene context setting failed, aborting test")

        def test_surface_deform(obj):
            smod = obj.modifiers.new(
                name='surfaceDeformMod', type='SURFACE_DEFORM')
            empty_obj = test_helpers.create_subdiv_obj(0, "CUBE")
            empty_obj.data.clear_geometry()
            full_obj = test_helpers.create_subdiv_obj(0, "CUBE")
            test_helpers.mess_around(False)

            smod.target = empty_obj
            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=smod) == True:
                return False  # target without geometry cannot be bound

            smod.target = full_obj
            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=smod) == False:
                return False  # binding should be possible and thus successful
            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=smod) == True:
                return False  # unbinding, so no bind should be detected

            smod.target = None
            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=smod) == True:
                return False  # no target obj is set and binding shouldn't be possible

            smod.target = full_obj
            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=smod) == False:
                return False  # binding should be possible and thus successful

            return True

        def test_laplacian_deform(obj):
            """
            Note on the Laplacian Deform modifier:
            Even without any coding it behaves weird (Blender 3.0)
            Try these steps to see what I mean as an example:

            - add laplac mod
            - add two empty vertex groups to object
            - choose last empty vertex group
            - try to bind
            - will fail

            - add laplac mod
            - add two empty vertex groups
            - add weight to ONE of them
            - choose empty vertex group
            - try to bind
            - will succeed
            - even shows difference, unlike if you select the filled one.

            This is why this testfunction makes sure only one single vertex groups exists when the modifier is bound


            I once even managed to bind an empty vertex group where the mod showed the "unbind" button while also, 
            simulateneously, showing an error message that the vertex group is invalid.
            """

            ld_mod = obj.modifiers.new(
                name='LaplacianDeformMod', type='LAPLACIANDEFORM')
            test_helpers.mess_around(False)

            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=ld_mod) == True:
                return False  # doesnt work with no vertex group selected

            filled_vg = obj.vertex_groups.new(name="filled")
            # adds a weight of 0.5 to vertex with index 0
            filled_vg.add([0], 0.5, "ADD")
            ld_mod.vertex_group = filled_vg.name
            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=ld_mod) == False:
                return False  # should work since vertex group has at least one vertex in it
            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=ld_mod) == True:
                # unbinding, so False is expected as the return value.
                return False

            obj.vertex_groups.remove(filled_vg)
            empty_vg = obj.vertex_groups.new(name="empty")
            ld_mod.vertex_group = empty_vg.name
            # if modifiers.tryToBind(context=C, modifier=ldMod) == True:
            # I gave up with this: it shouldn't be possible but because, as I said,
            # the laplacian deform mod can behave very weird, you will be able to bind an empty vertex group here.
            # Making the test fail everytime, not because our function doesn't work, but because the modifier is bugged.
            #     print(2)
            #     return False  # should not work because vertex group is empty

            return True

        def test_mesh_deform(obj):
            md_mod = obj.modifiers.new(
                name='MeshDeformMod', type='MESH_DEFORM')
            target_obj = test_helpers.create_subdiv_obj(0, "PLANE")
            test_helpers.mess_around(False)

            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=md_mod) == True:
                return False  # no target object selected, binding shouldnt be possible
            md_mod.object = target_obj

            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=md_mod) == False:
                return False  # target object selected, binding should be possible
            if modifiers.ButtonPresser.try_to_bind(context=C, modifier=md_mod) == True:
                # unbinding, so False should be returned by the function.
                return False

            return True

        def test_data_transfer(obj):
            obj_target = test_helpers.create_subdiv_obj(2, "PLANE")
            obj_target.vertex_groups.new()
            dt_mod = obj.modifiers.new(name='Data transfer', type='DATA_TRANSFER')
            dt_mod.object = obj_target
            dt_mod.use_vert_data = True
            dt_mod.data_types_verts = {'VGROUP_WEIGHTS'}
            dt_mod.vert_mapping = 'TOPOLOGY'
            dt_mod.layers_vgroup_select_src = 'ALL'
            test_helpers.mess_around(False)

            if len(obj.vertex_groups) != 0:
                return False
            modifiers.ButtonPresser.data_transfer_button(dt_mod)
            if len(obj.vertex_groups) == 0:
                return False

            return True

        for test_some_mod in (test_surface_deform, test_laplacian_deform, test_mesh_deform, test_data_transfer):
            # testing all operator binds in different scene-context
            for set_scene_context in (object_in_current_scene, object_in_other_scene, object_in_no_scene):
                plane = test_helpers.create_subdiv_obj(0, "PLANE")
                set_scene_context(plane)
                test_helpers.mess_around(False)
                if test_some_mod(plane) == False:
                    print(test_some_mod.__name__)
                    print(set_scene_context.__name__)
                    return False
                D.objects.remove(plane)

        return True

    def test_custom_properties():
        try:
            from ..advanced import custom_properties
            importlib.reload(custom_properties)
            # modifiers = bpy.data.texts["modifiers.py"].as_module()
        except:
            print("COULDN'T IMPORT custom_properties")
            return False

        name_to_use = "Bread"
        description_to_use = "...can be tasty"

        def test_bool(blend_object_creator):
            blend_obj = blend_object_creator()
            for default_to_use in (0, 1, False, True):
                handler = custom_properties.CustomPropertyHandler.SimpleBool(blend_obj=blend_obj, name=name_to_use, description=description_to_use, default=default_to_use)
                if handler.get_value() != default_to_use:
                    print("Wrong default value for bool prop")
                    return False
                if handler.type != bool:
                    print("Wrong type for boolean prop")
                    return False
                t_dict = handler.get_dict()
                if t_dict["description"] != description_to_use:  # has no "name" key
                    print("Wrong name or description")
                    return False
                custom_properties.CustomPropertyHandler.change_description(blend_obj=blend_obj,prop_name=name_to_use,description="new Description")
                if handler.get_dict()["description"] != "new Description":
                    print("Description wasn't changed")
                    return False
            return True

        def test_float(blend_object_creator):
            blend_obj = blend_object_creator()
            handler = custom_properties.CustomPropertyHandler.SimpleFloat(blend_obj=blend_obj, name=name_to_use, description=description_to_use, default=8, min=0, max=51, soft_min=None, soft_max=15)
            if type(handler.get_value()) != float or handler.get_value() != 8.0:
                print("Wrong default value for float prop")
                return False
            if handler.type != float:
                print("Wrong type for float prop")
                return False
            t_dict = handler.get_dict()
            if t_dict["description"] != description_to_use:  # has no "name" key
                print("Wrong name or description")
                return False
            return True

        def test_integer(blend_object_creator):
            blend_obj = blend_object_creator()
            handler = custom_properties.CustomPropertyHandler.SimpleInteger(blend_obj=blend_obj, name=name_to_use, description=description_to_use, default=-89, min=-10000, max=24, soft_min=0, soft_max=None)
            if handler.get_value() != -89:
                print("Wrong default value for integer prop")
                return False
            if handler.type != int:
                print("Wrong type for integer prop")
            t_dict = handler.get_dict()
            if t_dict["description"] != description_to_use:  # has no "name" key
                print("Wrong name or description")
                return False
            return True

        def test_set_and_get_val(blend_object_creator):
            for prop_val in [1, "Hi", D.objects[0], [D.meshes[0], D.scenes[0]]]:
                blend_obj = blend_object_creator()
                if custom_properties.CustomPropertyHandler.just_set_val(blend_obj=blend_obj, prop_name="New custom prop", value=prop_val, test_for_success=True) != True:
                    print("Setting value of type " + str(type(prop_val)) + " failed")
                    return False
                if custom_properties.CustomPropertyHandler.just_get_val(blend_obj=blend_obj, prop_name="New custom prop") != prop_val:
                    print("just_get_val() method failed")
                    return False

            return True

        create_scene = lambda: D.scenes.new(name="new scene for testing")
        create_obj = lambda: test_helpers.create_subdiv_obj(subdivisions=2, type="MONKEY")
        create_collection = lambda: D.collections.new(name="new Collection for testing")

        for create_blend_obj in (create_obj, create_scene, create_collection):
            for fun in (test_bool, test_float, test_integer, test_set_and_get_val):
                if fun(create_blend_obj) != True:
                    return False

        return True

    def test_drivers():
        try:
            from ..advanced import drivers
            importlib.reload(drivers)
            # modifiers = bpy.data.texts["modifiers.py"].as_module()
        except:
            print("COULDN'T IMPORT drivers")
            return False

        # different types of objects to add drivers to
        objects_and_props = []
        bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 0), rotation=(1.39626, 1.08593e-07, 0.0977383), scale=(1, 1, 1))
        obj_camera = C.object
        camera = obj_camera.data
        objects_and_props += [(camera, (lambda: camera.lens), "lens")]

        scene_new = D.scenes.new("new scene")
        objects_and_props += [(scene_new, (lambda: scene_new.gravity[1]), "gravity", 1)]

        obj_plane = test_helpers.create_subdiv_obj(subdivisions=0, type="PLANE")
        mod_wave = obj_plane.modifiers.new(name="wave",type="WAVE")
        objects_and_props += [(mod_wave, (lambda: mod_wave.show_viewport),"show_viewport")]

        bpy.ops.object.light_add(type='SUN', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        obj_sun = C.object
        sun = obj_sun.data
        obj_monkey = test_helpers.create_subdiv_obj(subdivisions=2, type="MONKEY")
        obj_monkey["cust prop"] = 2.7
        obj_monkey.update_tag()  # otherwise driver cannot access that custom property

        for stuff in objects_and_props:
            boss_obj = stuff[0]
            fun_get_value = stuff[1]
            data_path = stuff[2]
            if len(stuff) == 4:
                prop_index = stuff[3]
                driver_helper = drivers.DriverHelper(boss_object=boss_obj, property_name=data_path, index=prop_index)
            else:
                driver_helper = drivers.DriverHelper(boss_object=boss_obj, property_name=data_path)
            if len(driver_helper.driver.variables) != 0:
                print("No variables should exist yet")
                return False
            if driver_helper.driver.expression != "":
                print(driver_helper.driver.expression)
                print("Expression should be empty.")
                return False
            var_normal = driver_helper.add_variable("new_variable")
            if var_normal.name != "new_variable":
                print("Wrong variable name")
                return False
            var_linked_normal = driver_helper.add_variable_linked_to_property(prop_owner=sun, property_name="energy")
            var_linked_custom = driver_helper.add_variable_linked_to_property(prop_owner=obj_monkey, property_name="cust prop", is_custom_property=True)
            driver_helper.driver.expression = var_linked_normal.name + " + " + var_linked_custom.name

            driver_helper.get_variables()

            # # is_valid returns False if a variable isn't set properly, but not if the driver expression is wrong.
            # boss_obj.animation_data.drivers.update()
            # boss_obj.update_tag()
            # driver_helper.fcurve.update()
            # D.worlds[0].update_tag()
            # if driver_helper.driver.is_valid != False:
            #     print("Driver should be invalid, but isn't")
            #     print(boss_obj.name)
            #     return False
            # driver_helper.driver.variables.remove(var_normal)
            # if driver_helper.driver.is_valid != True:
            #     print("Driver should be valid, but isn't")
            #     return False

            if boss_obj == camera:
                driver_helper.refresh_driver_value(context=C)
                if round(fun_get_value(), 4) != round(obj_monkey["cust prop"] + sun.energy, 4):
                    print(fun_get_value())
                    print(obj_monkey["cust prop"] + sun.energy)
                    print(driver_helper.driver.expression)
                    print("Wrong end value!")
                    print(boss_obj.name)
                    return False

        return True

    def test_node_helper():
        try:
            from ..advanced import node_helper
            importlib.reload(node_helper)
            # modifiers = bpy.data.texts["modifiers.py"].as_module()
        except:
            print("COULDN'T IMPORT node_helper")
            return False
        #currently only tests geometry node modifer

        obj_monkey = test_helpers.create_subdiv_obj(subdivisions=1, type="MONKEY")
        mod_geo_node = obj_monkey.modifiers.new(name="Geometry Node modifier",type='NODES')
        random_node_group = bpy.data.node_groups.new(name='Geometry Nodes Test', type='GeometryNodeTree')
        for source in (None, mod_geo_node, random_node_group, mod_geo_node.node_group.name):
            nhelper = node_helper.GeometryNodesModifierHandler(source=source, reset=False)
            if type(nhelper.node_group) != bpy.types.GeometryNodeTree:
                print("Node group wasn't identified correctly.")
                print(type(nhelper.node_group))
                return False

        nhelper = node_helper.GeometryNodesModifierHandler(source=mod_geo_node, reset=True)
        if len(nhelper.node_group.links) != 0:
            print("Reset didn't work, there are links")
            return False
        if nhelper.main_input_node == None or nhelper.main_output_node == None:
            print("Reset didn't work, no input/output node exists")
            return False
        
        input_socket = nhelper.add_input(bl_socket_idname='NodeSocketBool', name="Some Input")
        output_socket = nhelper.add_output(bl_socket_idname='NodeSocketFloat', name="Some output")
        for socket in (input_socket, output_socket):
            if issubclass(type(socket),bpy.types.NodeSocketInterface) == False:
                print("Wrong type, expected NodeSocketInterface, got:")
                print(type(socket))
                return False
        
        if (input_socket.identifier in set(mod_geo_node.keys()) == False) or (output_socket.identifier+'3_attribute_name' in set(mod_geo_node.keys())==False) :
            print("Problem with input/output socket on modifier")
            return False
        
        node_transform = nhelper.add_node('GeometryNodeTransform')
        if len(nhelper.node_group.nodes) != 3:
            print("Wrong amount of nodes")
            return False
        
        nhelper.connect_nodes(output_socket=nhelper.main_input_node.outputs["Some Input"], input_socket=node_transform.inputs["Rotation"])
        link = node_transform.inputs["Rotation"].links[0]
        if link.from_socket != nhelper.main_input_node.outputs[1]:
            print("Wrong link took place")
            return False

        nhelper.clear_all_nodes()
        if len(nhelper.node_group.nodes) != 0:
            print("Clearing nodes failed")
            return False
        if nhelper.main_input_node != None or nhelper.main_output_node != None:
            print("Main input/output nodes weren't cleared from instance")
            return False

        node_group_new = bpy.data.node_groups.new(name='Another Geometry Nodes Test', type='GeometryNodeTree')
        nhelper_new = node_helper.GeometryNodesModifierHandler(source=node_group_new, reset=True)
        nhelper_new.link_ng_to_modifier(mod_geo_node)

        if mod_geo_node.node_group != node_group_new:
            print("Using new node group for modifier failed")
            return False

        node_transfer_attr =  nhelper_new.add_node(node_type='GeometryNodeAttributeTransfer')
        input_socket = node_helper.GeometryNodesModifierHandler.get_input_socket_by_identifier(node=node_transfer_attr,socket_identifier='Attribute_002')
        for i in range(len(node_transfer_attr.inputs)):
            if i == 3 and node_transfer_attr.inputs[i] != input_socket:
                print("Wrong input socket from identifier")
                return False
            if i != 3 and node_transfer_attr.inputs[i] == input_socket:
                print("Wrong input socket from identifier")
                return False
        node_capture_attr = nhelper_new.add_node(node_type='GeometryNodeCaptureAttribute')
        output_socket = node_helper.GeometryNodesModifierHandler.get_output_socket_by_identifier(node=node_capture_attr, socket_identifier='Attribute_001')
        for i in range(len(node_capture_attr.outputs)):
            if i == 2 and node_capture_attr.outputs[i] != output_socket:
                print("Wrong output socket from identifier")
                return False
            if i != 2 and node_capture_attr.outputs[i] == output_socket:
                print("Wrong output socket from identifier")
                return False

        nhelper.deselect_all_nodes()
        return True

    x = True
    # fun as in function, not the joy I haven't experienced since my first day at highschool
    for fun in (
            test_select_objects, test_delete_object_and_mesh, test_information_gathering, test_tag_vertices, test_create_collection, test_create_real_mesh,
            test_delete_verts_faces_edges, test_coordinateStuff, test_everything_key_frames, test_vertex_groups, test_shapekeys,
            test_modifiers, test_custom_properties, test_drivers,test_node_helper):
        try:
            if fun() == True:
                None
            else:
                print("\n\n")
                print("Test negative in " + fun.__name__ + " !")
                x = False
        except Exception as exception:
            print("\n\n")
            print("Exception occured in " + fun.__name__ + " !")
            print(traceback.format_exc())
            # print("message:\n"+str(exception))
            x = False
        if x == False:
            # 1/0
            pass

    if x == True:
        print("\nEvery test succeeded! (That's good)")
        return True
    else:
        print("\nAt least one test failed. (That's not good)")
        return False


if __name__ == "__main__":
    run()
