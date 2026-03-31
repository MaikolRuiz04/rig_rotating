import RPi.GPIO as GPIO
import time
RPWM_PIN = 18
LPWM_PIN = 13
REN_PIN = 16
LEN_PIN = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(RPWM_PIN, GPIO.OUT)
GPIO.setup(LPWM_PIN, GPIO.OUT)
GPIO.setup(REN_PIN, GPIO.OUT)
GPIO.setup(LEN_PIN, GPIO.OUT)

frequency = 1000
rpwm = GPIO.PWM(RPWM_PIN, frequency)
lpwm = GPIO.PWM(LPWM_PIN, frequency)

rpwm.start(0)
lpwm.start(0)

try:
	while True:
		GPIO.output(REN_PIN, GPIO.HIGH)
		GPIO.output(LEN_PIN, GPIO.LOW)
		
		rpwm.ChangeDutyCycle(50)
		lpwm.ChangeDutyCycle(0)
		print("Forward 50%")
		time.sleep(2)
		
		
		GPIO.output(REN_PIN, GPIO.LOW)
		GPIO.output(LEN_PIN, GPIO.HIGH)
		
		rpwm.ChangeDutyCycle(0)
		lpwm.ChangeDutyCycle(30)
		print("Reverse 50%")
		time.sleep(2)
		
except KeyboardInterrupt:
	print("Stopping motor...")
	
finally:
	rpwm.stop()
	lpwm.stop()
	GPIO.cleanup()
		
		
		
