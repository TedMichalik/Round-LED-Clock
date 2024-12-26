# Wi-Fi Connected Round-LED-Clock with Raspberry Pi Zero W
 
 ### Schema for the RPi Zero W
 
 Connect GPIO3 and Ground (pins 5 and 9) to a momentary contact push button switch.  
 Connect 5 volts (pin 2) to 5 volt on the LED strip with old USB cable.  
 Connect Ground (pin 6) to Ground on the LED strip with old USB cable.  
 Connect MOSI (pin 19) to the Data line on the LED strip with old USB cable.  
 
 ### Parts list (just Google on the name to find a link where to buy)

| Components                              	    |
| -------------                          	    |
| Raspberry Pi Zero W  			            |
| LED strip WS2812B 60 RGB LED's 1 meter            |
| Black PLA filament                           	    |
| White PLA filament                           	    |
| 5 Volt power adapter with Micro USB cable         |
| Old USB cable                                     |
| Momentary contact push button switch and wire     |


### YouTube video

<a href="https://youtu.be/Z4b4v84smpg" target="_blank"><img src="https://img.youtube.com/vi/Z4b4v84smpg/0.jpg" 
alt="Click to view: LED Clock" width="500" border="1" /></a>


### Raspberry Pi Zero W Setup

Use Raspberry Pi Imager to burn Raspberry Pi OS Lite for the Raspberry Pi Zero W on an SD card. Name it clock with user clock. Set up the WiFi SSID and password. Enable SSH.

Boot the Raspberry Pi and find its IP address from the router. SSH into the Raspberry Pi and change to root.

Images for other Raspberry Pi boards are installed, but not needed by the Raspberry Pi Zero W. Remove them with this command:
```
apt --autoremove remove linux-image-*-{v7,v7l,v8}
```

Add these lines to /boot/firmware/config.txt
```
dtparam=spi=on
dtoverlay=gpio-shutdown
```

Add these lines to /etc/modules
```
spi_bcm2835
spidev
```

Update to the latest software:
```
apt update
apt full-upgrade
apt install git
apt autoremove
```

Run raspi-config and set the correct language for your locale.

Then reboot
```
reboot
```

SSH back into the Raspberry Pi as user clock. Clone the clock program and go to the folder for the Raspberry Pi.
```
git clone https://github.com/TedMichalik/Round-LED-Clock.git
cd Round-LED-Clock/RPi/
```

Create a virtual environment for the python program and install needed libraries.
```
python -m venv ws2812
source ws2812/bin/activate
pip install rpi_ws281x
pip install adafruit-circuitpython-neopixel
```

Check that the program works.
```
python Round-LED-Clock.py -c
```

Add a service to start on boot.
```
sudo cp roundledclock.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable roundledclock.service
```

Check that the push button can shutdown and restart the clock.


The 3D printed enclosure for the Raspberry Pi Zero W was obtained here:

Rasperry Pi Zero headless case - roomy  
by imhavoc on Thingiverse:  
https://www.thingiverse.com/thing:4861097
