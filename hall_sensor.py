import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
HALL_PIN = 4

GPIO.setup(HALL_PIN, GPIO.IN)

print("Hall sensor running...")

try:
    while True:
        if GPIO.input(HALL_PIN) == GPIO.HIGH:
            print("Magnet detected!")
        else:
            print("No magnet")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting")

finally:
    GPIO.cleanup()
