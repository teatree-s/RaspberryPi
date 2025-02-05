/*****************************************************************************
* | File      	:   Readme_CN.txt
* | Author      :   Waveshare team
* | Function    :   Help with use
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2020-08-28
* | Info        :   在这里提供一个中文版本的使用文档，以便你的快速使用
******************************************************************************/
这个文件是帮助您使用本例程。
由于我们的OLED屏越来越多，不便于我们的维护，因此把所有的OLED程序做成一个工程。
在这里简略的描述本工程的使用：

1.基本信息：
本例程基于树莓派4B+开发的，内核版本
	Linux raspberrypi 5.4.51-v7l+ #1333 SMP Mon Aug 10 16:51:40 BST 2020 armv7l GNU/Linux
你可以在工程的examples\中查看对应的测试例程;

2.管脚连接：
管脚连接你可以在\lib\waveshare_OLED\config.py中查看，这里也再重述一次：
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

3.安装库：
    sudo apt-get update
    sudo apt-get install python-pip
    sudo apt-get install python-pil
    sudo apt-get install python-numpy
    sudo pip install RPi.GPIO

或

    sudo apt-get update
    sudo apt-get install python3-pip
    sudo apt-get install python3-pil
    sudo apt-get install python3-numpy
    sudo pip3 install RPi.GPIO

4.基本使用：
由于本工程是一个综合工程，对于使用而言，你可能需要阅读以下内容：
你可以在examples\目录中查看测试程序
请注意你购买的是哪一款的OLED。
栗子1：
    如果你购买的1.3inch OLED Module (C)，那么你应该执行命令：
		sudo python OLED_1in3_c_test.py
	或
		sudo python3 OLED_1in3_c_test.py
栗子2：
    如果你购买的1.5inch RGB OLED Module，那么你应该执行命令：
		sudo python OLED_1in5_rgb_test.py
	或
		sudo python3 OLED_1in5_rgb_test.py

