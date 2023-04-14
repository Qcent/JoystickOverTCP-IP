# JoystickOverTCP-IP
A Client/Server application for transmitting joystick controlls over any network.
Add net play to any two-player game or console emulator when used in conjunction with video stream / screenshare.

# Notes
This application requires that the host/server computer have [vJoy](https://github.com/shauleiz/vJoy) installed.
 
This application communicates on port 5000 (can be changed easily in source code), if computers are behind a firewall and/or router this port most likely will need to be opened and forwarded.
 
Compiled executables in /dist folder are win64

# Seting up vJoy
To run this application the Host/Server must install [vJoy](https://github.com/shauleiz/vJoy) to emulate a native game controller. It will use the first vJoy device slot without altering the python script.
The application is currently configured to reproduce the buttons, axes and d-hat of an XBox controller (PlayStation DualShock via [DS4Windows](https://ds4-windows.com/)). vJoy must be configured to support 6 axes, 11 buttons and 1 four direction POV hat switch (as shown below).

![Example vJoy Configuration](images/vJoyConfig.png)

# How to use joyServer
If running from script you will require the python libraries: pyvjoy, socket, ast, urllib.request, time, argparse.

Once run, a message will indicate that you are awaiting a connection and the program will display your local and outward facing IP addresses. The Client will need to enter your address into their application. When the Client successfully establishes a connection you will see an onscreen notification.

With command line arguments you can specify which port to listen on and if you want to display latency info. \
eg.
```
 joyServer1.1 -p 6800    # runs joyServer on port 6800
 joyServer1.1 -l         # runs joyServer on default port 5000 with connection latency shown in window
```

![joyServer Output](images/serverSide.png)

# How to use joyClient
If running from script you will require the python libraries: pygame, socket, ipaddress, time, argparse.

This app uses your primary game controller by default. To select your input device, run with command line option -s. Once run you will be required to enter the address of the host/server. If you then receive a "Connected!" message you should be good to go.

Command line arguments available:
```
 -p 6800              # run on port 6800
 -n 196.x.x.x         # automatically attempts to connect to supplied network address
 -f 30                # fps set to 30, program will attempt to communicate with the server 30 times per second
 -s                   # when -s flag is included, a prompt to select from attached joysticks will be displayed
 -l                   # when -l flag is included, latency will be output to window
```

![joyClient Output](images/clientSide.png)
