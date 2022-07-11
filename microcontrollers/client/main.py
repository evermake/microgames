from machine import Pin, ADC, WDT, PWM
import socket
import network
from time import sleep_ms
from events import JoystickPositionUpdatedEvent, encode_events    

host = '192.168.0.1'
port = 7777
server_address = (host, port)

Y_AXIS_PIN = 35
X_AXIS_PIN = 34
BUTTON_PIN = 32


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return  int(rightMin + (valueScaled * rightSpan))


class Joystick:
    def __init__(self, x_pin, y_pin, sw_pin):
        self._x_adc = ADC(Pin(x_pin, Pin.IN))
        self._y_adc = ADC(Pin(y_pin, Pin.IN))
        self._x_adc.width(ADC.WIDTH_12BIT)
        self._y_adc.width(ADC.WIDTH_12BIT)
        self._x_adc.atten(ADC.ATTN_11DB)
        self._y_adc.atten(ADC.ATTN_11DB)
        self._switch = Pin(sw_pin, Pin.IN, Pin.PULL_UP)

    def read(self): 
        x_value = translate(self._x_adc.read_u16(), 0, 65535, -100, 100)
        y_value = translate(self._y_adc.read_u16(), 0, 65535, -100, 100)
        return JoystickPositionUpdatedEvent(x_value, y_value, not bool(self._switch.value()))


pwm_led = PWM((Pin(4)))
pwm_led.freq(1000)

joystick = Joystick(X_AXIS_PIN, Y_AXIS_PIN, BUTTON_PIN)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.disconnect()
counter = True

while not wlan.isconnected():
    counter = not counter
    pwm_led.duty(counter * 1023)

    try:
        wlan.connect('microgrames-server-1', 'microgrames-top')
    except OSError:
        print('.', end='')
        sleep_ms(100)


print('\nConnected to:', wlan.config('essid'))
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while wlan.isconnected():
        pwm_led.duty(1023)
        sleep_ms(100)  
        event = joystick.read()
        events = encode_events([event])
        print(events)
        client_socket.sendto(events, server_address)
except KeyboardInterrupt:
    print("Bye!")
finally:
    print("Closing socket...")
    client_socket.close()

    print("Deactivating WLAN...")
    wlan.active(False)
