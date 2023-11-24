import supervisor
supervisor.runtime.autoreload = False

import time
import board
import busio
import adafruit_mpu6050
import sdcardio
import storage
import circuitpython_csv as csv

# i2c = board.I2C()  # uses board.SCL and board.SDA
i2c = busio.I2C(board.IO11, board.IO10)
mpu = adafruit_mpu6050.MPU6050(i2c, address = 0x68)

spi = busio.SPI(board.IO35, board.IO37, board.IO33)
sdcard = sdcardio.SDCard(spi, board.IO39)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# Write the CSV file!
with open("/sd/testwrite.csv", mode="w", encoding="utf-8") as writablefile:
    csvwriter = csv.writer(writablefile)
    csvwriter.writerow(["I", "love", "CircuitPython", "!"])
    csvwriter.writerow(["Spam"] * 3)

while True:
    # print("Acceleration: X:%.2f, Y: %.2f, Z: %.2f m/s^2"%(mpu.acceleration))
    print("Gyro X:%.2f, Y: %.2f, Z: %.2f degrees/s"%(mpu.gyro))
    # print("Temperature: %.2f C"%mpu.temperature)
    print("")
    # time.sleep(1)
