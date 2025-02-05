/*****************************************************************************
* | File      	:   Readme_EN.txt
* | Author      :   Waveshare team
* | Function    :   Help with use
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2020-08-28
* | Info        :   Here is an English version of the documentation for your quick use.
******************************************************************************/
This file is to help you use this routine.
Since our OLED screens are getting more and more, it is not convenient for our maintenance, so all the OLED screen programs are made into one project.
A brief description of the use of this project is here:

1. Basic information:
This routine is based on the raspberry PI 4B+ development, the kernel version:
	Linux raspberrypi 5.4.51-v7l+ #1333 SMP Mon Aug 10 16:51:40 BST 2020 armv7l GNU/Linux
You can view the corresponding test routines in the examples\ of the project;

2. Pin connection:
Pin connections can be viewed in \lib\waveshare_OLED\config.py and will be repeated here:
SPI:
	OLED   =>    RPI(BCM)
	VCC    ->    3.3
	GND    ->    GND
	DIN    ->    10(MOSI)
	CLK    ->    11(SCLK)
	CS     ->    8
	DC     ->    25
	RST    ->    27

IIC:
	OLED   =>    RPI(BCM)
	VCC    ->    3.3
	GND    ->    GND
	DIN    ->    2(SDA)
	CLK    ->    3(SCL)
	CS     ->    8
	DC     ->    25
	RST    ->    27

3.Installation library
    sudo apt-get update
    sudo apt-get install python-pip
    sudo apt-get install python-pil
    sudo apt-get install python-numpy
    sudo pip install RPi.GPIO

or

    sudo apt-get update
    sudo apt-get install python3-pip
    sudo apt-get install python3-pil
    sudo apt-get install python3-numpy
    sudo pip3 install RPi.GPIO

4. Basic use:
Since this project is a comprehensive project, you may need to read the following for use:
You can view the test program in the examples\ directory.
Please note which OLED you purchased.
eg 1:
    if you bought 1.3inch OLED Module (C)，you should type：
		sudo python OLED_1in3_c_test.py
	or
		sudo python3 OLED_1in3_c_test.py
eg 2:
    if you bought 1.5inch RGB OLED Module，you should type：
		sudo python OLED_1in5_rgb_test.py
	or
		sudo python3 OLED_1in5_rgb_test.py
    
