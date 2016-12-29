The config in this directory is targeted LIRC 0.9.4 and may be incompatible to
earlier version.

Wire IR LED and receiver properly and connect to GPIO on Raspberry Pi 3.

Add this line to /boot/config.txt:

  dtoverlay=lirc-rpi,gpio_out_pin=22,gpio_in_pin=23,gpio_in_pull=down
