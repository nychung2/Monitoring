import sys
import smbus
import time
import os
import datetime as dt
import numpy as np
from termcolor import colored

import i2c_functions as sensor

# This functions returns all the data for the following.
def collect_data(sht35_a, sht35_b, am2302, adc):
    timestamp = str(dt.datetime.now())

    # Region One
    try:
        sht1 = sht35_a.read()
    except:
        sht1 = [-99, -99]
    
    # Region Two
    try:
        sht2 = sht35_b.read()
        am_sens = am2302.read()
    except:
        sht2 = [-99, -99]
        am_sens = [-99, -99]

    # Surface Temperature and Current Sensing
    try:
        # Addresses for each port
        t1 = 0xB4
        t2 = 0x31
        t3 = 0xD4
        t4 = 0xE4
        p1 = 0x94
        p2 = 0xA4
        adc_array = []
        adc_array.append(adc.temperature(thermistor = t1))
        adc_array.append(adc.temperature(thermistor = t2))
        adc_array.append(adc.temperature(thermistor = t3))
        adc_array.append(adc.temperature(thermistor = t4))
        adc_array.append(adc.current(input = p1)) # add p1 CS data.
    except:
        adc_array = None

    return timestamp, sht1, sht2, am_sens, adc_array

def ambient_status(value = None):
    if (value == -99):
            return 'red', 'not connected'
    if (value < 10):
        return 'cyan', 'ready'
    return 'yellow', 'not ready'

def component_status(component = None, value = None, log_file = None):
    if (component == 't1'):
        if (value is None):
            return 'red', 'not connected'
        if (value > 30 or value < 15): # arbitrary limits for now.
            return 'red', 'outside nominal range'
        else:
            return 'green', 'operating normally'
    if (component == 't2'):
        if (value is None):
            return 'red', 'not connected'
        if (value > 30 or value < 15): # arbitrary limits for now.
            return 'red', 'outside nominal range'
        else:
            return 'green', 'operating normally'
    if (component == 't3'):
        if (value is None):
            return 'red', 'not connected'
        if (value > 30 or value < 15): # arbitrary limits for now.
            return 'red', 'outside nominal range'
        else:
            return 'green', 'operating normally'
    if (component == 't4'):
        if (value is None):
            return 'red', 'not connected'
        if (value > 30 or value < 15): # arbitrary limits for now.
            return 'red', 'outside nominal range'
        else:
            return 'green', 'operating normally'
    if (component == 'cs'):
        if (value is None):
            return 'red', 'not connected'
        if (value > 30 or value < 15): # arbitrary limits for now.
            return 'red', 'outside nominal range'
        else:
            return 'green', 'operating normally'
    return 'green'

# Wait for input from Super Capacitors, then Save Files and Shutdown System.
def shutdown_protocol(sensor_log = None, error_log = None):
    os.shutdown()
    return None


