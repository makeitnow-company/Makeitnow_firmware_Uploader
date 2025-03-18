import machine
from machine import SoftI2C, PWM, Pin, ADC, DAC, Timer
from Makeitnow_class import WiFiConnection, BLE, TimeManager, SerialHandler
from Makeitnow_function import mPrint, map_value
import math
import _thread
import utime
import sys

p2 = Pin(2, Pin.OUT)


while True:
    p2.value(1)
    utime.sleep(1)
    p2.value(0)
    utime.sleep(1)