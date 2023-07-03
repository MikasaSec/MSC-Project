#温湿度传感器
#sudo python3 BME280.py
import smbus
import time

I2C_ADDR = 0x76
digT = []
digP = []
digH = []
t_fine = 0.0

class BME280:
	def __init__(self, address = I2C_ADDR):
		self.i2c = smbus.SMBus(1)
		self.address = address
		
		self.calib = []
		self.osrs_t = 1
		self.osrs_p = 1
		self.osrs_h = 1
		self.mode   = 3
		self.t_sb   = 5
		self.filter = 0
		self.spi3w_en = 0

		ctrl_meas_reg = (self.osrs_t << 5) | (self.osrs_p << 2) | self.mode
		config_reg    = (self.t_sb << 5) | (self.filter << 2) | self.spi3w_en
		ctrl_hum_reg  = self.osrs_h

		self.writeReg(0xF2, ctrl_hum_reg)
		self.writeReg(0xF4, ctrl_meas_reg)
		self.writeReg(0xF5, config_reg)
	#初始方法 初始化 BME280 传感器的通信接口、地址和配置参数，确保传感器处于正确的工作状态，并准备好读取温度、压力和湿度数据

	def writeReg(self, reg_address, data):
		self.i2c.write_byte_data(self.address ,reg_address,data)
	#向BME280传感器的寄存器写入数据

	def get_calib_param(self):
		for i in range (0x88,0x88+24):
			self.calib.append(self.i2c.read_byte_data(self.address, i))
		self.calib.append(self.i2c.read_byte_data(self.address, 0xA1))
		for i in range (0xE1,0xE1+7):
			self.calib.append(self.i2c.read_byte_data(self.address, i))

		digT.append((self.calib[1] << 8) | self.calib[0])
		digT.append((self.calib[3] << 8) | self.calib[2])
		digT.append((self.calib[5] << 8) | self.calib[4])
		digP.append((self.calib[7] << 8) | self.calib[6])
		digP.append((self.calib[9] << 8) | self.calib[8])
		digP.append((self.calib[11]<< 8) | self.calib[10])
		digP.append((self.calib[13]<< 8) | self.calib[12])
		digP.append((self.calib[15]<< 8) | self.calib[14])
		digP.append((self.calib[17]<< 8) | self.calib[16])
		digP.append((self.calib[19]<< 8) | self.calib[18])
		digP.append((self.calib[21]<< 8) | self.calib[20])
		digP.append((self.calib[23]<< 8) | self.calib[22])
		digH.append( self.calib[24] )
		digH.append((self.calib[26]<< 8) | self.calib[25])
		digH.append( self.calib[27] )
		digH.append((self.calib[28]<< 4) | (0x0F & self.calib[29]))
		digH.append((self.calib[30]<< 4) | ((self.calib[29] >> 4) & 0x0F))
		digH.append( self.calib[31] )
		
		for i in range(1,2):
			if digT[i] & 0x8000:
				digT[i] = (-digT[i] ^ 0xFFFF) + 1

		for i in range(1,8):
			if digP[i] & 0x8000:
				digP[i] = (-digP[i] ^ 0xFFFF) + 1

		for i in range(0,6):
			if digH[i] & 0x8000:
				digH[i] = (-digH[i] ^ 0xFFFF) + 1
	#获取BME280传感器的校准参数

	def readData(self):
		data = []
		for i in range (0xF7, 0xF7+8):
			data.append(self.i2c.read_byte_data(self.address, i))
		pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)#左移 12 位。将 data[0] 中的数据移至正确的位置，以在压力的原始值中占据相应的位
		temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
		hum_raw  = (data[6] << 8)  |  data[7]
		
		pressure = self.compensate_P(pres_raw)
		temperature = self.compensate_T(temp_raw)
		var_h = self.compensate_H(hum_raw)
		return [pressure, temperature, var_h]
	#读取传感器的原始数据，并进行数据补偿计算，最终返回经过补偿后的压力、温度和湿度数据

	def compensate_P(self, adc_P):
		global  t_fine
		pressure = 0.0
		
		v1 = (t_fine / 2.0) - 64000.0
		v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * digP[5]
		v2 = v2 + ((v1 * digP[4]) * 2.0)
		v2 = (v2 / 4.0) + (digP[3] * 65536.0)
		v1 = (((digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8)  + ((digP[1] * v1) / 2.0)) / 262144
		v1 = ((32768 + v1) * digP[0]) / 32768
		
		if v1 == 0:
			return 0
		pressure = ((1048576 - adc_P) - (v2 / 4096)) * 3125
		if pressure < 0x80000000:
			pressure = (pressure * 2.0) / v1
		else:
			pressure = (pressure / v1) * 2
		v1 = (digP[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
		v2 = ((pressure / 4.0) * digP[7]) / 8192.0
		pressure = pressure + ((v1 + v2 + digP[6]) / 16.0)  
		return (pressure/100) #
	#补偿压力值，压力值以hPa（百帕）为单位返回

	def compensate_T(self, adc_T):
		global t_fine
		v1 = (adc_T / 16384.0 - digT[0] / 1024.0) * digT[1]
		v2 = (adc_T / 131072.0 - digT[0] / 8192.0) * (adc_T / 131072.0 - digT[0] / 8192.0) * digT[2]
		t_fine = v1 + v2
		temperature = t_fine / 5120.0
		return temperature
	#补偿温度值，温度值以摄氏度（℃）为单位返回

	def compensate_H(self, adc_H):
		global t_fine
		var_h = t_fine - 76800.0
		if var_h != 0:
			var_h = (adc_H - (digH[3] * 64.0 + digH[4]/16384.0 * var_h)) * (digH[1] / 65536.0 * (1.0 + digH[5] / 67108864.0 * var_h * (1.0 + digH[2] / 67108864.0 * var_h)))
		else:
			return 0
		var_h = var_h * (1.0 - digH[0] * var_h / 524288.0)
		if var_h > 100.0:
			var_h = 100.0
		elif var_h < 0.0:
			var_h = 0.0
		# print "hum : %6.2f ％" % (var_h)
		return var_h
	#补偿湿度值，湿度值以百分比（%）为单位返回


if __name__ == '__main__':
	sensor = BME280()
	sensor.get_calib_param()
	time.sleep(1)#调用 get_calib_param 方法获取校准参数，然后暂停 1 秒
	try:
		data = []
		data = sensor.readData() #调用BME280对象的readData()方法，从传感器中读取压力、温度和湿度数据，并将数据存储在data列表
		print("pressure : %7.2f hPa" %data[0])
		print("temp : %-6.2f ℃" %data[1])
		print("hum : %6.2f ％" %data[2])
	except KeyboardInterrupt:#如果在执行过程中检测到键盘中断（用户按下Ctrl+C），则执行pass语句，忽略异常，程序退出
		pass
#在当前脚本被直接执行时才会执行这个代码块。