import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
HALL_PIN = 17
count = 0
start_time = time.time()
duration = 10
rpm = 0


GPIO.setup(HALL_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("Hall sensor running...")

def count_pulse(channel):
    global count, start_time
    count+= 1
    
GPIO.add_event_detect(HALL_PIN, GPIO.FALLING, callback=count_pulse)

try:
    while True:
        time.sleep(1)
        rpm = (count)*60
        print(f"RPM: {rpm}")
        count = 0

except KeyboardInterrupt:
    print("Exiting")

finally:
    print(count)
    GPIO.cleanup()
