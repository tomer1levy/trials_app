from serial.tools import list_ports
import tkinter as tk
from tkinter import ttk
import platform
import tkinter

selected_option = None
port = None
def port_search():
    port_window = tk.Tk()
    # Find the right port
    usb_ports = [p.device for p in list_ports.comports() if 'USB' in p.description]
    if len(usb_ports) == 0:
        print('No USB ports found')
        exit()
    else:
        print('Multiple USB ports found. ')
        ports_list = [port for i, port in enumerate(usb_ports)]

        def select(event):
            global selected_option
            selected_option = combobox.get()
            label.config(text=f"You selected: {selected_option}")

        def confirm():
            global port
            system_platform = platform.system()
            selected_option = combobox.get()
            if system_platform == "Darwin":  # macOS
                port = usb_ports[int(selected_option)]
            if system_platform == "Windows":
                port = selected_option
                port_window.quit()
        combobox = ttk.Combobox(port_window, values=ports_list)
        combobox.pack()
        combobox.bind("<<ComboboxSelected>>", select)
        # Create a label to display the selected option
        label = tkinter.Label(port_window, text="Choose your port")
        label.pack()
        confirm_button = tk.Button(text='confirm', command=confirm)
        confirm_button.pack()

    port_window.mainloop()
    return port

