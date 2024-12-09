import bpy, aud, os

bl_info = {
    "name": "Audio Notifier",
    "author": "Loïc \"Lauloque\" Dautry",
    "version": (1, 0, 1),
    "blender": (4, 3, 0),
    "location": "Preferences > Add-ons",
    "description": "Plays custom sounds notifications on specific events",
    "warning": "",
    "wiki_url": "",
    "category": "System",
}

class PlaySoundOperator(bpy.types.Operator):
    bl_idname = "audio_notifier.play_sound"
    bl_label = "Play Sound"
    bl_options = {'INTERNAL'}

    sound_type: bpy.props.StringProperty()  # Ensure this is defined correctly

    def execute(self, context):
        prefs = bpy.context.preferences.addons[__package__].preferences

        sound_paths = {
            "cancel": prefs.cancel_audio_path,
            "success": prefs.success_audio_path,
            "warning": prefs.warning_audio_path
        }

        file_path = sound_paths.get(self.sound_type)
        if not file_path:
            self.report({'ERROR'}, f"Unknown sound type: {self.sound_type}")
            return {'CANCELLED'}

        try:
            device = aud.Device()
            sound = aud.Sound(file_path)
            device.play(sound)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to play sound: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

class AudioNotifierAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    addon_dir = os.path.dirname(__file__)
    cancel_audio_path = os.path.join(addon_dir, "sounds", "cancel.ogg")
    success_audio_path = os.path.join(addon_dir, "sounds", "success.ogg")
    warning_audio_path = os.path.join(addon_dir, "sounds", "warning.ogg")

    cancel_audio_path: bpy.props.StringProperty(
        name="Cancel Audio Path",
        description="Path to the audio file played on render cancel",
        subtype='FILE_PATH',
        default=cancel_audio_path
    )
    success_audio_path: bpy.props.StringProperty(
        name="Success Audio Path",
        description="Path to the audio file played on render success",
        subtype='FILE_PATH',
        default=success_audio_path
    )
    warning_audio_path: bpy.props.StringProperty(
        name="Warning Audio Path",
        description="Path to the audio file played on warnings",
        subtype='FILE_PATH',
        default=warning_audio_path
    )

    enable_render_sound: bpy.props.BoolProperty(
        name="Enable Render Sound",
        description="Enable/disable sound for render completion/cancellation",
        default=True
    )
    enable_bake_sound: bpy.props.BoolProperty(
        name="Enable Bake Sound",
        description="Enable/disable sound for bake completion/cancellation",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Audio Paths")
        layout.use_property_split = True
        
        row = layout.row(align=True)
        row.prop(self, "cancel_audio_path", text="Cancel")
        row.operator("audio_notifier.play_sound", text="", icon='PLAY').sound_type = "cancel"

        row = layout.row(align=True)
        row.prop(self, "success_audio_path", text="Success")
        row.operator("audio_notifier.play_sound", text="", icon='PLAY').sound_type = "success"

        row = layout.row(align=True)
        row.prop(self, "warning_audio_path", text="Warning")
        row.operator("audio_notifier.play_sound", text="", icon='PLAY').sound_type = "warning"
        
        layout.label(text="Which events to get notified:")
        layout.use_property_split = True
        
        row = layout.row(align=True)
        row.prop(self, "enable_render_sound", text="Rendering")
        row = layout.row(align=True)
        row.prop(self, "enable_bake_sound", text="Baking")


### Handlers for render complete/canceled
def on_render_complete(scene):
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.enable_render_sound:
        bpy.ops.audio_notifier.play_sound(sound_type="success")

def on_render_cancel(scene):
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.enable_render_sound:
        bpy.ops.audio_notifier.play_sound(sound_type="cancel")
    

### Handlers for baking complete/cancel
def on_bake_complete(scene):
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.enable_bake_sound:
        bpy.ops.audio_notifier.play_sound(sound_type="success")

def on_bake_cancel(scene):
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.enable_bake_sound:
        bpy.ops.audio_notifier.play_sound(sound_type="cancel")


def register():
    bpy.utils.register_class(AudioNotifierAddonPreferences)
    bpy.utils.register_class(PlaySoundOperator)

    # Register handlers
    bpy.app.handlers.render_complete.append(on_render_complete)
    bpy.app.handlers.render_cancel.append(on_render_cancel)
    bpy.app.handlers.object_bake_complete.append(on_bake_complete)
    bpy.app.handlers.object_bake_cancel.append(on_bake_cancel)


def unregister():
    bpy.utils.unregister_class(AudioNotifierAddonPreferences)
    bpy.utils.unregister_class(PlaySoundOperator)

    # Safe remove handlers
    # Need this to avoid errors when disabling extension,
    #     apparently some handlers don't get registered
    #     right away, causing errors.
    def safe_remove(handler, handler_list):
        handler_name = handler.__name__
        if handler in handler_list:
            handler_list.remove(handler)
        else:
            print(f"Handler not found in list: {handler_name}")

    safe_remove(on_render_complete, bpy.app.handlers.render_complete)
    safe_remove(on_render_cancel, bpy.app.handlers.render_cancel)
    safe_remove(on_bake_complete, bpy.app.handlers.object_bake_complete)
    safe_remove(on_bake_cancel, bpy.app.handlers.object_bake_cancel)
