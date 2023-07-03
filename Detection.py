from Modules import SH1106
from PIL import Image, ImageDraw, ImageFont
from twilio.rest import Client

oled = SH1106.SH1106()
account_sid = 'ACcf4e51fcfaa85057d3b67882af8fdbd4'
auth_token = '050793697db4f538c71c2488e1b1f85b'
client = Client(account_sid, auth_token)

class Detection:

    def Detect(self, mode):
        image2 = Image.new('1', (oled.width, oled.height), "BLACK")
        draw = ImageDraw.Draw(image2)
        image3 = Image.new('1', (oled.width, oled.height), "BLACK")
        draw1 = ImageDraw.Draw(image3)
        x = 0
        font = ImageFont.truetype('Font.ttc', 10)
        font1 = ImageFont.truetype('Font.ttc', 13)

        while True:
            attributes = ['bme280', 'light', 'sgp', 'uv']  # 属性列表

            # 检查并获取属性值
            attribute_values = []
            for attribute in attributes:
                value = getattr(mode, attribute, None)
                attribute_values.append(value)

            # 检查属性是否全部为None
            if all(value is None for value in attribute_values):
                continue

            # 读取属性值
            bme280 = attribute_values[0]
            light = attribute_values[1]
            sgp = attribute_values[2]
            uv = attribute_values[3]

            # 获取数据
            bme = bme280.readData() if bme280 else None
            pressure = round(bme[0], 2) if bme else None
            temp = round(bme[1], 2) if bme else None
            hum = round(bme[2], 2) if bme else None
            lux = round(light.Lux(), 2) if light else None
            gas = round(sgp.raw(), 2) if sgp else None
            uvdata = uv.UVS() if uv else None

            draw.rectangle((0, 0, 128, 64), fill=0)

            if pressure is not None: #压力
                draw.text((0, 0), str(pressure), font=font, fill=1)
                draw.text((40, 0), 'hPa', font=font, fill=1)

            if temp is not None: #温度
                draw.text((0, 15), str(temp), font=font, fill=1)
                draw.text((40, 15), 'C', font=font, fill=1)

            if hum is not None: #湿度
                draw.text((0, 30), str(hum), font=font, fill=1)
                draw.text((40, 30), '%RH', font=font, fill=1)

            if lux is not None: #光强
                draw.text((0, 45), str(lux), font=font, fill=1)
                draw.text((40, 45), 'Lux', font=font, fill=1)
                if lux > 10:  # 当 lux 超过 10 时终止程序
                    print("Lux exceeds 100.Alarm and  Program terminated.")
                    draw1.text((10, 15), 'Alarm', font=font1, fill=1)
                    draw1.text((10, 35), 'GAS!!!', font=font1, fill=1)
                    oled.display(image3)
                    message = client.messages.create(
                            from_='+447445997296',
                            body='Security check please',
                            to='+447536356640')

                    return

            if uvdata is not None: #紫外线
                draw.text((65, 0), str(uvdata), font=font, fill=1)
                draw.text((105, 0), 'UV', font=font, fill=1)

            if gas is not None: #有害气体
                draw.text((65, 30), str(gas), font=font, fill=1)
                draw.text((105, 30), 'GAS', font=font, fill=1)

            oled.display(image2)


