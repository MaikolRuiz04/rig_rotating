
import sys
from tkinter import *
from datetime import datetime
import pigpio
import csv
import os
import threading
from threading import Timer
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np
import time    
    
# Pinouts
R_PWM = 18  # Forward drive PWM
L_PWM = 13  # Reverse drive PWM
HALL_PIN = 17    # Hall sensor

status = 0  # Status variable
rotations = 0   # rotation count from hall (resets every second)
rpm =  0     # rpm from rotations (calculate every second)
sample = 0  # time sample
total_rot = 0   # total number of rotations
temp = 0    # temporarily hold values
x, y = [], []   # plot axes
flag = 1
last_meas =0
pi=pigpio.pi()
pwm = 3000;

#GPIO.setmode(GPIO.BCM)      # setup GPIO
#GPIO.setwarnings(False)     # not sure what this does

# change pins to corresponding ones (NOTE: Reverse drive is disabled but can be enabled if desired)
#gpioSetMode(R_PWM, PI_OUT)                      # Rpwm pin enable
#gpioSetMode(L_PWM, PI_OUT)                      # Lpwm pin enable

# setup Hall sensor pin
pi.set_mode(HALL_PIN,pigpio.INPUT)
pi.set_pull_up_down(HALL_PIN, pigpio.PUD_UP)

# Forward Drive PWM setup
pi.hardware_PWM(R_PWM,pwm, 0)


# Reverse Drive PWM setup (same as above)
duty1 = 0                                     # keep track of duty cycle
pi.hardware_PWM(L_PWM,pwm, 0)

# csv file setup for hall_data
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_name = f"hall_data_{timestamp}.csv"
folder_name='Hall_Sensor_Data'
full_path=os.path.join(folder_name, file_name)
headers = ["Seconds", "RPM","Duty Cycle"]

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

