# Connect to The Things Network (TTN) and publish some test data
#
# How to get started:
#   • Create an account on cloud.thethings.network
#   • Create an application
#   • Run this script to get the JoinEUI and DeviceEUI
#   • On your applicaiton, generate an AppKey and paste it as a string in the code below.
#   • Run this script again
#   • Monitor your applicaiton console and look for a test message being received on TTN
#
# This demo is based off the Getting Started Guide by seeedstudio:
# https://wiki.seeedstudio.com/LoRa-E5_STM32WLE5JC_Module/#getting-started
#
# Refer to the AT Command Specification
# https://files.seeedstudio.com/products/317990687/res/LoRa-E5%20AT%20Command%20Specification_V1.0%20.pdf




# Put your key here (string). This should match the AppKey generated by your application.
#For example: app_key = 'E08B834FB0866939FC94CDCC15D0A0BE'
app_key = 'E1A2D215693295D6567BC33DC805040B'

# Regional LoRaWAN settings. You may need to modify these depending on your region.
# If you are using AU915: Australia
#band='AU915'
#channels='8-15'

# If you are using US915
# band='US915'
# channels='8-15'
# 
# If you are using EU868
band='EU868'
channels='0-2'


import machine
import time

from machine import UART, Pin
from utime import sleep_ms
from sys import exit

uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
join_EUI = None   # These are populated by this script
device_EUI = None

### Function Definitions

def receive_uart():
    '''Polls the uart until all data is dequeued'''
    rxData=bytes()
    while uart1.any()>0:
        rxData += uart1.read(1)
        sleep_ms(2)
    return rxData.decode('utf-8')

def send_AT(command):
    '''Wraps the "command" string with AT+ and \r\n'''
    buffer = 'AT' + command + '\r\n'
    uart1.write(buffer)
    sleep_ms(300)

def test_uart_connection():
    '''Checks for good UART connection by querying the LoRa-E5 module with a test command'''
    send_AT('') # empty at command will query status
    data = receive_uart()
    if data == '+AT: OK\r\n' : print('LoRa radio is ready\n')
    else:
        print('LoRa-E5 detected\n')
        exit()

def get_eui_from_radio():
    '''Reads both the DeviceEUI and JoinEUI from the device'''
    send_AT('+ID=DevEui')
    data = receive_uart()
    device_EUI = data.split()[2]

    send_AT('+ID=AppEui')
    data = receive_uart()
    join_EUI = data.split()[2]

    print(f'JoinEUI: {join_EUI}\n DevEUI: {device_EUI}')
    
def set_app_key(app_key):
    if app_key is None or app_key == 'None':
        print('\nGenerate an AppKey on cloud.thethings.network and enter it at the top of this script to proceed')
        exit()

    send_AT('+KEY=APPKEY,"' + app_key + '"')
    receive_uart()
    print(f' AppKey: {app_key}\n')


def configure_regional_settings(band=None, DR='0', channels=None):
    ''' Configure band and channel settings'''
    
    send_AT('+DR=' + band)
    send_AT('+DR=' + DR)
    send_AT('+CH=NUM,' + channels)
    send_AT('+MODE=LWOTAA')
    receive_uart() # flush
    
    send_AT('+DR')
    data = receive_uart()
    print(data)


def join_the_things_network():
    '''Connect to The Things Network. Exit on failure'''
    send_AT('+JOIN')
    data = receive_uart()
    print(data)

    status = 'not connected'
    while status == 'not connected':
        data = receive_uart()
        if len(data) > 0: print(data)
        if 'joined' in data.split():
            status = 'connected'
        if 'failed' in data.split():
            print('Join Failed')
            exit()
        
        sleep_ms(1000)
        
def send_message(message):
    '''Send a string message'''
    send_AT('+MSG="' + message + '"')

    done = False
    while not done:
        data = receive_uart()
        if 'Done' in data or 'ERROR' in data:
            done = True
        if len(data) > 0: print(data)
        sleep_ms(1000)
        
#调整速率和编码率（无报错，但是连不上）

# def configure_data_rate_and_coding_rate(DR='5', CR='4/5'):
#     send_AT('+DR=' + DR)
#     send_AT('+CR=' + CR)
#     receive_uart()  # flush
# 
# def main_loop():
#     while True:
#         # ... 之前的代码 ...
# 
#         # 调整数据速率和编码率
#         configure_data_rate_and_coding_rate(DR='5', CR='4/5')
# 
#         # 发送数据
#         send_message(message)
# 
#         sleep_ms(3000)
# 在主程序中调用 main_loop()
# main_loop()


#启用ADR(不行，但是一直在闪蓝光，应该是设备在尝试连接)

# def enable_adr():
#     send_AT('+ADR=ON')
#     receive_uart()  # flush
# 
# def main_loop_with_adr():
#     while True:
# 
# 
#         # 启用 ADR
#         enable_adr()
# 在主程序中调用 main_loop_with_adr()
# main_loop_with_adr()
# 



##########################################################
#        
# The main program starts here
#
##########################################################

test_uart_connection()

get_eui_from_radio()

set_app_key(app_key)

configure_regional_settings(band=band, DR='0', channels=channels)

join_the_things_network()


# Send example data
print("sending temperature data")
analog_value = machine.ADC(26)
conversion_factor = 3.3/ 65535

while True:
    temp_voltage_raw = analog_value.read_u16()
    convert_voltage = temp_voltage_raw*conversion_factor
    tempC = convert_voltage/(10.0 / 1000)
    print("Temperature: ",tempC, "°C", sep=" ")
    #message = "Temperature: {:.2f} °C".format(tempC)
    message = str(tempC)
    send_message(message)
    sleep_ms(3000)



