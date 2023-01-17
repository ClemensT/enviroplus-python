#!/usr/bin/env python3

import time
from pms5003 import PMS5003, ReadTimeoutError
import logging
import json
import requests

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
    while True:
        try:
            readings = pms5003.read()
            data = Pm()
            data.p_1_0 = int(readings.pm_ug_per_m3(1.0))
            data.p_2_5 = int(readings.pm_ug_per_m3(2.5))
            data.pa_1_0 = int(readings.pm_ug_per_m3(1.0, True))
            data.pa_2_5 = int(readings.pm_ug_per_m3(2.5, True))
            data.p_10 = int(readings.pm_ug_per_m3(10.0))

            r = requests.post(url = URL, data = data.__dict__)

            print("works", json.dumps(data.__dict__))
            print(readings)
            #logging.info(readings)
            time.sleep(30.0)

        except ReadTimeoutError:
            pms5003 = PMS5003()
except KeyboardInterrupt:
    pass
