from heartrate_monitor import HeartRateMonitor
import time
import argparse
import csv                          # ADDED
from datetime import datetime       # ADDED
from gpiozero import LED, Button    # ADDED
import dropbox                      # ADDED
 
# ---------------- ADDED: settings ----------------
DROPBOX_TOKEN = "PASTE_YOUR_DROPBOX_ACCESS_TOKEN_HERE"
HR_MIN = 50        # alert if heart rate is below this (BPM)
HR_MAX = 120       # alert if heart rate is above this (BPM)
SPO2_MIN = 94      # alert if SpO2 is below this (%)
 
red_led = LED(17)       # red LED on GPIO17 (physical pin 11)
button = Button(22)     # push button on GPIO22 (physical pin 15)
readings = []           # every reading taken while the script runs
 
 
# ---------------- ADDED: what happens when the button is pressed ----------------
def save_data():
    filename = "health_data_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
 
    # 1. save to a file on the Pi
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "heart_rate_bpm", "spo2_percent"])
        writer.writerows(readings)
    print("Saved", len(readings), "readings to", filename)
 
    # 2. upload the same file to Dropbox (the cloud)
    try:
        dbx = dropbox.Dropbox(DROPBOX_TOKEN)
        with open(filename, "rb") as f:
            dbx.files_upload(f.read(), "/" + filename)
        print("Uploaded to Dropbox:", filename)
    except Exception as e:
        print("Dropbox upload failed:", e)
 
 
button.when_pressed = save_data
# -------------------------------------------------------------------------------
 
parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
parser.add_argument("-r", "--raw", action="store_true",
                    help="print raw data instead of calculation result")
parser.add_argument("-t", "--time", type=int, default=30,
                    help="duration in seconds to read from sensor, default 30")
args = parser.parse_args()
 
print('sensor starting...')
hrm = HeartRateMonitor(print_raw=args.raw, print_result=(not args.raw))
hrm.start_sensor()
try:
    # CHANGED: instead of time.sleep(args.time), check the readings once a second
    blinking = False
    end_time = time.time() + args.time
    while time.time() < end_time:
        bpm = hrm.bpm
        spo2 = hrm.spo2
        alert = False
 
        if bpm > 0:   # bpm is 0 when no finger is on the sensor
            readings.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             round(bpm, 1), round(spo2, 1)])
            if bpm < HR_MIN or bpm > HR_MAX:
                alert = True
            if 0 < spo2 < SPO2_MIN:   # spo2 is -999 when the sensor couldn't calculate it
                alert = True
 
        if alert and not blinking:
            red_led.blink(on_time=0.1, off_time=0.1)   # blink rapidly
            blinking = True
        elif not alert and blinking:
            red_led.off()
            blinking = False
 
        time.sleep(1)
except KeyboardInterrupt:
    print('keyboard interrupt detected, exiting...')
 
red_led.off()   # ADDED
hrm.stop_sensor()
print('sensor stoped!')
 
