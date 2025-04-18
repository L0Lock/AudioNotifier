[![GitHub license](https://img.shields.io/github/license/L0Lock/AudioNotifier?style=for-the-badge&labelColor=rgb(64,64,64))](https://github.com/L0Lock/AudioNotifier/blob/master/LICENSE) ![Minimum Blender Version](https://img.shields.io/badge/Blender-4.2LTS-green?style=for-the-badge&logo=blender&logoColor=white&labelColor=rgb(64,64,64)) [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/H2H818FHX)

-----

![feature](Prez/feature.jpg)

- Gives Blender audio notifications for success, cancel and warning events. Shipped with default [sound files](https://freesound.org/s/762132/) under [CC 0](http://creativecommons.org/publicdomain/zero/1.0/) license. Credits to [IENBA](https://freesound.org/people/IENBA/).
- Out of the box notifies of the success or cancellation of renders and baking processes.

## Usage

![prefs](Prez/prefs.jpg)

In the addon's preferences, you can chose :

- Audio Volume
- Add repetitions
- Use a custom sound file for each notification.  
    Pressing [[&#10229; Backspace]] while hovering a path or using [[Right 🖱️]] > Reset To Default Value will reset it to using the default sound file provided with the addon.  
- Toggle on/off the render and baking events notifications if you don't want one of them to occur. Render events optionally can add notification for each frame of an animation render (the success sound will be half the volume and double the pitch)
- Enable Developer prints (visible in the console using the menu Window > Toggle System Console). This will print a lot of messages in the console, it's useful for developers or bug reports. It can be quite verbose and impact performance, so **use only when needed!**

## Installation

You can download the extension either from:

- Blender's GUI (Preferences > Get Extensions)
- The [Blender Extension Platform](https://extensions.blender.org/add-ons/audio-notifier/) (still in approval queue)
- [This repository's releases page](https://github.com/L0Lock/AudioNotifier/releases).

The installation process is well explained by Blender's official extensions platform documentation:

[About — Blender Extensions](https://extensions.blender.org/about/)