if __name__ == '__main__':
    update_interval = 5 # Console Update Interval (Seconds), Default: 5
    record_interval = 120 # Data Record Interval (Seconds), Default: 120
    store_interval = 7200 # Data Save Record Interval (Seconds), Default: 7200

    # update the names of these variables to change output name.
    region_one = 'Region One Temperature and RH is'
    region_two = 'Region Two Temperature and RH is'
    thermistor_one = 'Thermistor One Temperature is'
    thermistor_two = 'Thermistor Two Temperature is'
    thermistor_three = 'Thermistor Three Temperature is'
    thermistor_four = 'Thermistor Four Temperature is'
    current_sensor_o = 'Current Draw is currently at'

    # Initialize Sensors as Objects
    # Will also store a log everytime this file runs.
    print('Initializing Sensors')
    try:
        first_sht35 = sensor.SHT35(address = 0x45, bus = 1)
    except:
        first_sht35 = None
        print("SHT35 Sensor 1 Failed to Connect")
    
    try:
        second_sht35 = sensor.SHT35(address = 0x44, bus = 1)
    except:
        second_sht35 = None
        print("SHT35 Sensor 2 Failed to Connect")

    try:
        am2302_sensor = sensor.AM2302() # fill this in.
    except: 
        am2302_sensor = None
        print("AM2302 Sensor Failed to Connect")

    try:
        adc_sensor = sensor.ADS7828(bus = 6)
    except:
        adc_sensor = None
        print("ADS7828 Sensor Failed to Connect")

    current_interval = 0
    recent_backup_date = 'N/A'
    storage_array = ['timestamp', 'sht1', 'sht2', 'am_sens', 'adc_array']
    time.sleep(3)
    # Run Scripting Loop
    while True:
        data_array = collect_data(sht35_a = first_sht35, sht35_b = second_sht35, am2302 = am2302_sensor, adc = adc_sensor)
        
        path = '/home/pi/DataLogs/'

        if not os.path.exists(path + str(dt.date.today()) + '.csv'):
            with open(path + str(dt.date.today()) + '.csv') as fe:
                fe.write('timestamp,sht1,sht2,am_sens,adc_array')
                fe.write('\n')
                fe.close()
            date_to_remove = str(dt.datetime.now - dt.timedelta(days=7))
            date_to_remove = date_to_remove[0:10]
            if os.path.exists(path + date_to_remove + '.csv'):
                os.remove(path + date_to_remove + '.csv')
        
        if (current_interval / record_interval == 1): 
            path_temp = path + str(dt.date.today())
            with open(path_temp + '.csv', 'a') as fd:
                recent_backup_date = str(dt.datetime.now())
                array_string = str(data_array)
                array_string.replace('[', '')
                array_string.replace(']', '')
                fd.write(array_string)
                fd.write('\n')
                fd.close()

            current_interval = 0
            

        # Posts data collected to the display.
        print('')
        print(colored('=======PT2 Instrument Monitoring Sub-Assembly=======','blue'))
        print(colored(region_one), colored(str('%.1f'%data_array[1][0]) + ' C', 'green'), colored('&'), colored(str('%.1f'%data_array[1][1]) + '% RH', ambient_status(data_array[1][1])[0]))
        print(colored(region_two), colored(str('%.1f'%data_array[2][0]) + ' C', 'green'), colored('&'), colored(str('%.1f'%data_array[2][1]) + '% RH', ambient_status(data_array[2][1])[0]))
        print(colored(thermistor_one), colored(str('%.1f'%data_array[4][0]) + ' C', component_status(component = 't1', value = data_array[4][0])[0]))
        print(colored(thermistor_two), colored(str('%.1f'%data_array[4][1]) + ' C', component_status(component = 't2', value = data_array[4][1])[0]))
        print(colored(thermistor_three), colored(str('%.1f'%data_array[4][2]) + ' C', component_status(component = 't3', value = data_array[4][2])[0]))
        print(colored(thermistor_four), colored(str('%.1f'%data_array[4][3]) + ' C', component_status(component = 't4', value = data_array[4][3])[0]))
        print(colored(current_sensor_o), colored(str('%.1f'%data_array[4][4]) + ' A', component_status(component = 'cs', value = data_array[4][4])[0]))
        print(colored('===================System Status====================','blue'))
        print(colored('Region One is'), colored(ambient_status(data_array[1][1])[1], ambient_status(data_array[1][1])[0]))
        print(colored('Region Two is'), colored(ambient_status(data_array[2][1])[1],ambient_status(data_array[2][1])[0]))
        print(colored('Thermistor One is'), colored(component_status(component = 't1', value = data_array[4][0])[1], component_status(component = 't1', value = data_array[4][0])[0]))
        print(colored('Thermistor Two is'), colored(component_status(component = 't2', value = data_array[4][1])[1], component_status(component = 't2', value = data_array[4][1])[0]))
        print(colored('Thermistor Three is'), colored(component_status(component = 't3', value = data_array[4][2])[1], component_status(component = 't3', value = data_array[4][2])[0]))
        print(colored('Thermistor Four is'), colored(component_status(component = 't4', value = data_array[4][3])[1], component_status(component = 't4', value = data_array[4][3])[0]))
        print(colored('Current Draw is'), colored(component_status(component = 'cs', value = data_array[4][4])[1], component_status(component = 'cs', value = data_array[4][4])[0]))
        print(colored("Data Last Backed Up:"), colored(recent_backup_date, 'magenta'))
        print('')

        current_interval += update_interval
        time.sleep(update_interval)
