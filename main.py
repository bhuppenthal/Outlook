import tkinter as tk
from tkinter import ttk
from tktooltip import ToolTip
# import numpy
import matplotlib
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
        'init_value': 70000,
        'type': 'd',
        'text_lbl': 'Salary',
        'text_tip': 'Current yearly salary',
        'width': 10
    },
    {
        'name': 'contribution',
        'init_value': '10',
        'type': 'd',
        'text_lbl': 'Contribution Rate',
        'text_tip': 'Contribution rate of salary',
        'width': 10
    },
    {
        'name': 'increase',
        'init_value': '2',
        'type': 'd',
        'text_lbl': 'Annual Raise',
        'text_tip': 'Estimated rate of salary increase annually',
        'width': '10'
    },
    {
        'name': 'years',
        'init_value': 25,
        'type': 'i',
        'text_lbl': 'Years to Retirement',
        'text_tip': 'Estimated number of years to retirement',
        'width': 10
    },
    {
        'name': 'balance',
        'init_value': '25000',
        'type': 'd',
        'text_lbl': 'Currentl Balance',
        'text_tip': 'Current 401k balance',
        'width': 10
    },
    {
        'name': 'return_rate',
        'init_value': '6.5',
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
        # automatically set attributes!!
        self.default_act_vars = INIT_VALS

        self.act_vars = {'salary': tk.DoubleVar(master=self),
                         'contribution': tk.DoubleVar(master=self),
                         'increase': tk.DoubleVar(master=self),
                         'years': tk.IntVar(master=self),
                         'balance': tk.DoubleVar(master=self),
                         'return_rate': tk.DoubleVar(master=self)}
        self.act_vars['salary'].set(INIT_VALS['salary'])
        self.act_vars['salary'].trace('w', self._trigger_render)
        self.act_vars['contribution'].set(INIT_VALS['contribution'])
        self.act_vars['contribution'].trace('w', self._trigger_render)
        self.act_vars['increase'].set(INIT_VALS['increase'])
        self.act_vars['increase'].trace('w', self._trigger_render)
        self.act_vars['years'].set(INIT_VALS['years'])
        self.act_vars['years'].trace('w', self._trigger_render)
        self.act_vars['balance'].set(INIT_VALS['balance'])
        self.act_vars['balance'].trace('w', self._trigger_render)
        self.act_vars['return_rate'].set(INIT_VALS['return_rate'])
        self.act_vars['return_rate'].trace('w', self._trigger_render)

        self.socket_manager = SocketManager()

    def set_vars_default(self):
        self.act_vars['salary'].set(self.default_act_vars['salary'])
        self.act_vars['contribution'].set(self.default_act_vars['contribution'])
        self.act_vars['increase'].set(self.default_act_vars['increase'])
        self.act_vars['years'].set(self.default_act_vars['years'])
        self.act_vars['balance'].set(self.default_act_vars['balance'])
        self.act_vars['return_rate'].set(self.default_act_vars['return_rate'])

    def switch_frame(self, frame_class):
        if frame_class is OutlookFrame:
            new_frame = frame_class(self, self.act_vars)
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

        self.default_act_vars = response['info']
        self.act_vars['salary'].set(self.default_act_vars['salary'])
        self.act_vars['contribution'].set(self.default_act_vars['contribution'])
        self.act_vars['increase'].set(self.default_act_vars['increase'])
        self.act_vars['years'].set(self.default_act_vars['years'])
        self.act_vars['balance'].set(self.default_act_vars['balance'])
        self.act_vars['return_rate'].set(self.default_act_vars['return_rate'])

        self.switch_frame(OutlookFrame)

    def get_outlook(self):
        return {'salary': self.act_vars['salary'].get(),
                'contribution': self.act_vars['contribution'].get(),
                'increase': self.act_vars['increase'].get(),
                'years': self.act_vars['years'].get(),
                'balance': self.act_vars['balance'].get(),
                'return_rate': self.act_vars['return_rate'].get()}

    def set_outlook(self, load_dict):
        ...

    def _trigger_render(self, *args):
        self._frame.render_graph()

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
        self.btn_frame = ttk.Frame(self, padding="5 5 5 5")
        self.act_frame = ttk.Frame(self, padding="5 5 5 5")
        self.graph_frame = ttk.Frame(self)

        self.salary = args['salary']
        self.contribution = args['contribution']
        self.increase = args['increase']
        self.years = args['years']
        self.balance = args['balance']
        self.return_rate = args['return_rate']

        self.set_up_widgets()
        self.set_up_grid()

    def set_up_widgets(self):
        self._figure = None
        self._canvas = None
        # set up widgets
        self._salary_lbl = ttk.Label(self.act_frame , text='Salary')
        self._salary_etr = tk.Entry(self.act_frame , width=10, textvariable=self.salary)
        ToolTip(self._salary_etr, msg='Yearly salary', delay=0.5)

        self._contribution_lbl = ttk.Label(self.act_frame , text='Contribution Rate')
        self._contribution_etr = tk.Entry(self.act_frame , width=10, textvariable=self.contribution)
        ToolTip(self._contribution_etr, msg='Contribution rate of salary', delay=0.5)

        self._increase_lbl = ttk.Label(self.act_frame , text='Annual Salary Increase')
        self._increase_etr = tk.Entry(self.act_frame , width=10, textvariable=self.increase)
        ToolTip(self._increase_etr, msg='Estimated increase of salary annually', delay=0.5)

        self._years_lbl = ttk.Label(self.act_frame , text='Years to Retirement')
        self._years_etr = tk.Entry(self.act_frame , width=10, textvariable=self.years)
        ToolTip(self._years_etr, msg='Estimated number of years', delay=0.5)

        self._balance_lbl = ttk.Label(self.act_frame , text='Balance')
        self._balance_etr = tk.Entry(self.act_frame , width=10, textvariable=self.balance)
        ToolTip(self._balance_etr, msg='Current balance', delay=0.5)

        self._return_lbl = ttk.Label(self.act_frame , text='Expected Rate of Return')
        self._return_etr = tk.Entry(self.act_frame , width=10, textvariable=self.return_rate)
        ToolTip(self._return_etr, msg='Expected rate of return', delay=0.5)

        self._tutorial_btn = ttk.Button(self.btn_frame , text='Open tutorial', command=self.master.open_tutorial)

        self._save_btn = ttk.Button(self.btn_frame , text='Save', command=self.master.open_save)
        ToolTip(self._save_btn, msg='Opens the save dialog window', delay=0.5)

        self._refresh_btn = ttk.Button(self.btn_frame , text='Refresh', command=self._refresh)
        ToolTip(self._refresh_btn, msg='Resets all fields to their original values', delay=0.5)

        self._back_btn = ttk.Button(self.btn_frame , width=10, text='Back',command=lambda: self.master.switch_frame(StartupFrame))
        ToolTip(self._back_btn, msg='Return to the opening page', delay=0.5)

    def set_up_grid(self):
        self._salary_lbl.grid(row=1, column=0, sticky='W')
        self._salary_etr.grid(row=2, column=0)
        self._contribution_lbl.grid(row=3, column=0, sticky='W')
        self._contribution_etr.grid(row=4, column=0)
        self._increase_lbl.grid(row=5, column=0, sticky='W')
        self._increase_etr.grid(row=6, column=0)
        self._years_lbl.grid(row=7, column=0, sticky='W')
        self._years_etr.grid(row=8, column=0)
        self._balance_lbl.grid(row=9, column=0, sticky='W')
        self._balance_etr.grid(row=10, column=0)
        self._return_lbl.grid(row=11, column=0, sticky='W')
        self._return_etr.grid(row=12, column=0)

        self._back_btn.grid(row=0, column=0, sticky='NW', pady=10)
        self._tutorial_btn.grid(row=1, column=0, columnspan=2)
        self._save_btn.grid(row=2, column=0, padx=2, pady=5)
        self._refresh_btn.grid(row=2, column=1, padx=2, pady=5)

        self.btn_frame.grid(row=0, column=0)
        self.act_frame.grid(row=1, column=0)
        self.act_frame.rowconfigure(0, minsize=100)
        self.act_frame.rowconfigure(13, minsize=100)
        self.graph_frame.grid(row=0, column=1, rowspan=2)

        # create the widget and stuff
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
        ax.set_xlim(0, self.years.get()+1)
        ax.set_ylim(0, max(self._y)*1.1)
        self._canvas.draw()

    def _calculate(self):
        starting_salary = self.salary.get()
        contribution = self.contribution.get()/100 + 1
        increase = self.increase.get()/100 + 1
        years = self.years.get()
        starting_balance = self.balance.get()
        return_rate = self.return_rate.get()/100 + 1

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
