import machine
from machine import I2C, SoftI2C, PWM, Pin, ADC, DAC, Timer
from Makeitnow_class import WiFiConnection, BLE, TimeManager, SerialHandler, NeoBitmap
from Makeitnow_function import mPrint, map_value
import math
import _thread
import utime
import sys
from neopixel import NeoPixel
neoled23 = NeoPixel(Pin(23), 25)
neoled23.fill((0,0,0))
neoled23.write()
utime.sleep(0.5)

p2 = Pin(2, Pin.OUT)


while True:
    p2.value(1)
    utime.sleep(1)
    p2.value(0)
    utime.sleep(1)