import tkinter as tk
from tkinter import ttk
from tktooltip import ToolTip
from matplotlib.figure import Figure
import matplotlib.pyplot as pltlib
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import json
import socket
from configuration import ACT, TUTORIAL, FEATURES


class RootWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title('Outlook')

        self.set_up_frames()
        self.set_up_variables()
        self.set_up_grid()

    def set_up_frames(self):
        self._frame = StartupFrame(self, {})
        self._tutorial_window = None
        self._load_window = None

    def set_up_variables(self):
        """Set up the root window variables and open the socket."""

        def tk_var(self, act_v):
            if act_v['type'] == 'i':
                var = tk.IntVar(master=self)
            else:
                var = tk.DoubleVar(master=self)
            var.set(act_v['init_val'])
            var.trace('w', self._trigger_render)
            return var

        self.tk_vars = {var['name']: tk_var(self, var) for var in ACT}
        self.default_vals = {var['name']: var['init_val'] for var in ACT}
        self.socket_manager = SocketManager()

    def set_up_grid(self):
        self._frame.grid(row=0, column=0)

    def switch_frame(self, frame_class):
        """Change the displayed frame to the parameter frame_class."""
        if frame_class is OutlookFrame:
            new_frame = frame_class(self, self.tk_vars)
        else:
            new_frame = frame_class(self, [])
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
        self.socket_manager.send_over_socket(save_dict)

    def load_outlook(self, path):
        load_dict = {'path': path,
                     'action': 'load',
                     'info': None}
        response = self.socket_manager.send_over_socket(load_dict)
        self.default_vals = {k: v for k, v in response['info'].items()}
        self.set_vars_default()
        self.switch_frame(OutlookFrame)

    def get_outlook(self):
        return {k: v.get() for k, v in self.tk_vars.items()}

    def _trigger_render(self, *args):
        self._frame.render_graph()

    def set_vars_default(self):
        for key in self.tk_vars:
            self.tk_vars[key].set(self.default_vals[key])


