from mpu6050 import mpu6050
import time

sensor = mpu6050(0x6a)

print("IMU Test Started")

while True:

    accel = sensor.get_accel_data()
    gyro = sensor.get_gyro_data()

    print("-------------------")

    print("Acceleration")
    print("X:", accel['x'])
    print("Y:", accel['y'])
    print("Z:", accel['z'])

    print("Gyroscope")
    print("X:", gyro['x'])
    print("Y:", gyro['y'])
    print("Z:", gyro['z'])

    time.sleep(0.5)