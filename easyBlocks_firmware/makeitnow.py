import machine 
from machine import I2C, SoftI2C, PWM, Pin, ADC, DAC, Timer 
from Makeitnow_class import WiFiConnection, BLE, TimeManager, SerialHandler, NeoBitmap 
from Makeitnow_function import mPrint, map_value 
import math 
import _thread 
import utime 
import sys
import random
from neopixel import NeoPixel 
handler = SerialHandler() 
neoled23 = NeoPixel(Pin(23), 25) 
neoled23.fill((0,0,0)) 
neoled23.write() 
utime.sleep(0.1) 
import Makeitnow_sensor 
 
p35 = Pin(35, Pin.IN) 
 
pBUZZER = PWM(Pin(27),freq=1) 
pBUZZER.duty(0) 
 
p34 = Pin(34, Pin.IN) 
 
i2c = I2C(-1, scl=Pin(22), sda=Pin(21)) 
 
gyro = Makeitnow_sensor.LIS2DW12(i2c) 
 
veml6040 = Makeitnow_sensor.VEML6040(i2c) 
 
p2 = PWM(Pin(2),freq=500) 
p2.duty(0)

test_f=4

def generate_random_color():
    return (random.randint(30, 70), random.randint(30, 70), random.randint(30, 70))

def wave_effect(neopixel_strip, direction, delay=0.12, steps=12):
    global test_f
    color = generate_random_color()
    fade_amount = 9

    for step in range(steps):
        if p34.value():
                test_f = 0
                utime.sleep(0.3)
                break
        if gyro.detect_slant(direction) == 0: 
                break
        for i in range(25):
            # 현재 픽셀의 열과 행 계산
            col = i % 5
            row = i // 5
            
            # 방향에 따라 밝기 설정
            if ((direction == 'r' and col == step) or
                (direction == 'l' and col == 4 - step) or
                (direction == 'f' and row == 4 - step) or
                (direction == 'b' and row == step)or
                (direction == 'h' and max(abs(col - 2), abs(row - 2)) == step)):
                neopixel_strip[i] = color
            else:
                # 이전 색상을 어둡게 처리
                current_color = neopixel_strip[i]
                neopixel_strip[i] = tuple(max(0, c - fade_amount) for c in current_color)

        neopixel_strip.write()
        utime.sleep(delay)

    neopixel_strip.fill((0, 0, 0))
    neopixel_strip.write()
    
notes = [262, 294, 330, 349, 392, 440, 494]
sheet = [0,0,4,4,5,5,4,3,3,2,2,1,1,0]
note_index = 0

def timer_tick1(timer):
    global notes, sheet, note_index
    if p35.value():
        pBUZZER.freq(notes[sheet[note_index]]) 
        pBUZZER.duty(512) 
        while p35.value():
            utime.sleep(0.15)
        pBUZZER.duty(0)
        note_index += 1
        if note_index >= len(sheet):
            note_index = 0
timer1 = Timer(1)
timer1.init(period=100, mode=Timer.PERIODIC, callback=timer_tick1)
    
    
while True:
    if p34.value():
        test_f = (test_f + 1)%5
        utime.sleep(0.3)
        
    if test_f == 0:
        neoled23.fill((30,0,0))
        neoled23.write()
    elif test_f == 1:
        neoled23.fill((0,30,0))
        neoled23.write()
    elif test_f == 2:
        neoled23.fill((0,0,30))
        neoled23.write()
    elif test_f == 3:
        neoled23.fill((30,30,30))
        neoled23.write()
        
    elif test_f == 4:
        if gyro.detect_slant('t'): 
            neoled23.fill((0,0,0)) 
            neoled23.write()
        elif gyro.detect_slant('h'): 
            wave_effect(neoled23, 'h')
            neoled23.write() 
        elif gyro.detect_slant('l'): 
            wave_effect(neoled23, 'l')
            neoled23.write() 
        elif gyro.detect_slant('r'): 
            wave_effect(neoled23, 'r')
            neoled23.write() 
        elif gyro.detect_slant('f'): 
            wave_effect(neoled23, 'f')
            neoled23.write() 
        elif gyro.detect_slant('b'): 
            wave_effect(neoled23, 'b')
            neoled23.write()
        
    if (veml6040.read_color('w')) < 150: 
        p2.duty(50) 
    else: 
        p2.duty(0) 
 

