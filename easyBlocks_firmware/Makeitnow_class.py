from machine import Pin,RTC,PWM
import utime
import network
import ubluetooth
from micropython import const
from Makeitnow_function import mPrint
import sys
import select
import ujson
from neopixel import NeoPixel
from Makeitnow_fonts import bit_fonts
import ntptime

class NeoBitmap:
    def __init__(self, pin, width=5, height=5, spacing=1):
        self.np = NeoPixel(Pin(pin), width * height)
        self.width = width
        self.height = height
        self.spacing = spacing
        self.font = bit_fonts
        self.rainbow_index = 0 

    def display_char_at(self, char, start_pos, color=(30, 30, 30)):
        if char in self.font:
            for y in range(self.height):
                for x in range(self.width):
                    real_x = x + start_pos
                    if 0 <= real_x < self.width:
                        idx = y * self.width + real_x
                        if (self.font[char][y] >> (4-x)) & 1:
                            self.np[idx] = color
                        else:
                            self.np[idx] = (0, 0, 0)

    def display_message_slide(self, message, delay=0.5, color=(30, 30, 30)):
        if not isinstance(message, str):
            message = str(message)
        if len(message) == 1:
            self.clear()
            self.display_char_at(message, 0, color)  # 문자를 시작 위치에 표시
            self.np.write()
            return
        total_width = len(message) * (self.width + self.spacing)
        for pos in range(total_width):
            self.clear()
            for i, char in enumerate(message):
                start_pos = i * (self.width + self.spacing) - pos
                self.display_char_at(char, start_pos, color)
            self.np.write()
            utime.sleep(delay)

            
    def display_char(self, char, color=(30, 30, 30)):
        if not isinstance(char, str):
            char = str(char)
        if char in self.font:
            for y in range(self.height):
                for x in range(self.width):
                    idx = y * self.width + x
                    if (self.font[char][y] >> (4-x)) & 1:
                        self.np[idx] = color
                    else:
                        self.np[idx] = (0, 0, 0)
            self.np.write()
    
    def display_bitmap(self, *bitmap, color=(30, 30, 30)):
        for y, value in enumerate(bitmap):
            for x in range(self.width):
                idx = y * self.width + x
                if (value >> (4-x)) & 1:
                    self.np[idx] = color
                else:
                    self.np[idx] = (0, 0, 0)
        self.np.write()

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def adjust_brightness(self, color, brightness):
        return tuple(int(c * brightness / 100) for c in color)

    def display_colors(self, brightness, *colors):
        for idx, color in enumerate(colors):
            rgb = self.hex_to_rgb(color)
            adjusted_rgb = self.adjust_brightness(rgb, brightness)
            self.np[idx] = adjusted_rgb
        self.np.write()

    def clear(self):
        for i in range(self.width * self.height):
            self.np[i] = (0, 0, 0)
        self.np.write()
        
    def wave_effect(self, R, G, B, direction, delay=100, steps=12):
        color = (R, G, B)
        fade_amount = 9
        for step in range(steps):
            for i in range(self.width * self.height):
                col = i % self.width
                row = i // self.width
                is_active = (
                    (direction == 'r' and col == step) or
                    (direction == 'l' and col == self.width - 1 - step) or
                    (direction == 'u' and row == self.height - 1 - step) or
                    (direction == 'd' and row == step) or
                    (direction == 'h' and max(abs(col - (self.width // 2)), abs(row - (self.height // 2))) == step)
                )
                if is_active:
                    self.np[i] = color
                else:
                    current_color = self.np[i]
                    self.np[i] = tuple(max(0, c - fade_amount) for c in current_color)
            self.np.write()
            utime.sleep_ms(delay)
        self.clear()

    def rainbow_cycle(self, delay=1, brightness=20):
        for i in range(self.width * self.height):
            pixel_index = (i * 256 // (self.width * self.height)) + self.rainbow_index
            pos = pixel_index & 255
            if pos < 85:
                color = (255 - pos * 3, pos * 3, 0)
            elif pos < 170:
                pos -= 85
                color = (0, 255 - pos * 3, pos * 3)
            else:
                pos -= 170
                color = (pos * 3, 0, 255 - pos * 3)
            adjusted_color = self.adjust_brightness(color, brightness)
            self.np[i] = adjusted_color
        self.np.write()
        utime.sleep_us(delay)
        self.rainbow_index = (self.rainbow_index + 1) % 256 
    

class SerialHandler:
    def __init__(self):
        pass

    def available(self):
        return bool(select.select([sys.stdin], [], [], 0)[0])

    def read(self):
        if self.available():
            data_from_web = sys.stdin.readline().strip()
            try:
                json_data = ujson.loads(data_from_web)
                if json_data["status"] == "success":
                    if json_data["type"] == "data":
                        return json_data["data"]
                        
                else:
                    raise Exception(f"Status 에러 : {json_data['status']}")
                    return None
                
            except ValueError:
                return None
            except KeyError as e:
                raise Exception( "Json데이터에 키가 없습니다.",f"{e}")
                return None
        return None

        
class WiFiConnection:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        if not self.wlan.isconnected():
            self.wlan.active(True)
            mPrint('Connecting to Wi-Fi...')
            self.wlan.connect(self.ssid, self.password)
            
            start_time = utime.time()
            while not self.wlan.isconnected():
                if utime.time() - start_time > 5:
                    mPrint('Wi-Fi connection failed')
                    raise Exception('Wi-Fi연결실패 Wi-Fi를 확인해 주세요.')
                utime.sleep(0.5)

        mPrint('Wi-Fi connected:', self.wlan.ifconfig())
    
    def disconnect(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()
            mPrint('Wi-Fi disconnected')
            
    def get_wlan(self):
        return self.wlan
    
    def is_connected(self):
        return self.wlan.isconnected()
        

class BLE:
    _IRQ_CENTRAL_CONNECT = const(1)
    _IRQ_CENTRAL_DISCONNECT = const(2)
    _IRQ_GATTS_WRITE = const(3)
    
    def __init__(self, name, callback=None):
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self.ble_irq)
        self.callback = callback
        self.register_service()
        self.advertise()
        self.connected = False

    def ble_irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            self.connected = True
            self.ble.gap_advertise(0)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            self.connected = False
            self.advertise()
            
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            data = self.ble.gatts_read(value_handle)
            data = data.strip()
            data = data.decode()
            if self.callback:
                self.callback(data)

    def register_service(self):
        #NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        #RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        #TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
        NUS_UUID = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
        RX_UUID = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
        TX_UUID = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'

        
        NUS = ubluetooth.UUID(NUS_UUID)
        RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE,)
        TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY,)

        SERVICES = (NUS, (TX, RX,))
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services((SERVICES,))

    def advertise(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray(b'\x02\x01\x06') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        
    def send_data(self, data, newline=False):
        if self.is_connected():
            data_str = str(data)
            if newline:
                data_str += '\r\n'
            data_encoded = data_str.encode()
            self.ble.gatts_notify(0, self.tx, data_encoded)
        else:
            mPrint("Cannot send data: Not connected")

    def is_connected(self):
        return self.connected

class TimeManager:
    def __init__(self, time_difference):
        self.time_difference = time_difference
        self.wifi_flag = None
        self.update_time()
        self.manual_time_set_at = utime.mktime((2024, 01, 01, 12, 00, 00, 0, 0))

    def update_time(self):
        try:
            ntptime.settime()
        except:
            self.wifi_flag = 1
    
    def set_manual_time(self, year, month, day, hour, minute, second):
        self.manual_time_set_at = utime.time()
        self.manual_time = utime.mktime((year, month, day, hour, minute, second, 0, 0))
        
    def get_time(self, time_type):
        if self.wifi_flag == 1:
            elapsed = utime.time() - self.manual_time_set_at
            current_time = utime.localtime(self.manual_time + elapsed)
        else:
            current_time = utime.localtime()
        
        time_dict = {
            'Y': current_time[0],
            'M': current_time[1],
            'D': current_time[2],
            'h': (current_time[3] + self.time_difference) % 24,
            'm': current_time[4],
            's': current_time[5],
            'w': current_time[6],
            'j': current_time[7],
        }
        return time_dict.get(time_type, "Invalid time type")

class ADS1115:
    def __init__(self, i2c, address=0x48):
        self.i2c = i2c
        self.address = address
        self.write_register(0x01, 0x8583)  # 기본 설정값으로 리셋
        self.write_register(0x01, (self.read_register(0x01) & 0xFF7F) | 0x0100)  # 단일 변환 모드로 설정
        self.write_register(0x01, (self.read_register(0x01) & 0xFF1F) | (0b100 << 5))  # 데이터 속도 128 SPS 설정
        self.write_register(0x01, (self.read_register(0x01) & 0xF1FF) | (0b001 << 9))  # ±4.096V 범위 설정

    def read_register(self, reg):
        self.i2c.writeto(self.address, bytearray([reg]))
        result = self.i2c.readfrom(self.address, 2)
        return (result[0] << 8) | result[1]

    def write_register(self, reg, value):
        self.i2c.writeto(self.address, bytearray([reg, (value >> 8) & 0xFF, value & 0xFF]))

    def read_channel(self, channel, raw=False):
        mux_dict = {0: 0b100, 1: 0b101, 2: 0b110, 3: 0b111}
        if channel in mux_dict:
            config = self.read_register(0x01)
            config = (config & 0x8FFF) | (mux_dict[channel] << 12)
            self.write_register(0x01, config)
        
        config = self.read_register(0x01)
        config |= 0x8000  # 단일 변환 시작 비트를 설정
        self.write_register(0x01, config)

        while True:
            utime.sleep_ms(1) 
            status = self.read_register(0x01)
            if (status & 0x8000) != 0:  # 변환 완료 확인
                break

        result = self.read_register(0x00)  # 변환 결과 읽기
        if result & 0x8000:  # 2의 보수 처리
            result -= 1 << 16

        if raw:
            return result >> 2
        else:
            voltage = result * 4.096 / 32768.0
            return voltage

class Motor:
    def __init__(self, pin_pwm_positive, pin_pwm_negative, direction=False, pwm_freq=500):
        self.pwm_positive = PWM(Pin(pin_pwm_positive), freq=pwm_freq)
        self.pwm_negative = PWM(Pin(pin_pwm_negative), freq=pwm_freq)
        self.pwm_positive.duty(0)
        self.pwm_negative.duty(0)
        self.direction = direction

    def set_speed(self, speed):
        speed = max(-100, min(100, speed))
        if self.direction:
            duty_cycle = int(abs(speed) * 10.23)
            r_duty_cycle = 0
        else:
            duty_cycle = 0
            r_duty_cycle = int(abs(speed) * 10.23)
        
        if speed >= 0:
            self.pwm_positive.duty(duty_cycle)
            self.pwm_negative.duty(r_duty_cycle)
        else:
            self.pwm_positive.duty(r_duty_cycle)
            self.pwm_negative.duty(duty_cycle)