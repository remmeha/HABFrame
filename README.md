
# HABFrame 
An openHAB control panel / photoframe. Based on a webserver. Build with python and flask. 

[![](https://img.shields.io/badge/python-3.5%2B-green.svg)]()
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)

I wrote this python Flask app first of all to learn more about python and webserver programming, including html, js, and css. Also I wanted to create an openHAB control panel which functions as a digital photoframe. Check out the end result if you are interested.

Features:
- Web-based openHAB control panel
- Configurable with a custom sitemap configuration
- Remotely turn on and off screen
- Can be used as a digital photoframe or clock even without openHAB
- Receive messages or toast popups
- Widget templates for main page and popups (Music and Weather, with the possibility to create more)


## Installation

### Clone the repo
```shell
$ git clone https://github.com/remmeha/HABFrame.git
$ git submodule init
$ git submodule update
```

### Install requirements

```shell
$ pip3 install -r requirements.txt
```

Make sure you have the following installed:


### Run with Python

Python 3.5+ is supported and tested.

```shell
$ python3.5 HABframe.py
```

### Open your webbrowser
Open http://localhost:8890 and enjoy. :smiley:

:point_down:Screenshots (more in examples/screenshots):

<p align="left">
  <img src="https://raw.githubusercontent.com/remmeha/HABFrame/master/examples/screenshots/Screenshot_1.png" width="800px" alt="">
</p>
<p align="left">
  <img src="https://raw.githubusercontent.com/remmeha/HABFrame/master/examples/screenshots/Screenshot_2.png" width="800px" alt="">
</p>
<p align="left">
  <img src="https://raw.githubusercontent.com/remmeha/HABFrame/master/examples/screenshots/Screenshot_3.png" width="800px" alt="">
</p>
<p align="left">
  <img src="https://raw.githubusercontent.com/remmeha/HABFrame/master/examples/screenshots/Screenshot_5.png" width="800px" alt="">
</p>
<p align="left">
  <img src="https://raw.githubusercontent.com/remmeha/HABFrame/master/examples/screenshots/Screenshot_7.png" width="800px" alt="">
</p>

## Configuration

Copy and edit the configuration file

```shell
$ cp config/settings_example.xml config/settings.xml
```

| Settings      | Description                                  |
|---------------|----------------------------------------------|
| <b>main	        | <i>main settings                                |
| name          | General frame name                           |
| hostname      | Either hostname of IP-address of server      |
| port	        | Port on which server should start            |
| openhab_ip    | openHAB server IP-address		       |
| openhab_port  | openHAB server port			       |
| sitemap       | openHAB sitemap                              |
| resize_icons  | resize icons (helps with some web browsers)  |
| habpanel_link | Add a link on the frontpage to the HABPanel  |
| enable_screen_control | 'off': Do not turn off screen <br> 'black': Turn screen black <br>  'url': call an url to turn on and off the screen <br>  'cmd': run a command to turn on and off the screen |
| screen_on_url | url to turn on screen (see enable_screen_control) |
| screen_off_url | url to turn off screen (see enable_screen_control) |
| screen_on_cmd | command to turn on screen (see enable_screen_control) |
| screen_off_cmd | command to turn off screen (see enable_screen_control) |
| enable_clock | Enable the use of a clock as screensaver when screen is on (0: disabled, 1: enabled) |
| enable_album | Enable the use of an album as screensaver when screen is on (0: disabled, 1: enabled) |
| <b>WUNDERGROUND | <i>Wunderground settings for when wunderground widgets are used |
| apikey | Wunderground api key |
| updateperiod | Weather data refresh time [minutes] |
| language     | Language for weather information |
| location     | Weather location (name or zmw location) |
| <b>LOGGING   | <i>logging settings |
| log          | log file |
| errorlog     | error log file |
| eventlog     | event log file |
| level        | error, warn, info, debug, trace |
| ALBUM        | album settings for when album functionality is enabled |
| image_size   | resize image to fit screen WxH (eg. 800x480) |
| random_picture_url | url to retreive random image <br> for example: https://picsum.photos/800/480/?image=42 |
| picture_info_url | optional: Display a line of information about the picture within the frame |
| <b>DATA | |
| location | location to store data file |
| <b>PAGE | |
| event_check_reload | how often to check for new events, like messages or toasts [seconds] |
| page_reload | how often to reload the openhab data on a page [seconds] |

## openHAB sitemap

The openHAB sitemap needs to have a specific configuration. See the *.sitemap files in the example directory.

### Main

Text labels are used to create sections for the configuration specific for the HABFrame.

| Label name | Functionality |
|------|--------|
| items_left | The section with this label contains items displayed on the left of the main page |
| items_right | The section with this label contains items displayed on the right of the main page |
| b_{label} | labels starting with 'b_' in the main frame are displayed as menu button on the bottom of the main page. The sitemap sections contain the items in this menu |

### Widgets
The sections 'items_left' and 'items_right' can contain subsection (Frame {}) which are read and displayed as widgets in HABFrame. The items in these section contain the data needed in the widgets (named with the item label)

| Frame label name | Description |
|------------------|-------------|
| m_{name} | Frame label starting with 'm_' will be displayed as a large menu button, the items in this section are displayed in the menu |
| a_{name} | Same as 'm_', but now the menu is a popup |
| s_media | Displays media widget, using 3/5 rows on the frontpage |
| c_media | Large button with media widget popup |
| s_weather | Weather widget. 4 /5 rows used on frontpage |
| s_weather_wg | Weather widget with data from Wunderground, see main configuration |
| s_weather_small | Small weather widget |
| s_weather_small_wg | Small weather widget with data from wunderground |

### Sub menu's
See examples. Use for a submenu. Only 1 level of submenus supported

### Supported items

| Item type | Comment |
|-----------|---------|
| Switch    | Switch on / off |
| Selection | Use mappings for a list of possibilities <br> A mapping with one entry creates a push button |
| Text      | Creates a button without action, to only show information | 
| Slider    | A slider popup |
| Chart     | Creates a button with a chart popup. Note: Only rrd4j is supported as data source |

## Messages
send a message
```url
http://localhost:8890/message/new?sender=sender&subject=subject&message="this is a message"
```
send a toast popup message
```url
http://localhost:8890/message/toast?sender=sender&message="this is a toast message"
```

## Settings
### Settings page

TBD

### Remote control
Screen on and off
| ON  | Screensaver show either clock or photoframe |
| OFF | Screen is turned off when screensaver is activated |

```url
http://localhost:8890/state/photoframe/screen/on
http://localhost:8890/state/photoframe/screen/off
```

Select Photoframe or clock as screensaver
```url
http://localhost:8890/state/photoframe/frame/clock
http://localhost:8890/state/photoframe/frame/album
```

Trigger deactivation screensaver
```url
http://localhost:8890/state/photoframe/trigger
```

## Tips & Tricks

Use [Fully Kios Browser](https://www.ozerov.de/fully-kiosk-browser/) on a tablet or phone. You can enable or disable the screensaver with this app remotely using the screen_on/off_cmd setting.

Screen control with a raspberry pi:
```shell
$ echo 1 > /sys/class/backlight/rpi_backlight/bl_power
$ echo 0 > /sys/class/backlight/rpi_backlight/bl_power
```

