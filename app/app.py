#!/usr/bin/env python3
#!/usr/bin/env python3

import time
import colorsys
import sys
import ST7735
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
from enviroplus import gas
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont

import logging
import json
import requests
import numbers
import traceback
import threading

# 160 x 80
# Create ST7735 LCD display class
st7735 = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display
st7735.begin()

WIDTH = st7735.width
HEIGHT = st7735.height

# Set up canvas and font
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font_size = 20
fontM = ImageFont.truetype(UserFont, 18)
fontS = ImageFont.truetype(UserFont, 12)
lastMax = 0
displayOn = False

def display_text(message,x,y, font=fontM):
    draw.text((x, y), message, font=font, fill=(255, 255, 255))

def getMax(data):

    values = []
    if (isinstance(data.p_1_0, numbers.Number)):
        values.append(data.p_1_0)
    if (isinstance(data.p_2_5, numbers.Number)):
        values.append(data.p_2_5)
    if (isinstance(data.pa_1_0, numbers.Number)):
        values.append(data.pa_1_0)
    if (isinstance(data.pa_2_5, numbers.Number)):
        values.append(data.pa_2_5)
    if (isinstance(data.p_10, numbers.Number)):
        values.append(data.p_10)

    try:
        return max(values)
    except Exception:
        print(traceback.format_exc())
        # or
        print(sys.exc_info()[2])

        return 0

def drawArrow(x,y, up=False):
    width = 8
    height = 10
    if (up):
        draw.polygon([ (x-width,y), (x,y-height), (x+width, y)], (255,0,0))
    else:
        draw.polygon([ (x-width,y), (x,y+height), (x+width, y)], (255,255,255))

def displayAirQuality(data):

    maxV = getMax(data)

    x = WIDTH/2
    y = 50

    text_x = x + 4

    if (maxV < 15):
        draw.rectangle((x, y, WIDTH, HEIGHT), (0, 255, 0))
        draw.text((text_x, y+2), "good", font=fontM, fill=(255, 255, 255))
    elif (maxV < 20):
        draw.rectangle((x, y, WIDTH, HEIGHT), (0, 255, 255))
        draw.text((text_x, y+2), "medium", font=fontM, fill=(255, 255, 255))
    else:
        draw.rectangle((x, y, WIDTH, HEIGHT), (255, 0, 0))
        draw.text((text_x, y+2), "bad", font=fontM, fill=(255, 255, 255))

URL = "http://192.168.178.20:1880/enviro"


class Pm:
    p_1_0 = 0
    p_2_5 = 0
    pa_1_0 = 0
    pa_2_5 = 0
    p_10 = 0


logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""particulates.py - Print readings from the PMS5003 particulate sensor.

Press Ctrl+C to exit!

""")

pms5003 = PMS5003()
time.sleep(1.0)

try:
    uiCycleInit = 30
    inputCycleInit = 1

    inputCycle = inputCycleInit
    uiCycle = uiCycleInit
    maxV = 0

    while True:
        
        if (uiCycle > 0):
            uiCycle -= 1
        else:
            uiCycle = uiCycleInit
            try:
                draw.rectangle((0, 0, WIDTH, HEIGHT), (0, 0, 0))

                readings = pms5003.read()
                data = Pm()
                data.p_1_0 = int(readings.pm_ug_per_m3(1.0))
                data.p_2_5 = int(readings.pm_ug_per_m3(2.5))
                data.pa_1_0 = int(readings.pm_ug_per_m3(1.0, True))
                data.pa_2_5 = int(readings.pm_ug_per_m3(2.5, True))
                data.p_10 = int(readings.pm_ug_per_m3(10.0))

                maxV = getMax(data)

    
                display_text("p 1   : %i" % (data.p_1_0), 0,10)
                display_text("p 2.5 : %i" % (data.p_2_5), 0,30)
                display_text("pa 1.0: %i" % (data.pa_1_0), 0,50)
                display_text("pa 2.5: %i" % (data.pa_2_5), 80,10)
                display_text("p 10  : %i" % (data.p_10), 80,30)
                displayAirQuality(data)
        
                if (maxV > lastMax):
                    drawArrow(145,65, True)
                else:
                    drawArrow(145,65, False)
                    
                print("max %i"  % maxV)

                lastMax = maxV

                st7735.display(img)

                r = requests.post(url = URL, data = data.__dict__)

                print("works", json.dumps(data.__dict__))
                print(readings)

            except pmsReadTimeoutError:
                pms5003 = PMS5003()

        if (inputCycle > 0):
            inputCycle -= 1
        else:

            try:
                inputCycle = inputCycleInit
                prox = ltr559.get_proximity()

                if (prox > 2000):
                    displayOn = not displayOn
                    uiCycle = 0 
                st7735.set_backlight(displayOn)
            except:
                print("proxmity error")
            
        if (maxV > 20):
            st7735.set_backlight(True)


        time.sleep(1)
        
except KeyboardInterrupt:
    pass
