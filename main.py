import tkinter as tk
from tkinter import ttk
from tktooltip import ToolTip
# import numpy
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import json
import socket


class RootWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.init_vals = {'salary': 70000, 'rate': 4.99, 'years': 35}
        self.salary = tk.DoubleVar(master=self)
        self.salary.set(70000.00)
        self.salary.trace('w', self._debug_trace)
        self.rate = tk.DoubleVar(master=self)
        self.rate.set(4.99)
        self.rate.trace('w', self._debug_trace)
        self.years = tk.IntVar(master=self)
        self.years.set(35)
        self.years.trace('w', self._debug_trace)
        self.socket_manager = SocketManager()

        self.title('Outlook')
        self._frame = StartupFrame(self, {})
        self._tutorial_window = None
        self._load_window = None

        self._frame.grid(row=0, column=0)

    def switch_frame(self, frame_class):
        print(f'received request to switch to {frame_class}')
        if frame_class is OutlookFrame:
            new_frame = frame_class(self, [self.salary, self.rate, self.years])
        else:
            new_frame = frame_class
        self._frame.destroy()
        self._frame = new_frame
        self._frame.grid(row=0, column=0)

    def open_tutorial(self):
        self._tutorial_window = TutorialWindow(self)

    def open_load(self):
        self._load_window = LoadWindow(self)

    def open_save(self):
        self._load_window = SaveWindow(self)

    def save_outlook(self, path):
        save_dict = {'path': path,
                     'action': 'save',
                     'info': self.get_outlook()}
        print(f"save dictionary is {save_dict}")
        response = self.socket_manager.send_over_socket(save_dict)
        print(f"response is: {response}")

    def load_outlook(self, path):
        load_dict = {'path': path,
                     'action': 'load',
                     'info': None}
        print(f"load dictionary is {load_dict}")
        # load does seem to be broken entirely due to the OS bad fd error
        response = self.socket_manager.send_over_socket(load_dict)
        self.init_vals = response['info']
        self.salary.set(self.init_vals['salary'])
        self.rate.set(self.init_vals['rate'])
        self.years.set(self.init_vals['years'])
        self.switch_frame(OutlookFrame)

    def get_outlook(self):
        return {'salary': self.salary.get(),
                'rate': self.rate.get(),
                'years': self.years.get()}

    def set_outlook(self, load_dict):
        ...

    def _debug_trace(self, *args):
        print(f"salary: {self.salary.get()},rate: {self.rate.get()}, years: {self.years.get()}")