try:
    with open(full_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
except IOError as e:
    print(f"Error creating file: {e}")
    
# Tkinter window setup
root = Tk()
root.title("Rotating-Bending Machine")
root.geometry("750x700")
root.configure(bg='#eeeeee')

print("w and s controls motor speed")       # print message

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

# Handles forward/reverse drive
def motor1(duty):
    global duty1
    temp  = duty1
    if duty > 0:                            # Positive duty cycle -> forward drive (clockwise?)
        pi.hardware_PWM(L_PWM,pwm, 0)               # just in case, set reverse drive to 0 duty cycle
        if duty > duty1:
            while duty > temp:
                temp = temp + 1
                pi.hardware_PWM(R_PWM, pwm, abs(temp))
        else: 
            while duty < temp:
                temp = temp-1
                pi.hardware_PWM(R_PWM, pwm, abs(temp))
        pi.hardware_PWM(R_PWM, pwm, abs(duty))           # change duty cycle    else 
    else:                                   # negative duty cycle -> reverse drive (counterclockwise?)
        pi.hardware_PWM(R_PWM,pwm, 0)               # just in case, set forward drive to 0 duty cycle
        if duty > duty1:
            while duty > temp:
                temp = temp + 1
                pi.hardware_PWM(L_PWM, pwm, abs(temp))
        else: 
            while duty < temp:
                temp = temp-1
                pi.hardware_PWM(L_PWM, pwm, abs(temp))
        pi.hardware_PWM(L_PWM, pwm, abs(duty))           # change duty cycle    else 
    print("motor: " + str(duty))            # print the duty cycle
    current_pwm.config(text=f"-Current Duty Cycle: {duty1}")

# callback function to sense Hall sensor's detection
def hall_callback(gpio, level, tick):
    global status
    global total_rot
    if status:
        total_rot = total_rot + 1
        
        
# add falling edge detection to Hall channel
cb = pi.callback(HALL_PIN, pigpio.FALLING_EDGE, hall_callback)

# submit hall sensor data to csv file
def submit():
    global sample
    global rpm
    global duty1
    new_row = [sample, rpm, duty1]
    with open(full_path,mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(new_row)

# update measurements and graph
def rpm_measure():
    global status
    global rpm
    global sample
    global total_rot
    global rotaions
    global x,y
    global last_meas
    if status:
        sample = sample + 1
        rpm = 60*(total_rot-last_meas)
        submit() 
        current_rpm.config(text=f"-Current RPM: {rpm}")
        current_rot.config(text=f"-Current rotations: {total_rot}")
        current_time.config(text=f"Running for {sample} seconds")
        y.append(rpm)
        y=y[-60:]
        x.append(sample)
        x=x[-60:]
        last_meas = total_rot
        
        
def update_graph():
    global rpm
    global status
    global x, y
    global flag
    fig = Figure(figsize=(6,4), dpi=100)
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("RPM")
    ax.set_title("RPM versus Time")
    ax.set_ylim(0, 3100)
    canvas = FigureCanvasTkAgg(fig, master=root)
    if flag:
        canvas.draw()
        canvas.get_tk_widget().grid(row=12,column=0,columnspan=10)
        flag = 0 
    if status:
        canvas.draw()
        canvas.get_tk_widget().grid(row=12,column=0,columnspan=10)
    root.after(1100,update_graph)
    
# start timer to run every second
timer = RepeatTimer(1, rpm_measure)
timer.start()
        
root.after(0, update_graph)

# Increase duty cycle by 10
def incr_speed():
    global duty1
    global status
    if status:
        if duty1 < 1000000:
            duty1 += 100000
            motor1(duty1)    

# Decrease duty cycle by 10
def decr_speed():
    global duty1
    global status
    if status:
        if duty1 > -1000000:
            duty1 -= 100000
            motor1(duty1)
            
# manually enter speed
def set_speed():
    global duty1
    global status
    if status:
        input_data = speed.get()
        if input_data:
            try:
                int(input_data)
                duty1 = int(input_data)*10000
                motor1(duty1)
            except ValueError:
                trouble.config(
                    text=f'Numeric value expected, got "{input_data}"',
                    foreground="red",
                )        
        else:
            trouble.config(
                text = "Entry is empty",
                foreground="red",
            )
        
# kick-start: brief high-duty pulse to overcome static friction
KICK_DUTY = 800000    # 80% duty cycle
KICK_DURATION = 0.3   # seconds

def kick_start(target_duty):
    if target_duty > 0:
        pi.hardware_PWM(L_PWM, pwm, 0)
        pi.hardware_PWM(R_PWM, pwm, KICK_DUTY)
    elif target_duty < 0:
        pi.hardware_PWM(R_PWM, pwm, 0)
        pi.hardware_PWM(L_PWM, pwm, KICK_DUTY)
    time.sleep(KICK_DURATION)
    motor1(target_duty)

# start motor control/recording data
def toggle_on():
    global status
    global duty1
    global temp
    status = 1
    duty1 = temp
    if duty1 != 0:
        kick_start(duty1)
    else:
        motor1(duty1)
    paused.config(text = "")

# pause motor control/recording
def toggle_off():
    global status
    global duty1
    global temp
    status = 0
    temp = duty1
    duty1 = 0
    motor1(duty1)
    paused.config(text = "                         (PAUSED)")
    
# close program
def exit_prog():
    timer.cancel()
    cb.cancel()
    pi.stop()
    root.quit()
    root.destroy()
    sys.exit()
    
    
# Title label
title = Label(root, text="ROTATING-BENDING MACHINE",font =("Arial", 20, "bold"),bg='#101010', fg='#eeeeee')
title.grid(row=0, column = 0,columnspan=4,sticky=W)
        
# Paused message
paused = Label(root, text="", font = ("Arial", 18, "bold"),bg='#eeeeee', fg='#101010')
paused.grid(row=10,column=1,columnspan=2)

# current pwm label
current_pwm = Label(root, text=f"-Current Duty Cycle: {duty1}", font=("Arial", 12, "bold"), bg='#eeeeee')
current_pwm.grid(row=6,column=0,columnspan=2,sticky=W)
        
# Increase speed Tk-button
forward = Button(root, text="+10", width=4, command=incr_speed)
forward.grid(row = 4, column = 3, padx=2, pady=2)

# Decrease speed Tk-button
back = Button(root, text="-10", width=4, command=decr_speed)
back.grid(row=4, column=4,padx=2,pady=2)

# Text entry for speed
speed = Entry(root, width=20)
speed.grid(row=4, column=1,sticky=W)

# PWM label
pwm_indicator = Label(root, text="Duty Cycle (%): ",font=("Arial", 12, "bold"))
pwm_indicator.grid(row=4,column=0,sticky=W)

#spacing
spacing = Label(root,text="",bg='#eeeeee')
spacing.grid(row=5,column=0)
# troubleshoot message
trouble = Label(root, text="",bg='#eeeeee')
trouble.grid(row=2, column=1,padx=2,pady=1)

# Enter/confirm speed value types
confirm = Button(root, text="Enter", width=4,command=set_speed)
confirm.grid(row=4,column=2)

# Hall data query
# display_hall = Button(root, text="RPM data", command=query)
# display_hall.grid(row=7, column = 7)

# Label that displays the current RPM from Hall
current_rpm = Label(root,text=f"-Current RPM: {rpm}",font=("Arial", 12, "bold"),bg='#eeeeee')
current_rpm.grid(row=7,column=0,columnspan=2,sticky=W)

# Label that displays the time (of measurement not global)
current_time = Label(root,text=f"Running for {sample} seconds",font=("Arial", 14, "bold"),bg='#eeeeee')
current_time.grid(row=9,column=0, columnspan = 2,sticky=W)

# Label displaying total rotations
current_rot = Label(root,text=f"-Current rotations: {total_rot}",font=("Arial", 12, "bold"),bg='#eeeeee')
current_rot.grid(row=8,column=0,columnspan=2, sticky=W)

# Global start/stop
start = Button(root, text="START", command=toggle_on,font=("Arial", 14, "bold"), bg='#00ee00',fg='#eeeeee')
start.grid(row=9,column = 6)
stop = Button(root, text="STOP", command=toggle_off, font=("Arial", 14, "bold"), bg='#ee0000',fg='#eeeeee')
stop.grid(row=9,column=7)

# Exit button to properly close program
exit_program = Button(root, text = "EXIT", command=exit_prog, font = ("Arial", 12, "bold"))
exit_program.grid(row=0,column=7, sticky=E)

#timer_thread.join()    
root.mainloop()

# end of life 
p1.stop()
del p1
p2.stop()
del p2
GPIO.cleanup()

