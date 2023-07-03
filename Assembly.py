from Modules import BME280, LTR390, MPU9255, SGP40, TSL2591, SH1106
from PIL import Image,ImageDraw,ImageFont
import time

oled = SH1106.SH1106()
image3 = Image.new('1', (oled.width, oled.height), "BLACK")  # 创建了一个新的图像对象，用于在 OLED 显示屏上进行绘图操作
draw = ImageDraw.Draw(image3)
x = 0
font = ImageFont.truetype('Font.ttc', 11)  # 使用了字体文件 Font.ttc，并指定字体大小为10

class Assembly:
    @staticmethod
    def Assemble(x):
        if x == 0:  # Public Indoor
            assembly = IndoorAssembly()
        elif x == 1:  # Public Outdoor
            assembly = OutdoorAssembly()
        else:
            raise ValueError("Invalid value for 'x'")

        return assembly.create_object()


class IndoorAssembly:
    def create_object(self):
        mpu9255 = MPU9255.MPU9255()
        bme280 = BME280.BME280()
        bme280.get_calib_param()
        light = TSL2591.TSL2591()
        sgp = SGP40.SGP40()
        for _ in range(20):
            time.sleep(0.2)
            draw.rectangle((0, 0, 128, 64), fill=0)
            draw.text((5, 30), 'Indoor-Private Mode', font=font, fill=1)
            oled.display(image3)
        return IndoorObject(mpu9255, bme280, light, sgp)
class IndoorObject:
    def __init__(self, mpu9255, bme280, light, sgp):
        self.mpu9255 = mpu9255
        self.bme280 = bme280
        self.light = light
        self.sgp = sgp
        self.icm = self.mpu9255.getdata()

class OutdoorAssembly:
    def create_object(self):
        uv = LTR390.LTR390()
        bme280 = BME280.BME280()
        bme280.get_calib_param()
        for _ in range(20):
            time.sleep(0.2)
            draw.rectangle((0, 0, 128, 64), fill=0)
            draw.text((5, 30), 'Outdoor-Private Mode', font=font, fill=1)
            oled.display(image3)
        return OutdoorObject(bme280, uv)


class OutdoorObject:
    def __init__(self, bme280, uv):
        self.bme280 = bme280
        self.uv = uv

