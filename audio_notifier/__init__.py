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
        if not os.path.isfile(file_path):
            dprint(f"Audio file nout found: {file_path}")
            return {'CANCELLED'}

        try:
            sound = aud.Sound(file_path).loop(prefs.audio_repeat)
            device.volume = prefs.audio_volume
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
        default=False
    )
    audio_volume: bpy.props.FloatProperty(
        name="Volume of audio notifications",
        description="Default: 1. Can be set higher by typing a value.",
        default=1.0,
        min=0.0,
        soft_max=1.0,
        subtype='FACTOR'
    )
    audio_repeat: bpy.props.IntProperty(
        name="How many time is the notification played in a row",
        description=(
            "Default: 0 (played once). Can be set higher than 4 by"
            + "typing a value."
        ),
        default=0,
        min=0,
        soft_max=4,
    )

    def get_device(self):
        """Ensure a single audio device is used throughout the session."""
        if self.device is None:
            self.device = aud.Device()
        return self.device

    def draw(self, context):
        """Draw"""
        layout = self.layout

        layout.label(text="Audio Settings")
        layout.use_property_split = True

        row = layout.row(align=True)
        row.prop(self, "audio_volume", text="Volume")
        row = layout.row(align=True)
        row.prop(self, "audio_repeat", text="Repeat")

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

        row = layout.row(align=True)
        row.label(text="")
        row.label(
            text=(
                "Default sounds provided by IENBA under CC0 License on"
                + " freesound.org"
            )
        )

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
    if prefs.enable_render_sound:
        dprint("  found audio file, playing...")
        bpy.ops.audio_notifier.play_sound(sound_type="success")
    else:
        dprint("  couldn't find sound file!")


def on_render_cancel(scene):
    """Handler Render Cancel"""
    dprint("Render Cancel Handler detected")
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.enable_render_sound:
        dprint("  found audio file, playing...")
        bpy.ops.audio_notifier.play_sound(sound_type="cancel")
    else:
        dprint("  couldn't find sound file!")


def on_bake_complete(scene):
    """Handler Bake Complete"""
    dprint("Bake Complete Handler detected")
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.enable_bake_sound:
        dprint("  found audio file, playing...")
        bpy.ops.audio_notifier.play_sound(sound_type="success")
    else:
        dprint("  couldn't find sound file!")


def on_bake_cancel(scene):
    """Handler Bake Cancel"""
    dprint("Bake Cancel Handler detected")
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.enable_bake_sound:
        dprint("  found audio file, playing...")
        bpy.ops.audio_notifier.play_sound(sound_type="cancel")
    else:
        dprint("  couldn't find sound file!")


HANDLERS = [
    (on_render_complete, bpy.app.handlers.render_complete),
    (on_render_cancel, bpy.app.handlers.render_cancel),
    (on_bake_complete, bpy.app.handlers.object_bake_complete),
    (on_bake_cancel, bpy.app.handlers.object_bake_cancel),
]


def register_handlers(dummy=None):
    """Remove old handlers and append fresh ones from HANDLERS"""
    if bpy.app.background:
        return

    for func, handler_list in HANDLERS:
        func_name = func.__name__
        for existing in list(handler_list):
            if getattr(existing, "__name__", None) == func_name:
                handler_list.remove(existing)
                dprint(f"    Removed:{func_name}")
        handler_list.append(func)
        dprint(f"    Registered: {func_name}")

    # Handle self load_post registration of this here function
    self_name = register_handlers.__name__
    for existing in list(bpy.app.handlers.load_post):
        if getattr(existing, "__name__", None) == self_name:
            bpy.app.handlers.load_post.remove(existing)
            dprint(f"    Removed from load_post: {self_name}")
    bpy.app.handlers.load_post.append(register_handlers)
    dprint(f"    Registered from load_post: {self_name}")


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


def unregister():
    """
    Unregister Addon except if Blender run in CLI with background mode (-b).
    First the classes, then use a specific method to safely remove handlers:
    apparently some handlers don't get registered right away, causing errors.
    """

    if bpy.app.background:
        return

    dprint("Unregistering AudioNotifier handlers:")

    for func, handler_list in HANDLERS:
        func_name = func.__name__
        for existing in list(handler_list):
            if getattr(existing, "__name__", None) == func_name:
                handler_list.remove(existing)
                dprint(f"    Removed: {func_name}")
                break
        else:
            dprint(f"    Handler not found in list: {func_name}")

    # Remove the load_post entry for register_handlers
    self_name = register_handlers.__name__
    for existing in list(bpy.app.handlers.load_post):
        if getattr(existing, "__name__", None) == self_name:
            bpy.app.handlers.load_post.remove(existing)
            dprint(f"    Removed from load_post: {self_name}")
            break
    else:
        dprint("    skipping register_handlers: not found in load_post")

    dprint("Unregistering AudioNotifier classes.")
    bpy.utils.unregister_class(AudioNotifierAddonPreferences)
    bpy.utils.unregister_class(AudioNotifier_OT_PlaySound)
