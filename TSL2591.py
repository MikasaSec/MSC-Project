#环境光
#sudo python3 TSL2591.py
import sys
import time
import math
import smbus
import RPi.GPIO as GPIO

ADDR                = (0x29)
COMMAND_BIT         = (0xA0)
ENABLE_REGISTER     = (0x00)
ENABLE_POWERON      = (0x01)
ENABLE_POWEROFF     = (0x00)
ENABLE_AEN          = (0x02)
ENABLE_AIEN         = (0x10)
ENABLE_SAI          = (0x40)
ENABLE_NPIEN        = (0x80)
CONTROL_REGISTER    = (0x01)
SRESET              = (0x80)
AILTL_REGISTER      = (0x04)
AILTH_REGISTER      = (0x05)
AIHTL_REGISTER      = (0x06)
AIHTH_REGISTER      = (0x07)
NPAILTL_REGISTER    = (0x08)
NPAILTH_REGISTER    = (0x09)
NPAIHTL_REGISTER    = (0x0A)
NPAIHTH_REGISTER    = (0x0B)
PERSIST_REGISTER    = (0x0C)
ID_REGISTER         = (0x12)
STATUS_REGISTER     = (0x13)
CHAN0_LOW           = (0x14)
CHAN0_HIGH          = (0x15)
CHAN1_LOW           = (0x16)
CHAN1_HIGH          = (0x17)
LUX_DF = 408.0
LUX_COEFB = 1.64
LUX_COEFC = 0.59
LUX_COEFD = 0.86
LOW_AGAIN           = (0X00)
MEDIUM_AGAIN        = (0X10)
HIGH_AGAIN          = (0X20)
MAX_AGAIN           = (0x30)
ATIME_100MS         = (0x00)
ATIME_200MS         = (0x01)
ATIME_300MS         = (0x02)
ATIME_400MS         = (0x03)
ATIME_500MS         = (0x04)
ATIME_600MS         = (0x05)
MAX_COUNT_100MS     = (36863)
MAX_COUNT           = (65535)
INI_PIN = 23

class TSL2591:
	def __init__(self, address=ADDR):
		self.i2c = smbus.SMBus(1)
		self.address = address

		# 初始化GPIO设置，设置使用的引脚模式和警告
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(INI_PIN, GPIO.IN)

		self.ID = self.Read_Byte(ID_REGISTER)
		if(self.ID != 0x50):
			print("ID = 0x%x"%self.ID)
			sys.exit()

		#初始化TSL2591传感器的设置
		self.Write_Byte(ENABLE_REGISTER, ENABLE_AIEN | ENABLE_POWERON | ENABLE_AEN | ENABLE_NPIEN)
		self.IntegralTime = ATIME_200MS
		self.Gain = MEDIUM_AGAIN
		self.Write_Byte(CONTROL_REGISTER, self.IntegralTime | self.Gain)
		self.Write_Byte(PERSIST_REGISTER, 0x01)

		#将原始计数转换为光照强度
		atime = 100.0 * self.IntegralTime + 100.0
		again = 1.0
		if self.Gain == MEDIUM_AGAIN:
			again = 25.0
		elif self.Gain == HIGH_AGAIN:
			again = 428.0
		elif self.Gain == MAX_AGAIN:
			again = 9876.0
		self.Cpl = (atime * again) / LUX_DF

	def Read_Byte(self, Addr):
		Addr = (COMMAND_BIT | Addr) & 0xFF
		return self.i2c.read_byte_data(self.address, Addr)
	#从指定地址读取单个字节的数据

	def Write_Byte(self, Addr, val):
		Addr = (COMMAND_BIT | Addr) & 0xFF
		self.i2c.write_byte_data(self.address, Addr, val & 0xFF)
	#向指定地址写入单个字节的数据

	def Read_2Channel(self):
		CH0L = self.Read_Byte(CHAN0_LOW)
		CH0H = self.Read_Byte(CHAN0_LOW + 1)
		CH1L = self.Read_Byte(CHAN0_LOW + 2)
		CH1H = self.Read_Byte(CHAN0_LOW + 3)
		#读取通道0和通道1的低字节（CH0L和CH1L）和高字节（CH0H和CH1H）的数
		full = (CH0H << 8)|CH0L
		ir = (CH1H << 8)|CH1L
		return full,ir#将完整的通道0的数据值（full）和通道1的数据值（ir）作为元组返回
	#用于读取两个通道的数据值

	def Lux(self):
		status = self.Read_Byte(0x13) #调用Read_Byte()方法读取0x13地址的数据，保存在变量status中
		if(status & 0x10): #判断状态寄存器中的特定位是否被设置
			self.Write_Byte(0xE7, 0x13)
		full, ir = self.Read_2Channel()
		if full == 0xFFFF or ir == 0xFFFF: #如果其中任一通道的数据值为0xFFFF（表示数据溢出），则抛出运行时错误
			raise RuntimeError('Numerical overflow!')
		lux = ((full-ir) * (1.00 - (ir/full))) / self.Cpl #光照传感器的计算公式，使用数据值计算光照强度（Lux）
		return lux
	#计算光照强度（Lux）

	def SET_LuxInterrupt(self, SET_LOW, SET_HIGH):
		full, ir = self.Read_2Channel()
		set0dataL = int(SET_LOW * self.Cpl + ir)
		set0dataH = int(SET_HIGH * self.Cpl + ir)

		self.Write_Byte(AILTL_REGISTER, set0dataL & 0xFF)
		self.Write_Byte(AILTH_REGISTER, set0dataL >> 8)

		self.Write_Byte(AIHTL_REGISTER, set0dataH & 0xFF)
		self.Write_Byte(AIHTH_REGISTER, set0dataH >> 8)
	#根据给定的低阈值和高阈值，计算对应的光照强度值，并将结果写入相应的寄存器中，用于设置光照强度中断的阈值


if __name__ == '__main__':
	sensor = TSL2591()
	sensor.SET_LuxInterrupt(20, 200)
	time.sleep(1)
	try:
		while True:
			lux = sensor.Lux()
			print("Lux: %d" %lux)
			time.sleep(0.5)

	except KeyboardInterrupt:
		exit()
#在当前脚本被直接执行时才会执行这个代码块