class SaveWindow(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title('Save an outlook')
        self.geometry('500x50')

        self.set_up_frames()
        self.set_up_variables()
        self.set_up_widgets()
        self.set_up_grid()

    def set_up_frames(self):
        self._mainframe = ttk.Frame(self, padding='5 5 5 5')

    def set_up_variables(self):
        self._path = tk.StringVar()
        self._path.set('/home/brenda/python_projects/cs361-outlook/')

    def set_up_widgets(self):
        self._warn_lbl = tk.Label(self._mainframe, text='Warning! This will overwrite data at the path you specify.')
        self._path_etr = tk.Entry(self._mainframe, width=55, textvariable=self._path)
        ToolTip(self._path_etr, msg='Enter the path to save the .out file', delay=0.5)
        self._save_btn = tk.Button(self._mainframe, text='Save', command=self.save_outlook)

    def set_up_grid(self):
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

        self.set_up_frames()
        self.set_up_variables()
        self.set_up_widgets()
        self.set_up_grid()

    def set_up_frames(self):
        self._mainframe = ttk.Frame(self, padding='5 5 5 5')

    def set_up_variables(self):
        self._path = tk.StringVar()
        self._path.set('/home/brenda/python_projects/cs361-outlook/')

    def set_up_widgets(self):
        self._path_etr = tk.Entry(self._mainframe, width=55, textvariable=self._path)
        ToolTip(self._path_etr, msg='Enter the path to the .out file', delay=0.5)
        self._open_btn = tk.Button(self._mainframe, text='Open', command=self.load_outlook)

    def set_up_grid(self):
        self._mainframe.grid(row=0, column=0)
        self._path_etr.grid(row=0, column=0)
        self._open_btn.grid(row=0, column=1)

    def load_outlook(self):
        self.master.load_outlook(self._path.get())
        self.destroy()


class StartupFrame(tk.Frame):
    def __init__(self, master, args):
        tk.Frame.__init__(self, master)

        self.set_up_widgets()
        self.set_up_grid()

    def set_up_widgets(self):
        self.new_btn = ttk.Button(self,
                                  text='New Outlook',
                                  command=lambda: self.master.switch_frame(OutlookFrame))
        ToolTip(self.new_btn,
                msg="Opens a new outlook for editing", delay=0.5)

        self.load_btn = ttk.Button(self,
                                   text='Load Outlook',
                                   command=lambda: self.master.open_load())
        ToolTip(self.load_btn,
                msg="Loads an existing outlook for editing", delay=0.5)

        self.features_tpane = TogglePane(self, label='Features')

        self.features_details = FEATURES
        self.features_txt = tk.Text(self.features_tpane.frame,
                                    height=7,
                                    width=52)
        self.features_txt.insert(tk.END, self.features_details)
        self.features_txt.configure(state='disabled')

    def set_up_grid(self):
        self.grid(column=0, row=0)
        self.grid_rowconfigure(2, minsize=50)
        self.grid_rowconfigure(3, minsize=50)
        self.grid_columnconfigure(1, minsize=500)

        self.features_txt.grid(row=0, column=0)
        self.new_btn.grid(column=1, row=1)
        self.load_btn.grid(column=1, row=2)
        self.features_tpane.grid(column=1, row=3)


class OutlookFrame(tk.Frame):
    def __init__(self, master, args):
        tk.Frame.__init__(self, master)

        self.tk_vars = args
        self.set_up_frames()
        self.set_up_widgets()
        self.set_up_grid()

    def set_up_frames(self):
        self.btn_frame = ttk.Frame(self, padding="5 5 5 5")
        self.act_frame = ttk.Frame(self, padding="5 5 5 5")
        self.graph_frame = ttk.Frame(self)

    def set_up_widgets(self):
        self._figure = None
        self._canvas = None
        self.act_widgets()
        self.button_widgets()

    def act_widgets(self):
        def new_widgets(self, act_dict):
            label = ttk.Label(self.act_frame, text=act_dict['text_lbl'])
            entry = tk.Entry(self.act_frame,
                             width=act_dict['width'],
                             textvariable=self.tk_vars[act_dict['name']])
            ToolTip(entry, msg=act_dict['text_tip'], delay=0.5)
            return {'label': label, 'entry': entry}

        self._act_widgets = [new_widgets(self, act_dict) for act_dict in ACT]

    def button_widgets(self):
        self._tutorial_btn = ttk.Button(self.btn_frame,
                                        text='Open tutorial',
                                        command=self.master.open_tutorial)
        
        self._save_btn = ttk.Button(self.btn_frame,
                                    text='Save',
                                    command=self.master.open_save)
        ToolTip(self._save_btn, msg='Opens the save dialog window', delay=0.5)

        self._refresh_btn = ttk.Button(self.btn_frame,
                                       text='Refresh',
                                       command=self._refresh)
        ToolTip(self._refresh_btn,
                msg='Resets all fields to their original values', delay=0.5)

        self._back_btn = ttk.Button(self.btn_frame,
                                    width=10,
                                    text='Back',
                                    command=lambda:
                                        self.master.switch_frame(StartupFrame))
        ToolTip(self._back_btn,
                msg='Return to the opening page', delay=0.5)

    def set_up_grid(self):
        self.grid_act_widgets()
        self.grid_buttons()
        self.grid_graph()

    def grid_act_widgets(self):
        for i in range(0, len(self._act_widgets)):
            widgets = self._act_widgets[i]
            widgets['label'].grid(row=2*i, column=0, sticky='W')
            widgets['entry'].grid(row=2*i+1, column=0)

    def grid_buttons(self):
        self._back_btn.grid(row=0, column=0, sticky='NW')
        self._tutorial_btn.grid(row=1, column=0, columnspan=2, pady=10)
        self._save_btn.grid(row=2, column=0, padx=2, pady=5)
        self._refresh_btn.grid(row=2, column=1, padx=2, pady=5)

        self.btn_frame.grid(row=0, column=0, sticky='N')
        self.act_frame.grid(row=1, column=0, sticky='N')
        self.graph_frame.grid(row=0, column=1, rowspan=2)

    def grid_graph(self):
        self._calculate()
        self._canvas = pltlib.figure(1)
        self._figure = Figure(figsize=(5, 5), dpi=100)
        self._figure_sub_plot = self._figure.add_subplot(111)
        self._line1, = self._figure_sub_plot.plot(self._x, self._y, '-r')
        self._canvas = FigureCanvasTkAgg(self._figure, master=self.graph_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().grid(row=0, column=0)

    def render_graph(self):
        self._calculate()
        self._line1.set_data(self._x, self._y)
        ax = self._canvas.figure.axes[0]
        ax.set_xlim(0, max(self._x)+1)
        ax.set_ylim(0, max(self._y)*1.05)
        self._canvas.draw()

    def _calculate(self):
        starting_salary = self.tk_vars['salary'].get()
        contribution = self.tk_vars['contribution'].get()/100
        increase = self.tk_vars['increase'].get()/100 + 1
        years = self.tk_vars['years'].get()
        starting_balance = self.tk_vars['balance'].get()
        return_rate = self.tk_vars['return_rate'].get()/100 + 1

        salary = [starting_salary]
        balance = [starting_balance]
        for i in range(years):
            salary.append(salary[i]*increase)
            balance.append(balance[i]*return_rate + salary[i]*contribution)

        self._x = [i for i in range(years+1)]
        self._y = balance

    def _refresh(self):
        self.master.set_vars_default()
        self.render_graph()


class TutorialWindow(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.title('Tutorial')
        self.geometry('500x300')

        self.mainframe = ttk.Frame(self, padding='3 3 3 3')
        self.set_up_widgets()
        self.set_up_grid()

    def set_up_widgets(self):
        self._time_lbl = ttk.Label(self.mainframe,
                                   text='Estimated time to complete: 15 mins')
        self._steps_lbl = ttk.Label(self.mainframe,
                                    text=TUTORIAL,
                                    wraplength=500)

    def set_up_grid(self):
        self.mainframe.grid(row=0, column=0)
        self._time_lbl.grid(row=1, column=0, sticky='W')
        self._steps_lbl.grid(row=2, column=0, sticky='W')


class TogglePane(ttk.Frame):
    def __init__(self, master, label, expanded_text='-', collapsed_text='+'):
        ttk.Frame.__init__(self, master)

        self._label = label
        self._expanded_text = expanded_text
        self._collapsed_text = collapsed_text

        self.set_up_frames()
        self.set_up_widgets()
        self.set_up_grid()

        self._activate()

    def set_up_frames(self):
        self.frame = ttk.Frame(self, borderwidth=2, relief='sunken')

    def set_up_widgets(self):
        self._lbl = ttk.Label(self, text=self._label)

        self._open = tk.BooleanVar()
        self._btn = ttk.Checkbutton(self,
                                    variable=self._open,
                                    command=self._activate,
                                    style='TButton')

    def set_up_grid(self):
        self.grid(row=0, column=0)
        self._lbl.grid(row=0, column=0, sticky='E')
        self._btn.grid(row=0, column=1, sticky='W')

    def _activate(self):
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


def _quit():
    print('quitting app')
    root.quit()
    root.destroy()


if __name__ == '__main__':
    root = RootWindow()
    root.protocol('WM_DELETE_WINDOW', _quit)
    root.mainloop()
