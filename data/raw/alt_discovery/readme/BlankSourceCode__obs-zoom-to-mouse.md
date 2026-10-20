# OBS-Zoom-To-Mouse

An OBS lua script to zoom a display-capture source to focus on the mouse. 

I made this for my own use when recording videos as I wanted a way to zoom into my IDE when highlighting certain sections of code. My particular setup didn't seem to work very well with the existing zooming solutions so I created this.

Built with OBS v29.1.3

Now works on **Windows**, **Linux**, and **Mac**

Inspired by [tryptech](https://github.com/tryptech)'s [obs-zoom-and-follow](https://github.com/tryptech/obs-zoom-and-follow)

## Example
![Usage Demo](obs-zoom-to-mouse.gif)

## Install
1. Git clone the repo (or just save a copy of `obs-zoom-to-mouse.lua`)
1. Launch OBS
1. In OBS, add a `Display Capture` source (if you don't have one already)
1. In OBS, open Tools -> Scripts
1. In the Scripts window, press the `+` button to add a new script
1. Find and add the `obs-zoom-to-mouse.lua` script
1. For best results use the following settings on your `Display Capture` source
   * Transform:
      * Positional Alignment - `Top Left`
      * Bounding Box type -  `Scale to inner bounds`
      * Alignment in Bounding Box - `Top Left`
      * Crop - All **zeros**
   * If you want to crop the display, add a new Filter -> `Crop/Pad`
      * Relative - `False`
      * X - Amount to crop from left side
      * Y - Amount to crop form top side
      * Width - Full width of display minus the value of X + amount to crop from right side
      * Height - Full height of display minus the value of Y + amount to crop from bottom side
   
   **Note:** If you don't use this form of setup for your display source (E.g. you have bounding box set to `No bounds` or you have a `Crop` set on the transform), the script will attempt to **automatically change your settings** to zoom compatible ones. 
   This may have undesired effects on your layout (or just not work at all).

   **Note:** If you change your desktop display properties in Windows (such as moving a monitor, changing your primary display, updating the orientation of a display), you will need to re-add your display capture source in OBS for it to update the values that the script uses for its auto calculations. You will then need to reload the script.

## Usage
1. You can customize the following settings in the OBS Scripts window:
   * **Zoom Source**: The display capture in the current scene to use for zooming
   * **Zoom Factor**: How much to zoom in by
   * **Zoom Speed**: The speed of the zoom in/out animation
   * **Auto follow mouse**: True to track the cursor automatically while you are zoomed in, instead of waiting for the `Toggle follow` hotkey to be pressed first
   * **Follow outside bounds**: True to track the cursor even when it is outside the bounds of the source
   * **Follow Speed**: The speed at which the zoomed area will follow the mouse when tracking
   * **Follow Border**: The %distance from the edge of the source that will re-enable mouse tracking
   * **Lock Sensitivity**: How close the tracking needs to get before it locks into position and stops tracking until you enter the follow border
   * **Auto Lock on reverse direction**: Automatically stop tracking if you reverse the direction of the mouse.
   * **Show all sources**: True to allow selecting any source as the Zoom Source - Note: You **MUST** set manual source position for non-display capture sources
   * **Set manual source position**: True to override the calculated x/y (topleft position), width/height (size), and scaleX/scaleY (canvas scale factor) for the selected source. This is essentially the area of the desktop that the selected zoom source represents. Usually the script can calculate this, but if you are using a non-display capture source, or if the script gets it wrong, you can manually set the values.
   * **X**: The coordinate of the left most pixel of the source
   * **Y**: The coordinate of the top most pixel of the source
   * **Width**: The width of the source (in pixels)
   * **Height**: The height of the source (in pixels)
   * **Scale X**: The x scale factor to apply to the mouse position if the source is not 1:1 pixel size (normally left as 1, but useful for cloned sources that have been scaled)
   * **Scale Y**: The y scale factor to apply to the mouse position if the source is not 1:1 pixel size (normally left as 1, but useful for cloned sources that have been scaled)
   * **Monitor Width**: The width of the monitor that is showing the source (in pixels)
   * **Monitor Height**: The height of the monitor that is showing the source (in pixels)
   * **More Info**: Show this text in the script log
   * **Enable debug logging**: Show additional debug information in the script log

1. In OBS, open File -> Settings -> Hotkeys 
   * Add a hotkey for `Toggle zoom to mouse` to zoom in and out
   * Add a hotkey for `Toggle follow mouse during zoom` to turn mouse tracking on and off (*Optional*)

### Dual Machine Support
1. The script also has some **basic** dual machine setup support. By using my related project [obs-zoom-to-mouse-remote](https://github.com/BlankSourceCode/obs-zoom-to-mouse-remote) you will be able to track the mouse on your second machine
1. When you have [ljsocket.lua](https://github.com/BlankSourceCode/obs-zoom-to-mouse-remote) in the same directory as `obs-zoom-to-mouse.lua`, the following settings will also be available:
   * **Enable remote mouse listener**: True to start a UDP socket server that will listen for mouse position messages from a remote client
   * **Port**: The port number to use for the socket server
   * **Poll Delay**: The time between updating the mouse position (in milliseconds)
   * For more information see [obs-zoom-to-mouse-remote](https://github.com/BlankSourceCode/obs-zoom-to-mouse-remote)

### More information on how mouse tracking works
When you press the `Toggle zoom` hotkey the script will use the current mouse position as the center of the zoom. The script will then animate the width/height values of a crop/pan filter