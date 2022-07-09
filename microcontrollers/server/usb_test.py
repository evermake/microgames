from machine import Pin, UART
from time import sleep_ms
import os
import sys

STATUS_LED_PINT = 2
START_PROGRAM_BUTTON = 23
UART_BAUDRATE = 115200

# Start program only if start button is pressed.
start_button = Pin(START_PROGRAM_BUTTON, Pin.IN, Pin.PULL_UP)
if start_button.value() == 1:
    # Button is realeased => exit
    sys.exit(0)


os.dupterm(None)
uart = UART(1, tx=1, rx=3, baudrate=UART_BAUDRATE)

status_led = Pin(STATUS_LED_PINT, Pin.OUT)
status_led.value(1)

try:
    while True:
        data = uart.read()

        if data:
            status_led.value(0)
            sleep_ms(30)
            status_led.value(1)
            uart.write(data.decode('utf-8'))

        sleep_ms(50)
finally:
    status_led.value(0)
