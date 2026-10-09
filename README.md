# ENG108

CHANGES WE MADE TO ORIGINAL SCRIPTS BY https://github.com/doug-burrell/max30102

We just modified heartrate_monitor.py, main.py,  but we need heartrate_monitor.py, hrcalc.py, main.py and max30102.py for it to work.

heartrate_monitor.py

Added self.spo2 = 0 to store the SpO2 value
Added self.spo2 = spo2 to save the latest SpO2 reading

main.py

Added imports: csv, datetime, gpiozero, dropbox
Added the Dropbox token setting
Added alert limits: heart rate 50–120 BPM, SpO2 94%+
Added the red LED on GPIO17 and the push button on GPIO22
Added a readings list to store the data
Added a save_data() function that saves a CSV file and uploads it to Dropbox
Linked the button to save_data()
Replaced the 30-second wait with a loop that checks the readings every second
Saved each reading with a timestamp
Made the red LED blink fast when a reading is outside the limits
Turned the LED off at the end of the program
