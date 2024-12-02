<h1 tabindex="-1" class="heading-element" dir="auto">
    <a target="_blank" rel="noopener noreferrer" href="Prez/icon.jpg">
        <img src="Prez/icon.png" alt="icon" style="height: 1em; vertical-align: middle;">
    </a>
    Audio Notifier
</h1>

[![GitHub license](https://img.shields.io/github/license/L0Lock/AudioNotifier?style=for-the-badge)](https://github.com/L0Lock/AudioNotifier/blob/master/LICENSE) ![Latest Supported Blender Version](https://img.shields.io/badge/Blender-v4.3.0-orange?style=for-the-badge&logo=blender) [![ko-fi](Prez/SupportOnKofi.jpg)](https://ko-fi.com/lauloque)

-----

Gives Blender audio notifications for success, cancel and warning events. Shipped with default sound files under [Creative Commons 0](http://creativecommons.org/publicdomain/zero/1.0/ "Go to the full license text") license.

Notifies of the success or cancellation of renders and baking processes.

Provides a unified operator reusable for other addons developers to send audio notifications.

## Use in your addon

### Check before calling

Before calling the operator, it is safer to first check whether  the Audio Notifier extension is enabled to avoid errors:

```python
if context.preferences.addons.find("audio_notifier") == -1:
    # run the operator
```

You can even propose enabling it if you have a GUI. This is what I did in my other addon [convertRotationMode](https://github.com/L0Lock/convertRotationMode/tree/main?tab=readme-ov-file#not-so-simple-method) (feel free to dig the source code to see how it is implemented in the [AddonPreferences](https://github.com/L0Lock/convertRotationMode/blob/main/convert_Rotation_Mode/preferences.py)).

```python
if context.preferences.addons.find("audio_notifier") == -1:
    row = layout.row(align=False)
    row.alignment = 'CENTER'
    row.label(text="This addon requires the addon 'Audio Notifier' by Loïc \"Lauloque\" Dautry.", icon="ERROR")
    row = layout.row(align=False)
    row.alignment = 'CENTER'
    row.operator("preferences.addon_enable").module="audio_notifier"
```

### The operator

Call the operator `bpy.ops.audio_notifier.play_sound()` with the sound_type parameter:

- `sound_type` (str) – Specifies which sound to play. Can be one of the following:
  - `"cancel"` – Plays the cancel sound.
  - `"success"` – Plays the success sound.
  - `"warning"` – Plays the warning sound.

More sound types might come in the future.

### **Example Usage:**

To play a "success" sound after an event:

```python
# Call the operator with the 'success' sound type
bpy.ops.audio_notifier.play_sound(sound_type="success")
```

**Using with Handlers:**

You can also integrate the sound notifications into your event handlers. For example,  after rendering is completed:

```python
def on_render_complete(scene):
    bpy.ops.audio_notifier.play_sound(sound_type="success")

# Don't forget to Register and unregister the handler!
bpy.app.handlers.render_complete.append(on_render_complete)
```

### **Blender's Available Handlers:**

See the current list of available bpy handlers here: [Application Handlers (bpy.app.handlers) - Blender Python API](https://docs.blender.org/api/current/bpy.app.handlers.html)
