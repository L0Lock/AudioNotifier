import bpy


class OBJECT_PT_ExampleGui(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Example Gui"
    bl_idname = "OBJECT_PT_example_gui"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        if context.preferences.addons.find("bl_ext.extensions.audio_notifier") == -1:
            # propose enabling the addon
            layout.label(text="Required addon not found:", icon="ERROR")
            layout.label(text="'Audio Notifier' by Loïc \"Lauloque\" Dautry")
            layout.operator("preferences.addon_enable").module="bl_ext.extensions.audio_notifier"

        else:
            # your code that needs to play sound
            layout.label(text="Audio Notifier found")
            layout.operator("preferences.addon_disable").module="bl_ext.extensions.audio_notifier"

def register():
    bpy.utils.register_class(OBJECT_PT_ExampleGui)


def unregister():
    bpy.utils.unregister_class(OBJECT_PT_ExampleGui)


if __name__ == "__main__":
    register()
