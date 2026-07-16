#!/usr/bin/env python3

import time
import math
import csv
import subprocess
from mpu6050 import mpu6050

# ==========================================
# SETTINGS
# ==========================================

LAUNCH_THRESHOLD = 4.0      # g
LAUNCH_COUNT = 5            # consecutive samples

LANDING_ACCEL_MIN = 0.9
LANDING_ACCEL_MAX = 1.1
LANDING_GYRO_MAX = 5.0
LANDING_COUNT = 100         # ~5 sec at 20 Hz

SAMPLE_RATE = 20            # Hz

# ==========================================
# START CAMERA
# ==========================================

video_filename = f"flight_{int(time.time())}.h264"

camera = subprocess.Popen([
    "rpicam-vid",
    "-t", "0",
    "--width", "1920",
    "--height", "1080",
    "--framerate", "30",
    "-o", video_filename
])

print("Camera recording started")

# ==========================================
# IMU SETUP
# ==========================================

sensor = mpu6050(0x68)

# ==========================================
# LOG FILE
# ==========================================

csv_filename = f"flight_{int(time.time())}.csv"

csv_file = open(csv_filename, "w", newline="")
writer = csv.writer(csv_file)

writer.writerow([
    "unix_time",
    "flight_time",
    "event",
    "ax",
    "ay",
    "az",
    "gx",
    "gy",
    "gz",
    "total_accel",
    "total_gyro"
])

# ==========================================
# INITIAL STATE
# ==========================================

writer.writerow([
    time.time(),
    0,
    "BOOT",
    "", "", "",
    "", "", "",
    "", ""
])

recording_flight = False
launch_counter = 0
landing_counter = 0

launch_time = None

print("Waiting for launch...")

# ==========================================
# MAIN LOOP
# ==========================================

while True:

    accel = sensor.get_accel_data()
    gyro = sensor.get_gyro_data()

    ax = accel['x']
    ay = accel['y']
    az = accel['z']

    gx = gyro['x']
    gy = gyro['y']
    gz = gyro['z']

    total_accel = math.sqrt(ax**2 + ay**2 + az**2)
    total_gyro = math.sqrt(gx**2 + gy**2 + gz**2)

    current_time = time.time()

    if launch_time is None:
        flight_time = 0
    else:
        flight_time = current_time - launch_time

    # ======================================
    # LAUNCH DETECTION
    # ======================================

    if not recording_flight:

        if total_accel > LAUNCH_THRESHOLD:
            launch_counter += 1
        else:
            launch_counter = 0

        if launch_counter >= LAUNCH_COUNT:

            launch_time = current_time
            recording_flight = True

            print("==========")
            print("LAUNCH DETECTED")
            print("==========")

            writer.writerow([
                current_time,
                0,
                "LAUNCH",
                ax, ay, az,
                gx, gy, gz,
                total_accel,
                total_gyro
            ])

    # ======================================
    # FLIGHT RECORDING
    # ======================================

    if recording_flight:

        writer.writerow([
            current_time,
            flight_time,
            "DATA",
            ax,
            ay,
            az,
            gx,
            gy,
            gz,
            total_accel,
            total_gyro
        ])

        # ==============================
        # LANDING DETECTION
        # ==============================

        if (
            LANDING_ACCEL_MIN <= total_accel <= LANDING_ACCEL_MAX
            and total_gyro < LANDING_GYRO_MAX
        ):
            landing_counter += 1
        else:
            landing_counter = 0

        if landing_counter >= LANDING_COUNT:

            print("==========")
            print("LANDING DETECTED")
            print("==========")

            writer.writerow([
                current_time,
                flight_time,
                "LANDING",
                ax,
                ay,
                az,
                gx,
                gy,
                gz,
                total_accel,
                total_gyro
            ])

            break

    time.sleep(1 / SAMPLE_RATE)

# ==========================================
# CLEANUP
# ==========================================

csv_file.flush()
csv_file.close()

camera.terminate()
camera.wait()

print("Flight complete")
print(f"Video saved: {video_filename}")
print(f"Log saved: {csv_filename}")