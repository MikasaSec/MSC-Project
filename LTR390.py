#紫外传感器
#sudo python3 LTR390.py
import time
import math
import smbus

ADDR  = (0X53)

LTR390_MAIN_CTRL = (0x00)  # Main control register
LTR390_MEAS_RATE = (0x04)  # Resolution and data rate
LTR390_GAIN = (0x05)  # ALS and UVS gain range
LTR390_PART_ID = (0x06)  # Part id/revision register
LTR390_MAIN_STATUS = (0x07)  # Main status register
LTR390_ALSDATA = (0x0D)  # ALS data lowest byte, 3 byte
LTR390_UVSDATA = (0x10)  # UVS data lowest byte, 3 byte
LTR390_INT_CFG = (0x19)  # Interrupt configuration
LTR390_INT_PST = (0x1A)  # Interrupt persistance config
LTR390_THRESH_UP = (0x21)  # Upper threshold, low byte, 3 byte
LTR390_THRESH_LOW = (0x24)  # Lower threshold, low byte, 3 byte

#ALS/UVS measurement resolution, Gain setting, measurement rate
RESOLUTION_20BIT_TIME400MS = (0X00)
RESOLUTION_19BIT_TIME200MS = (0X10)
RESOLUTION_18BIT_TIME100MS = (0X20)#default
RESOLUTION_17BIT_TIME50MS  = (0x3)
RESOLUTION_16BIT_TIME25MS  = (0x40)
RESOLUTION_13BIT_TIME12_5MS  = (0x50)
RATE_25MS = (0x0)
RATE_50MS = (0x1)
RATE_100MS = (0x2)# default
RATE_200MS = (0x3)
RATE_500MS = (0x4)
RATE_1000MS = (0x5)
RATE_2000MS = (0x6)

# measurement Gain Range.
GAIN_1  = (0x0)
GAIN_3  = (0x1)# default
GAIN_6 = (0x2)
GAIN_9 = (0x3)
GAIN_18 = (0x4)


class LTR390:
	def __init__(self, address=ADDR):
		self.i2c = smbus.SMBus(1)#创建了一个SMBus对象，用于与I2C总线通信
		self.address = address

		self.ID = self.Read_Byte(LTR390_PART_ID)

		if(self.ID != 0xB2):
			print("ID有问题傻逼")
			return

		self.Write_Byte(LTR390_MAIN_CTRL, 0x0A) #  设置为激活模式
		self.Write_Byte(LTR390_MEAS_RATE, RESOLUTION_20BIT_TIME400MS | RATE_2000MS) #  设置传感器的分辨率为20位，并设置测量速率为2000毫秒
		self.Write_Byte(LTR390_GAIN, GAIN_3) #  设置传感器的增益范围为3
	#初始化LTR390传感器对象


	def Read_Byte(self, cmd):
		return self.i2c.read_byte_data(self.address, cmd)
	#读取LTR390传感器上指定寄存器地址 cmd 的值

	def Write_Byte(self, cmd, val):
		self.i2c.write_byte_data(self.address ,cmd, val)
	#向LTR390传感器上指定寄存器地址 cmd 写入一个字节的值 val

	def UVS(self):
		Data1 = self.Read_Byte(LTR390_UVSDATA)
		Data2 = self.Read_Byte(LTR390_UVSDATA + 1)
		Data3 = self.Read_Byte(LTR390_UVSDATA + 2)
		uv =  (Data3 << 16)| (Data2 << 8) | Data1 #将三个字节的数据 Data1、Data2 和 Data3 组合成一个 24 位的整数 uv
		return uv
	#定义了一个名为 UVS 的方法，在test中被调用，用于获取LTR390传感器测量到的紫外线强度值

if __name__ == '__main__':
	sensor = LTR390()
	time.sleep(1)
	try:
		while True:
			UVS = sensor.UVS()
			print("UVS: %d" %UVS)
			time.sleep(0.5)

	except KeyboardInterrupt:
		# sensor.Disable()
		exit()
#在当前脚本被直接执行时才会执行这个代码块。






