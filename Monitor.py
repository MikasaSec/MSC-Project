#sudo python3 Monitor.py
import time
from Modules import MPU9255, SH1106
from PIL import Image,ImageDraw,ImageFont
import os

os.system('i2cdetect -y -r 1')
MPU9255 = MPU9255.MPU9255()
oled = SH1106.SH1106()


class Monitor:
    def __init__(self):
        last_icm0 = None
        while True:
            time.sleep(0.2)
            icm = []
            icm = MPU9255.getdata()
            if last_icm0 is not None and abs(icm[0] - last_icm0) > 2500:
                break
            last_icm0 = icm[0]  # 保存当前的 icm[0] 值


