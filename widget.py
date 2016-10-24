import machine
from machine import I2C, Pin
import ssd1306
import neopixel
import time

i2c = I2C(sda=Pin(0), scl=Pin(2))
display = ssd1306.SSD1306_I2C(64, i2c, 0x3c, False)
np = neopixel.NeoPixel(machine.Pin(4), 1)
button1 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
button2 = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
button3 = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
buzzer = machine.PWM(machine.Pin(5))

def oled_clear():    
    display.fill(0)
    display.show()

def oled_wipe(x0, y0, x1, y1):
    for x in range(x0, x1):
        for y in range(y0, y1):
            display.pixel(x, y, 0)

def oled_text(text, x = 0, y = 0):
    oled_wipe(x, y, x + (len(text) * 8), y + 8)
    display.text(text, x, y)
    display.show()

def oled_line(x0, y0, x1, y1):
    display.line((x0, y0), (x1, y1))
    display.show()
    
def oled_circle(x0, y0, radius):
    display.circle(x0, y0, radius)
    display.show()

def oled_graphic(pic, origin_x = 0, origin_y = 0):
    for y, row in enumerate(pic):
        for x, col in enumerate(row):
            if col == "1":
                display.pixel(origin_x + x, origin_y + y, 1)
            else:
                display.pixel(origin_x + x, origin_y + y, 0)
    display.show()

def pixel_color(red, green, blue):
    np[0] = (red, green, blue)
    np.write()

def button_pressed(pin):
    if pin.value() == 0:
        active = 0
        while pin.value() == 0 and active < 75:
            active += 1
            time.sleep_ms(1)
        if pin.value() == 0 and active >= 75:
            buzzer_play(1000, 128, 50)
            return True
        else:
            return False
    else:
        return False
    
def button1_pressed():
    return button_pressed(button1)

def button2_pressed():
    return button_pressed(button2)

def button3_pressed():
    return button_pressed(button3)

def buzzer_play(freq, duty, duration):
    buzzer.freq(freq)
    buzzer.duty(duty)
    time.sleep_ms(duration)
    buzzer.deinit()
