import supervisor
supervisor.runtime.autoreload = False

print('Starting...')

import time
import board
import busio
import sdcardio
import storage
import os
import digitalio
import thisbutton as tb
import circuitpython_csv as csv

from robohat_mpu9250.mpu9250 import MPU9250
from robohat_mpu9250.mpu6500 import MPU6500
from robohat_mpu9250.ak8963 import AK8963

# Button initialization
buttonState = False
def buttonClickStart():
    global buttonState
    buttonState = not buttonState

button = tb.thisButton(board.BUTTON, True)
button.assignClickStart(buttonClickStart)

# LED initialization
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# IMU initialization
i2c = busio.I2C(board.IO11, board.IO10)
mpu = MPU6500(i2c, address=0x68)
ak = AK8963(i2c)
sensor = MPU9250(mpu, ak)

# uSDCard initialization
spi = busio.SPI(board.IO35, board.IO37, board.IO33)
sdcard = sdcardio.SDCard(spi, board.IO39)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

print('Waiting for button click to start recording the data')

# Wait for user button click before starting writing
# blinkind the LED while waiting
led_tick_counter = 0
while(buttonState is False):
    button.tick()

    led_tick_counter +=1
    if led_tick_counter % 5 == 0:
        led.value = not led.value

    time.sleep(0.05)

# Check for some free space of SDCard
sd_statvfs = vfs.statvfs('/sd')
# sd_free_space = file system block size * file system block size
sd_free_space = sd_statvfs[0] * sd_statvfs[3]
if sd_free_space < (1024 * 1024):
    print('SDCard with less then 1MByte of free space')
    # block here
    while True: pass 

# Find latest CSV file with numeric name
sd_listdir = vfs.ilistdir()
files = [file for file in sd_listdir]
csv_files = [file for file in files if '.csv' in file[0]]

last_file_number = 0
if len(csv_files):
    for csv_file in csv_files:
        csv_file_name = csv_file[0].rstrip('.csv')
        if csv_file_name.isdigit():
            last_file_number = int(csv_file_name)

# Limit to max of 1000 numbers
if last_file_number > 1000:
    last_file_number = 0

# Increase the number of lastest CSV file name number
last_file_number += 1
file_name = f'{last_file_number}.csv'

# Let's start writing
print(f'Start writing to file: {file_name}')
# Enable LED while writing data
led.value = True

writablefile = open('/sd/' + file_name, mode='w', encoding='utf-8')
csvwriter = csv.writer(writablefile)

# Write first line
csvwriter.writerow(['time milliseconds', 'magnetic x', 'magnetic y', 'magnetic z', 'acceleration x', 'acceleration y', 'acceleration z', 'gyro x', 'gyro y', 'gyro z'])

button_last_time = time.monotonic_ns()

# Each loop, to read the sensor and write the data in a line of CSV file, takes about 30ms
while True:
    current_time = time.monotonic_ns()

    # Get the IMU data
    magnetic = sensor.read_magnetic()
    acceleration = sensor.read_acceleration()
    gyro = sensor.read_gyro()

    # Write the IMU data to the CSV file
    data = [
        f'{int(time.monotonic_ns()/1000000)}',
        f'{magnetic[0]:.3f}',
        f'{magnetic[1]:.3f}',
        f'{magnetic[2]:.3f}',
        f'{acceleration[0]:.3f}',
        f'{acceleration[1]:.3f}',
        f'{acceleration[2]:.3f}',
        f'{gyro[0]:.3f}',
        f'{gyro[1]:.3f}',
        f'{gyro[2]:.3f}',
    ]
    csvwriter.writerow(data)
    
    # If button click, leave this loop
    # button.tick() only every 0.25ms
    if current_time - button_last_time > 250_000_000:
        button_last_time = current_time

        button.tick()
        if buttonState is False:
            break

# Flush any data in memory to the CSV file and close it
writablefile.flush()
writablefile.close()

print('Stopped writing...')

# Disable LED after finishing writing data
led.value = False

# Wait some time before restart
print('Restarting')
time.sleep(3)
supervisor.reload()