class SaveWindow(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title('Save an outlook')
        self.geometry('500x50')

        # set up frames
        self._mainframe = ttk.Frame(self, padding='5 5 5 5')

        self._path = tk.StringVar()
        self._path.set('/home/brenda/python_projects/cs361-outlook/')

        self._warn_lbl = tk.Label(self._mainframe, text='Warning! This will overwrite data at the path you specify.')
        self._path_etr = tk.Entry(self._mainframe, width=55, textvariable=self._path)
        ToolTip(self._path_etr, msg='Enter the path to save the .out file', delay=0.5)
        self._save_btn = tk.Button(self._mainframe, text='Save', command=self.save_outlook)

        self._mainframe.grid(row=0, column=0)
        self._warn_lbl.grid(row=1, column=0, columnspan=2)
        self._path_etr.grid(row=0, column=0)
        self._save_btn.grid(row=0, column=1)

    def save_outlook(self):
        self.master.save_outlook(self._path.get())
        self.destroy()


class LoadWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.title('Load an outlook')
        self.geometry('500x50')

        # set up frames
        self._mainframe = ttk.Frame(self, padding='5 5 5 5')

        # set up variables
        self._path = tk.StringVar()
        self._path.set('/home/brenda/python_projects/cs361-outlook/')

        # set up widgets
        self._path_etr = tk.Entry(self._mainframe, width=55, textvariable=self._path)
        ToolTip(self._path_etr, msg='Enter the path to the .out file', delay=0.5)
        self._open_btn = tk.Button(self._mainframe, text='Open', command=self.load_outlook)

        # set up grid
        self._mainframe.grid(row=0, column=0)
        self._path_etr.grid(row=0, column=0)
        self._open_btn.grid(row=0, column=1)

    def load_outlook(self):
        self.master.load_outlook(self._path.get())
        self.destroy()


class StartupFrame(tk.Frame):
    def __init__(self, parent, args):
        tk.Frame.__init__(self, parent)

        # widgets
        new_btn = ttk.Button(self, text='New Outlook', command=lambda: parent.switch_frame(OutlookFrame))
        ToolTip(new_btn, msg="Opens a new outlook for editing", delay=0.5)
        load_btn = ttk.Button(self, text='Load Outlook', command=lambda: parent.open_load())
        ToolTip(load_btn, msg="Loads an existing outlook for editing", delay=0.5)

        # TODO: it seems this would be better sent as arguments to the toggle pane?
        features_tpane = TogglePane(self, label='Features')
        features_details = 'Save Outlook: Allows you to save an outlook for\n   future editing.\n\n' \
                           'Load Outlook: Loads a previous outlook editing.\n\n' \
                           'Tool Tips: Hover over a button or field to learn\n  more about it.'
        features_txt = tk.Text(features_tpane.frame, height=7, width=52)
        features_txt.grid(row=0, column=0)
        features_txt.insert(tk.END, features_details)
        features_txt.configure(state='disabled')

        self.grid(column=0, row=0)
        self.grid_rowconfigure(2, minsize=50)
        self.grid_rowconfigure(3, minsize=50)
        self.grid_columnconfigure(1, minsize=500)
        new_btn.grid(column=1, row=1)
        load_btn.grid(column=1, row=2)
        features_tpane.grid(column=1, row=3)


class OutlookFrame(tk.Frame):
    def __init__(self, master, args):
        tk.Frame.__init__(self, master)

        self.salary = args[0]
        self.rate = args[1]
        self.years = args[2]

        # perform initial calculation
        self._calculate()

        # set up widgets
        self._salary_lbl = ttk.Label(self, text='Salary')
        self._salary_etr = tk.Entry(self, width=10, textvariable=self.salary)
        ToolTip(self._salary_etr, msg='Yearly salary', delay=0.5)
        self._rate_lbl = ttk.Label(self, text='Savings Rate')
        self._rate_etr = tk.Entry(self, width=10, textvariable=self.rate)
        ToolTip(self._rate_etr, msg='Savings rate of salary', delay=0.5)
        self._years_lbl = ttk.Label(self, text='Years to Retirement')
        self._years_etr = tk.Entry(self, width=10, textvariable=self.years)
        ToolTip(self._years_etr, msg='Estimated number of years', delay=0.5)
        self._tutorial_btn = ttk.Button(self, text='Open tutorial', command=master.open_tutorial)
        self._save_btn = ttk.Button(self, text='Save', command=master.open_save)
        ToolTip(self._save_btn, msg='Opens the save dialog window', delay=0.5)
        self._refresh_btn = ttk.Button(self, text='Refresh', command=self._refresh)
        ToolTip(self._refresh_btn, msg='Resets all fields to their original values', delay=0.5)

        self._figure = Figure(figsize=(5, 5), dpi=100)
        self._plot = self._figure.add_subplot(111)
        self._plot.plot(self._y)
        self._canvas = FigureCanvasTkAgg(self._figure, master=self)
        self._canvas.draw()

        # grid time
        self._salary_lbl.grid(row=0, column=0, sticky='E')
        self._salary_etr.grid(row=0, column=1)
        self._rate_lbl.grid(row=1, column=0, sticky='E')
        self._rate_etr.grid(row=1, column=1)
        self._years_lbl.grid(row=2, column=0, sticky='E')
        self._years_etr.grid(row=2, column=1)
        self._tutorial_btn.grid(row=3, column=0)
        self._save_btn.grid(row=4, column=0)
        self._refresh_btn.grid(row=4, column=1)
        self._canvas.get_tk_widget().grid(row=0, column=2, rowspan=5)

    def _calculate(self):
        self._y = [i**2 for i in range(101)]

    def _refresh(self):
        self._salary.set(70000.00)
        self._rate.set(4.99)
        self._years.set(35)


class TutorialWindow(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title('Tutorial')
        self.geometry('400x500')

        # set up frames
        self.mainframe = ttk.Frame(self, padding='3 3 3 3')

        # set up widgets
        self._time_lbl = ttk.Label(self.mainframe, text='Estimated time to complete: 15 minutes')
        self._steps_lbl = ttk.Label(self.mainframe,
                                    text='Step 1: Editing your salary\n'
                                         'Double click the default salary in the text box to overwrite it with your'
                                         ' salary.\n\n'
                                         'Step 2: Editing your savings rate.\n'
                                         'Double click the default salary in the text box to overwrite it with your'
                                         ' expected savings rate.\n\n'
                                         'Step 3: Edit your years to retirement.\n'
                                         'Double click the default number in the text box and fill in your expected'
                                         ' years to retirement.\n\n'
                                         'Step 4: Saving an outlook\n'
                                         'Clicking the save button will bring up a dialog box requesting a save'
                                         ' location. Please enter your desired location and click on the Save button.'
                                         '\n\n'
                                         'Step 5: Refreshing an Outlook\n'
                                         'Clicking this button will reset the outlook either to the default values or'
                                         ' to the values in your saved Outlook.')

        # set up grid
        self.mainframe.grid(row=0, column=0)
        self._time_lbl.grid(row=1, column=0, sticky='W')
        self._steps_lbl.grid(row=2, column=0, sticky='W')


class TogglePane(ttk.Frame):
    def __init__(self, parent, label, expanded_text='-', collapsed_text='+'):
        ttk.Frame.__init__(self, parent)

        self.parent = parent
        self.frame = ttk.Frame(self, borderwidth=2, relief='sunken')
        self._label = label
        self._expanded_text = expanded_text
        self._collapsed_text = collapsed_text

        # make a label
        self._lbl = ttk.Label(self, text=self._label)

        # make the button and tie it to a boolean
        self._open = tk.BooleanVar()
        self._btn = ttk.Checkbutton(self, variable=self._open, command=self._activate, style='TButton')

        # grid time
        self.grid(row=0, column=0)
        self._lbl.grid(row=0, column=0, sticky='E')
        self._btn.grid(row=0, column=1, sticky='W')

        self._activate()

    def _activate(self):
        print(f'activate: self._open is {self._open.get()}')
        if not self._open.get():
            self.frame.grid_forget()
            self._btn.configure(text=self._collapsed_text)
        elif self._open.get():
            self.frame.grid(row=1, column=0, columnspan=2)
            self._btn.configure(text=self._expanded_text)


class SocketManager():
    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 54290

    def send_over_socket(self, data):
        print(f"socket manager is sending: {data}")
        data_json = json.dumps(data)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.HOST, self.PORT))
            s.sendall(bytes(data_json, encoding="utf=8"))

            response = s.recv(1024)
            response = response.decode("utf=8")
            response = json.loads(response)

        print(f"socket manager received: {response}")
        print(f"type is {type(response)}")
        return response


if __name__ == '__main__':
    root = RootWindow()
    root.mainloop()
