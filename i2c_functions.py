import smbus
import time
import numpy as np

class SHT35(object):

    def __init__(self, address=0x45, bus=None):
        self.address = address

        # I2C bus
        self.bus = smbus.SMBus(bus)

    def read(self):
        # high repeatability, clock stretching disabled
        self.bus.write_i2c_block_data(self.address, 0x24, [0x00])

        # measurement duration < 16 ms
        time.sleep(0.016)

        # read 6 bytes back
        # Temp MSB, Temp LSB, Temp CRC, Humidity MSB, Humidity LSB, Humidity CRC
        data = self.bus.read_i2c_block_data(0x45, 0x00, 6)
        temperature = data[0] * 256 + data[1]
        celsius = -45 + (175 * temperature / 65535.0)
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
        return celsius, humidity


class TH02(object):
    def __init__(self, address=0x40, bus=None):
        self.address = address
        self.bus = smbus.SMBus(1)

    def read(self):
        self.bus.write_byte_data(self.address, 0x03, 0x11)
        time.sleep(.05)
        data = self.bus.read_i2c_block_data(0x40, 0x00, 3)
        cTemp = (((data[1] * 256 + (data[2] & 0xFC)) / 4.0) / 32.0 - 50.0)
        self.bus.write_byte_data(0x40, 0x03, 0x01)
        time.sleep(.05)
        data = self.bus.read_i2c_block_data(self.address, 0x00, 3)
        # Convert the data to 12-bits
        humidity = ((data[1] * 256 + (data[2] & 0xF0)) / 16.0) / 16.0 - 24.0
        humidity = humidity - (((humidity * humidity) * (-0.00393)) + (humidity * 0.4008) - 4.7844)
        humidity = humidity + (cTemp - 30) * (humidity * 0.00237 + 0.1973)
        return cTemp, humidity

class ADS7828(object):
    def __init__(self, address=0x48, bus=None):
        self.address = address
        self.bus = smbus.SMBus(bus)
    
    def read(self, channel):
        self.bus.write_byte(self.address, channel)
        time.sleep(.00003)
        
        array = []
        for i in range(10):
            data = self.bus.read_i2c_block_data(self.address, channel, 2)
            array.append((data[0] << 8) + (data[1]))
            time.sleep(.00003)
            
        return(np.mean(array))
    
    def temperature(self, thermistor):
        value = self.read(channel = thermistor)
        v_ref = 0.817
        v_in = 0.947
        resistor = 100000
        voltage = v_ref * value / 4095
        resistance = (voltage * resistor) / (v_in * (1 - voltage / v_in))
        temperature = 310.1 * pow(resistance / 1000, -0.1387) - 138.7
        return temperature
