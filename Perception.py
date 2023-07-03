#sudo python3 Perception.py
import time
from Modules import LTR390, SH1106
from PIL import Image,ImageDraw,ImageFont
import os

os.system('i2cdetect -y -r 1')

class Perception:
    def locationDetect(self):
        oled = SH1106.SH1106()
        uv = LTR390.LTR390()

        image1 = Image.new('1', (oled.width, oled.height), "BLACK")
        draw = ImageDraw.Draw(image1)
        font = ImageFont.truetype('Font.ttc', 11)

        for _ in range(20):
            time.sleep(0.2)
            draw.rectangle((0, 0, 128, 64), fill=0)
            uvdata = uv.UVS()
            draw.text((5, 20), str("Deployment environment"), font=font, fill=1)
            draw.text((5, 40), str("Percepting..."), font=font, fill=1)
            oled.display(image1)
            if uvdata > 5:
                break

        loc = 1 if uvdata > 5 else 0
        return loc

