#运动传感器  sudo python3 MPU9255.py
import sys
import time
import math
import smbus
import RPi.GPIO as GPIO

ADDR = (0x68)
PWR_M = 0x6B
DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
INT_EN = 0x38
ACCEL_X = 0x3B
ACCEL_Y = 0x3D
ACCEL_Z = 0x3F
GYRO_X = 0x43
GYRO_Y = 0x45
GYRO_Z = 0x47
TEMP = 0x41
MAG_X = 0x03
MAG_Y = 0x05
MAG_Z = 0x07
ST_1 = 0x02
ST_2 = 0x09
MAG_ADDRESS = 0x0C
MPU9255_REG_ID = 0x75
MPU9255_ID = 0x71

class MPU9255:
	def __init__(self, address=ADDR):
		self.bus = smbus.SMBus(1)
		self.address = address
		self.ID = self.Read_Byte(MPU9255_REG_ID)
		if (self.ID != MPU9255_ID):
			print("ID = 0x%x" % self.ID)
			sys.exit()

		self.Write_Byte(PWR_M, 0x01)
		self.Write_Byte(DIV, 0x07)
		self.Write_Byte(CONFIG, 0)
		self.Write_Byte(GYRO_CONFIG, 0x18)
		self.Write_Byte(INT_EN, 0x01)
		self.Write_Byte(0x37, 0x02)
		self.Write_Byte(0x36, 0x01)

		self.bus.write_byte_data(MAG_ADDRESS, 0x0A, 0x00)
		time.sleep(0.05)
		self.bus.write_byte_data(MAG_ADDRESS, 0x0A, 0x0F)
		time.sleep(0.05)
		self.bus.write_byte_data(MAG_ADDRESS, 0x0A, 0x00)
		time.sleep(0.05)
		self.bus.write_byte_data(MAG_ADDRESS, 0x0A, 0x06)
		time.sleep(0.1)
	#初始化

	def Read_Byte(self, Addr):
		return self.bus.read_byte_data(self.address, Addr)
	# 读取LTR390传感器上指定寄存器地址 cmd 的值

	def Write_Byte(self, Addr, val):
		self.bus.write_byte_data(self.address, Addr, val)
	# 向LTR390传感器上指定寄存器地址 cmd 写入一个字节的值 val

	def Read_Word(self, addr):
		high = self.Read_Byte(addr)#读取指定地址 addr 的高位字节值
		low = self.Read_Byte(addr + 1)#读取指定地址 addr + 1 的低位字节值。
		value = ((high << 8) | low)#将高位字节和低位字节进行合并，构成一个完整的字
		if (value > 32768):#如果读取的值超过了有符号整数的最大正值（32767），则将其转换为有符号整数的负值
			value = value - 65536
		return value
	# 从指定地址读取一个字（16位）的数据。

	def accel(self):
		x = self.Read_Word(ACCEL_X)
		y = self.Read_Word(ACCEL_Y)
		z = self.Read_Word(ACCEL_Z)
		Buf = [x, y, z]
		return Buf
	#用于获取加速度传感器的数据

	def gyro(self):
		x = self.Read_Word(GYRO_X)
		y = self.Read_Word(GYRO_Y)
		z = self.Read_Word(GYRO_Z)
		Buf = [x, y, z]
		return Buf
	#获取陀螺仪传感器的数据

	def mag(self):
		self.bus.read_byte_data(MAG_ADDRESS, ST_1)

		xh = self.bus.read_byte_data(MAG_ADDRESS, MAG_X)
		xl = self.bus.read_byte_data(MAG_ADDRESS, MAG_X + 1)
		x = ((xh << 8) | xl)
		yh = self.bus.read_byte_data(MAG_ADDRESS, MAG_Y)
		yl = self.bus.read_byte_data(MAG_ADDRESS, MAG_Y + 1)
		y = ((yh << 8) | yl)
		zh = self.bus.read_byte_data(MAG_ADDRESS, MAG_Z)
		zl = self.bus.read_byte_data(MAG_ADDRESS, MAG_Z + 1)
		z = ((zh << 8) | zl)

		self.bus.read_byte_data(MAG_ADDRESS, ST_2)
		Buf = [x, y, z]
		return Buf
	#用于获取磁力计传感器的数据

	def getdata(self):
		Accel = self.accel()
		Gyro = self.gyro()
		Mag = self.mag()
		return [Accel[0], Accel[1], Accel[2], Gyro[0], Gyro[1], Gyro[2], Mag[0], Mag[1], Mag[2]]
	#获取 MPU9255 的加速度、陀螺仪和磁力计数据


if __name__ == '__main__':
	sensor = MPU9255()
	icm = []
	try:
		while True:
			time.sleep(0.5)
			icm = sensor.getdata()
			print("/-------------------------------------------------------------/")
			#print("Roll = %.2f , Pitch = %.2f , Yaw = %.2f" %(icm[0],icm[1],icm[2]))
			print("Acceleration: X = %d, Y = %d, Z = %d" % (icm[0], icm[1], icm[2]))
			print("Gyroscope:     X = %d , Y = %d , Z = %d" % (icm[3], icm[4], icm[5]))
			print("Magnetic:      X = %d , Y = %d , Z = %d" % (icm[6], icm[7], icm[8]))
	except KeyboardInterrupt:
		print("KeyboardInterrupt")
		# sensor.Disable()
		exit()
#在当前脚本被直接执行时才会执行这个代码块