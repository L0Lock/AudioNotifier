import os

import aud
import bpy


class AudioNotifier_OT_PlaySound(bpy.types.Operator):
    """
    Plays a sound notification using a sound_type from the addon's prefs:
        'cancel'
        'success'
        'warning'
    """
    bl_idname = "audio_notifier.play_sound"
    bl_label = "Play Sound"
    bl_options = {'INTERNAL'}

    sound_type: bpy.props.StringProperty()  # Ensure this is defined correctly

    def execute(self, context):
        """Execute"""
        prefs = bpy.context.preferences.addons[__package__].preferences
        if not prefs:
            self.report(
                {'ERROR'},
                "Audio Notifier's preferences not initialized."
            )
            return {'CANCELLED'}

        device = prefs.get_device()

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
            sound = aud.Sound(file_path)
            device.play(sound)
        except Exception as e:
            self.report({'ERROR'}, f"An unexpected error occurred: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


class AudioNotifierAddonPreferences(bpy.types.AddonPreferences):
    """Addon's Preferences"""
    bl_idname = __package__
    addon_dir = os.path.dirname(__file__)
    cancel_audio_path = os.path.join(addon_dir, "sounds", "cancel.ogg")
    success_audio_path = os.path.join(addon_dir, "sounds", "success.ogg")
    warning_audio_path = os.path.join(addon_dir, "sounds", "warning.ogg")
    device = None

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
    developer_print: bpy.props.BoolProperty(
        name="Enable Developer Prints in System Console",
        description=(
            "Menu Windows > Toggle. Helps with debugging issues in "
            "the addon."
        ),
        default=True
    )

    def get_device(self):
        """Ensure a single audio device is used throughout the session."""
        if self.device is None:
            self.device = aud.Device()
        return self.device

    def draw(self, context):
        """Draw"""
        layout = self.layout

        layout.label(text="Audio Paths")
        layout.use_property_split = True

        row = layout.row(align=True)
        row.prop(self, "cancel_audio_path", text="Cancel")
        row.operator(
            "audio_notifier.play_sound",
            text="",
            icon='PLAY'
        ).sound_type = "cancel"
        if not os.path.isfile(self.cancel_audio_path):
            row = layout.row(align=True)
            row.label(text="")
            row.label(text="File not found!", icon='ERROR')

        row = layout.row(align=True)
        row.prop(self, "success_audio_path", text="Success")
        row.operator(
            "audio_notifier.play_sound",
            text="",
            icon='PLAY'
        ).sound_type = "success"
        if not os.path.isfile(self.success_audio_path):
            row = layout.row(align=True)
            row.label(text="")
            row.label(text="File not found!", icon='ERROR')

        row = layout.row(align=True)
        row.prop(self, "warning_audio_path", text="Warning")
        row.operator(
            "audio_notifier.play_sound",
            text="",
            icon='PLAY'
        ).sound_type = "warning"
        if not os.path.isfile(self.warning_audio_path):
            row = layout.row(align=True)
            row.label(text="")
            row.label(text="File not found!", icon='ERROR')

        layout.label(text="Which events to get notified:")
        layout.use_property_split = True

        row = layout.row(align=True)
        row.prop(self, "enable_render_sound", text="Rendering")
        row = layout.row(align=True)
        row.prop(self, "enable_bake_sound", text="Baking")

        layout.label(text="Developer Section")
        layout.use_property_split = True

        row = layout.row(align=True)
        row.prop(self, "developer_print")


def dprint(message: str):
    """Prints in the system console if the addon's developer printing is ON"""
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.developer_print:
        print(f": {message}")


def on_render_complete(scene):
    """Handler Render Complete"""
    dprint("Render Complete Handler detected")
    prefs = bpy.context.preferences.addons[__package__].preferences
    if os.path.isfile(prefs.enable_render_sound):
        dprint("  found audio file, playing...")
        bpy.ops.audio_notifier.play_sound(sound_type="success")
    else:
        dprint("  couldn't find sound file!")


def on_render_cancel(scene):
    """Handler Render Cancel"""
    dprint("Render Cancel Handler detected")
    prefs = bpy.context.preferences.addons[__package__].preferences
    if os.path.isfile(prefs.enable_render_sound):
        dprint("  found audio file, playing...")
        bpy.ops.audio_notifier.play_sound(sound_type="cancel")
    else:
        dprint("  couldn't find sound file!")


def on_bake_complete(scene):
    """Handler Bake Complete"""
    dprint("Bake Complete Handler detected")
    prefs = bpy.context.preferences.addons[__package__].preferences
    if os.path.isfile(prefs.enable_bake_sound):
        dprint("  found audio file, playing...")
        bpy.ops.audio_notifier.play_sound(sound_type="success")
    else:
        dprint("  couldn't find sound file!")


def on_bake_cancel(scene):
    """Handler Bake Cancel"""
    dprint("Bake Cancel Handler detected")
    prefs = bpy.context.preferences.addons[__package__].preferences
    if os.path.isfile(prefs.enable_bake_sound):
        dprint("  found audio file, playing...")
        bpy.ops.audio_notifier.play_sound(sound_type="cancel")
    else:
        dprint("  couldn't find sound file!")


def register_handlers(dummy=None):
    """
    Register app handlers for render and bake events if not already present.
    """
    if bpy.app.background:
        return

    def add_once(handler, handler_list):
        handler_name = handler.__name__
        if handler not in handler_list:
            dprint(f"    Appending: {handler_name}")
            handler_list.append(handler)
        else:
            dprint(f"    Found existing: {handler_name}")

    add_once(on_render_complete, bpy.app.handlers.render_complete)
    add_once(on_render_cancel, bpy.app.handlers.render_cancel)
    add_once(on_bake_complete, bpy.app.handlers.render_complete)
    add_once(on_bake_cancel, bpy.app.handlers.render_cancel)


def register():
    """
    Register addon except if Blender run in CLI with background mode (-b).
    First the classes, then create an audio device to play sounds, then
    register handlers regularly and in load_post to prevent issues with old
    blend files.
    """

    if bpy.app.background:
        return

    bpy.utils.register_class(AudioNotifierAddonPreferences)
    bpy.utils.register_class(AudioNotifier_OT_PlaySound)

    prefs = bpy.context.preferences.addons.get(__package__).preferences
    if prefs:
        prefs.get_device()

    dprint("Registering AudioNotifier handlers:")
    register_handlers()
    if register_handlers not in bpy.app.handlers.load_post:
        dprint("Loadposting AudioNotifier handlers registration.")
        bpy.app.handlers.load_post.append(register_handlers)


def unregister():
    """
    Unregister Addon except if Blender run in CLI with background mode (-b).
    First the classes, then use a specific method to safely remove handlers:
    apparently some handlers don't get registered right away, causing errors.
    """

    if bpy.app.background:
        return

    bpy.utils.unregister_class(AudioNotifierAddonPreferences)
    bpy.utils.unregister_class(AudioNotifier_OT_PlaySound)

    def safe_remove(handler, handler_list):
        handler_name = handler.__name__
        if handler in handler_list:
            handler_list.remove(handler)
            dprint(f"    Removed: {handler_name}")
        else:
            dprint(f"    Handler not found in list: {handler_name}")

    dprint("Unregistering AudioNotifier handlers:")
    safe_remove(on_render_complete, bpy.app.handlers.render_complete)
    safe_remove(on_render_cancel, bpy.app.handlers.render_cancel)
    safe_remove(on_bake_complete, bpy.app.handlers.object_bake_complete)
    safe_remove(on_bake_cancel, bpy.app.handlers.object_bake_cancel)
    safe_remove(register_handlers, bpy.app.handlers.load_post)
