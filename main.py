from port_searching import port_search
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
from itertools import count
import pandas as pd
import statistic as s
import datetime
import serial
import time

# parameters
measurement_in_graph = 70
fig_size = (3, 2)
font = ("Helvetica", 16)

# Setup
counter = count()
x_data = []
dis_data = []
RSSI_data = []
fp_data = []
in_measurement = True
SAMPLE_SIZE = 13
ani1 = None
ani2 = None
ani3 = None

port = port_search()
usb_port = serial.Serial(port, 115200)
time.sleep(2)

# Create a function to update the animation frames
def update_animation(frame):
    distance, rssi, fp = read()
    ax_distance.clear()
    ax_RSSI.clear()
    ax_fp.clear()
    if in_measurement:
        x_data.append(next(counter))
        dis_data.append(distance)
        RSSI_data.append(rssi)
        fp_data.append(fp)
    if len(x_data) > measurement_in_graph:
        ax_distance.plot(x_data[-1 * measurement_in_graph:], dis_data[-1 * measurement_in_graph:])
        ax_RSSI.plot(x_data[-1 * measurement_in_graph:], RSSI_data[-1 * measurement_in_graph:])
        ax_fp.plot(x_data[-1 * measurement_in_graph:], fp_data[-1 * measurement_in_graph:])
    else:
        ax_distance.plot(x_data, dis_data)
        ax_RSSI.plot(x_data, RSSI_data)
        ax_fp.plot(x_data, fp_data)

    # Set the axes
    ax_distance.set_xlabel("measure")
    ax_distance.set_title("distance")
    ax_RSSI.set_xlabel("measure")
    ax_RSSI.set_title("RSSI")
    ax_fp.set_xlabel("measure")
    ax_fp.set_title("fp")

    # Update the stats
    if len(x_data) > 2:
        stat_table.itemconfig(distance_av, text=f'{s.mean(dis_data)}')
        stat_table.itemconfig(RSSI_av, text=f'{s.mean(RSSI_data)}')
        stat_table.itemconfig(fp_av, text=f'{s.mean(fp_data)}')
        stat_table.itemconfig(distance_std, text=f'{s.std(dis_data)}')
        stat_table.itemconfig(RSSI_std, text=f'{s.std(RSSI_data)}')
        stat_table.itemconfig(fp_std, text=f'{s.std(fp_data)}')


def read():

    distance1 = None
    i = 0
    while distance1 is None:
        i += 1
        usb_port.write(f"go {SAMPLE_SIZE}\n".encode())
        line = usb_port.readline().decode()
        elements = line.split(' ')
        if len(elements) > 4:
            if elements[4] == 'range:':
                distance1 = float(elements[5].strip())
        if i > 25:
            print('error')
            raise
            window.quit()
    #distance1 = d + np.random.randint(-100, 100) / 100
    return distance1, -80 + np.random.randint(-100, 100) / 50, -70 + np.random.randint(-100, 100) / 50


# Create the main application window
window = Tk()
window.title("Trial for the DW3000 Sensor")
window.minsize(width=900, height=500)


# Create a Frame to hold the Matplotlib plot
frame = Frame(window)
frame.grid(row=3, column=0, padx=10, pady=10)

# Create a Matplotlib Figure and Canvas
dis_fig = Figure(figsize=fig_size)
ax_distance = dis_fig.add_subplot(111)
canvas = FigureCanvasTkAgg(dis_fig, master=frame)
distance_graph = canvas.get_tk_widget()

RSSI_fig = Figure(figsize=fig_size)
ax_RSSI = RSSI_fig.add_subplot(111)
canvas = FigureCanvasTkAgg(RSSI_fig, master=frame)
RSSI_graph = canvas.get_tk_widget()

fp_fig = Figure(figsize=fig_size)
ax_fp = fp_fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fp_fig, master=frame)
fp_graph = canvas.get_tk_widget()

stat_table = Canvas(window, width=900, height=180)
table_heading1 = stat_table.create_text(160, 10, text='Distance', font=font)
table_heading2 = stat_table.create_text(450, 10, text='Rssi', font=font)
table_heading3 = stat_table.create_text(740, 10, text='Fp', font=font)

av = stat_table.create_text(30, 90, text='Mean', font=font)
std = stat_table.create_text(30, 170, text='STD', font=font)

distance_av = stat_table.create_text(160, 90, text='0', font=font)
distance_std = stat_table.create_text(160, 170, text='0', font=font)

RSSI_av = stat_table.create_text(450, 90, text='0', font=font)
RSSI_std = stat_table.create_text(450, 170, text='0', font=font)

fp_av = stat_table.create_text(740, 90, text='0', font=font)
fp_std = stat_table.create_text(740, 170, text='0', font=font)

# Start the animation
def start():
    global in_measurement
    global counter
    global ani1
    global ani2
    global ani3
    if start_button.cget('text') == "Start":

        in_measurement = True
        # Create a FuncAnimation object
        ani1 = FuncAnimation(dis_fig, update_animation, repeat=False, cache_frame_data=False)
        ani2 = FuncAnimation(RSSI_fig, update_animation, repeat=False, cache_frame_data=False)
        ani3 = FuncAnimation(fp_fig, update_animation, repeat=False, cache_frame_data=False)
        ani1._start()
        ani2._start()
        ani3._start()
    if start_button.cget('text') == "clear":
        current_datetime = datetime.datetime.now()
        if save_to_file.get():
            data = pd.DataFrame({'distance': dis_data, 'RSSI': RSSI_data, 'fp': fp_data})
            data.to_csv(f'{round(data["distance"].mean(), 2)}m{current_datetime.hour},{current_datetime.minute}.csv')
        x_data.clear()
        dis_data.clear()
        RSSI_data.clear()
        fp_data.clear()
        stop_button.config(text='stop')
        start_button.config(text='Start')
        counter = count()
        #in_measurement = not in_measurement
        ani1.event_source.stop()
        ani2.event_source.stop()
        ani3.event_source.stop()


def stop():
    global in_measurement
    in_measurement = not in_measurement
    if not in_measurement:
        stop_button.config(text='resume')
        start_button.config(text='clear')
    if in_measurement:
        stop_button.config(text='stop')
        start_button.config(text='start')


# Create the buttons
close_button = Button(window, text="Close", command=window.quit)
start_button = Button(window, text="Start", command=start)
stop_button = Button(window, text="stop", command=stop)

# Create a variable to store the checkbox's state
save_to_file = BooleanVar()

# Create a Checkbutton widget
checkbox = Checkbutton(window, text="save this measurement?", variable=save_to_file)

# Grid
stat_table.grid(row=0, column=0, padx=10, pady=10)

distance_graph.grid(row=3, column=0, padx=10, pady=10)
RSSI_graph.grid(row=3, column=1, padx=10, pady=10)
fp_graph.grid(row=3, column=2, padx=10, pady=10)

close_button.grid(row=4, column=0, padx=50, pady=10, columnspan=2)
start_button.grid(row=5, columns=1, padx=50, pady=10, columnspan=2)
checkbox.grid(row=6, columns=1, padx=50, pady=10, columnspan=2)
stop_button.grid(row=7, columns=2, padx=50, pady=10, columnspan=2)

# Start the Tkinter main loop
window.mainloop()
