import tkinter as tk
from tkinter import ttk
from tktooltip import ToolTip
# import numpy
# import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as pltlib
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import json
import socket

INIT_VALS = {'salary': 70000,
             'contribution': 10,
             'increase': 3,
             'years': 35,
             'balance': 20000,
             'return_rate': 6.5}

ACT = [
    {
        'name': 'salary',
        'init_val': 70000,
        'type': 'd',
        'text_lbl': 'Salary',
        'text_tip': 'Current yearly salary',
        'width': 10
    },
    {
        'name': 'contribution',
        'init_val': 10,
        'type': 'd',
        'text_lbl': 'Contribution Rate',
        'text_tip': 'Contribution rate of salary',
        'width': 10
    },
    {
        'name': 'increase',
        'init_val': 2,
        'type': 'd',
        'text_lbl': 'Annual Raise',
        'text_tip': 'Estimated rate of salary increase annually',
        'width': '10'
    },
    {
        'name': 'years',
        'init_val': 25,
        'type': 'i',
        'text_lbl': 'Years to Retirement',
        'text_tip': 'Estimated number of years to retirement',
        'width': 10
    },
    {
        'name': 'balance',
        'init_val': 25000,
        'type': 'd',
        'text_lbl': 'Current Balance',
        'text_tip': 'Current 401k balance',
        'width': 10
    },
    {
        'name': 'return_rate',
        'init_val': 6.5,
        'type': 'd',
        'text_lbl': 'Return Rate',
        'text_tip': 'Expected Rate of Return',
        'width': 10
    }
]


class RootWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.set_up_variables()

        self.title('Outlook')
        self._frame = StartupFrame(self, {})
        self._tutorial_window = None
        self._load_window = None
        self._frame.grid(row=0, column=0)

    def set_up_variables(self):
        def tk_var(self, vtype, init):
            if vtype == 'i':
                var = tk.IntVar(master=self)
            else:
                var = tk.DoubleVar(master=self)
            var.set(init)
            var.trace('w', self._trigger_render)
            return var

        self.tk_vars = {v['name']: tk_var(self, v['type'], v['init_val']) for v in ACT}
        self.default_vals = {var['name']: var['init_val'] for var in ACT}
        self.socket_manager = SocketManager()

    def switch_frame(self, frame_class):
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
        # for every variable in tk_vars, set to value in self.default_vals
        for key in self.tk_vars:
            self.tk_vars[key].set(self.default_vals[key])


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
        self.btn_frame = ttk.Frame(self, padding="5 5 5 5")
        self.act_frame = ttk.Frame(self, padding="5 5 5 5")
        self.graph_frame = ttk.Frame(self)

        # unpack the tk variables into class members
        self.tk_vars = args
        self.set_up_widgets()
        self.set_up_grid()

    def set_up_widgets(self):
        def new_widgets(self, act_dict):
            label = ttk.Label(self.act_frame, text=act_dict['text_lbl'])
            entry = tk.Entry(self.act_frame,
                             width=act_dict['width'],
                             textvariable=self.tk_vars[act_dict['name']])
            ToolTip(entry, msg=act_dict['text_tip'], delay=0.5)
            return {'label': label, 'entry': entry}

        self._figure = None
        self._canvas = None
        self._act_widgets = [new_widgets(self, act_dict) for act_dict in ACT]

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
        for i in range(0, len(self._act_widgets)):
            widgets = self._act_widgets[i]
            widgets['label'].grid(row=2*i, column=0, sticky='W')
            widgets['entry'].grid(row=2*i+1, column=0)

        self._back_btn.grid(row=0, column=0, sticky='NW')
        self._tutorial_btn.grid(row=1, column=0, columnspan=2)
        self._save_btn.grid(row=2, column=0, padx=2, pady=5)
        self._refresh_btn.grid(row=2, column=1, padx=2, pady=5)

        self.btn_frame.grid(row=0, column=0)
        self.act_frame.grid(row=1, column=0)
        self.graph_frame.grid(row=0, column=1, rowspan=2)

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
        contribution = self.tk_vars['contribution'].get()/100 + 1
        increase = self.tk_vars['increase'].get()/100 + 1
        years = self.tk_vars['years'].get()
        starting_balance = self.tk_vars['balance'].get()
        return_rate = self.tk_vars['return_rate'].get()/100 + 1

        salary_at_year = [starting_salary]
        balance_at_year = [starting_balance]
        for i in range(years):
            salary_at_year.append(salary_at_year[i]*increase)
            balance_at_year.append(balance_at_year[i]*return_rate + salary_at_year[i]*contribution)

        self._x = [i for i in range(years+1)]
        self._y = balance_at_year

    def _refresh(self):
        self.master.set_vars_default()
        self.render_graph()


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


def _quit():
    print('quitting app')
    root.quit()
    root.destroy()


if __name__ == '__main__':
    root = RootWindow()
    root.protocol('WM_DELETE_WINDOW', _quit)
    root.mainloop()
