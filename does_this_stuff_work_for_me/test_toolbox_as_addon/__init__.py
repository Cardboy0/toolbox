import importlib
import sys
import warnings
import traceback
import bpy

bl_info = {
    "name": "Toolbox Testing",
    "author": "Cardboy0",
    "blender": (3, 4, 0),
    "description": "Simply runs the test methods from the toolbox repository, only from inside an add-on.",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "support": 'TESTING'}


class OBJECT_OT_test_toolbox(bpy.types.Operator):
    bl_idname = "object.test_toolbox"
    bl_label = "Tests the toolbox repository for functionality."

    def execute(self, context):
        from test_toolbox_as_addon.toolbox_to_test.does_this_stuff_work_for_me import run_tests as run_toolbox_tests
        # import here instead of the start of this file because otherwise the whole add-on wouldn't work when import fails
        importlib.reload(run_toolbox_tests)

        failed_contexts = []
        print("Running with operator context")
        if run_toolbox_tests.run(context=context) == False:
            failed_contexts += ["Operator Context"]

        print("\n\nRunning with no operator context")
        if run_toolbox_tests.run(context=None) == False:
            failed_contexts += ["No Context"]

        print("+" * 200 + "\n\n")
        if len(failed_contexts) == 0:
            print("All tests for every context succeeded")
        else:
            print("At least one test failed with the following contexts:")
            for failed_context in failed_contexts:
                print(failed_context)
        print("\nFinished Toolbox Add-on Testing")
        print("+" * 200 + "\n\n\n")
        return {'FINISHED'}


class OBJECT_PT_test_toolbox(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_label = "Test Toolbox"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator(
            operator=OBJECT_OT_test_toolbox.bl_idname,
            text="Test the toolbox!"
        )


def register():
    bpy.utils.register_class(OBJECT_OT_test_toolbox)
    bpy.utils.register_class(OBJECT_PT_test_toolbox)


def unregister():
    bpy.utils.unregister_class(OBJECT_PT_test_toolbox)
    bpy.utils.unregister_class(OBJECT_OT_test_toolbox)
