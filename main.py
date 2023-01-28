import tkinter as tk
from tkinter import ttk
from tktooltip import ToolTip
import numpy
import matplotlib


class StartupWindow:
    def __init__(self, parent):
        self.parent = parent

        mainframe = ttk.Frame(self.parent, padding='3 3 3 3')

        # new outlook button
        new_btn = ttk.Button(mainframe, text='New Outlook', command=self._open_outlook)
        ToolTip(new_btn, msg="Opens a new outlook for editing.", delay=0.5)

        # load outlook button
        load_btn = ttk.Button(mainframe, text='Load Outlook')
        ToolTip(load_btn, msg="Loads an existing outlook for editing", delay=0.5)

        features_tpane = TogglePane(mainframe, label='Features')
        features_details = 'We have implemented some cool new features...'
        features_txt = tk.Text(features_tpane.frame, height=5, width=52)
        features_txt.grid(row=0, column=0)
        features_txt.insert(tk.END, features_details)
        features_txt.configure(state='disabled')

        mainframe.grid(column=0, row=0)
        mainframe.grid_columnconfigure(0, minsize=200)
        mainframe.grid_columnconfigure(2, minsize=200)
        new_btn.grid(column=1, row=1)
        load_btn.grid(column=1, row=2)
        features_tpane.grid(column=1, row=3)

    def _open_outlook(self):
        outlookWindow = OutlookWindow(self.parent)
        outlookWindow.title('Edit an outlook')
        outlookWindow.geometry('500x500')


class OutlookWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # set up frames
        self.mainframe = ttk.Frame(self, padding='3 3 3 3')

        # set up widgets
        self._salary_lbl = ttk.Label(self.mainframe, text='Salary')
        self._salary = tk.StringVar()
        self._salary_etr = tk.Entry(self.mainframe, width=10, textvariable=self._salary)
        self._rate_lbl = ttk.Label(self.mainframe, text='Savings Rate')
        self._rate = tk.StringVar()
        self._rate_etr = tk.Entry(self.mainframe, width=10, textvariable=self._rate)
        self._years_lbl = ttk.Label(self.mainframe, text='Years to Retirement')
        self._years = tk.StringVar()
        self._years_etr = tk.Entry(self.mainframe, width=10, textvariable=self._years)

        # grid time
        self.mainframe.grid(row=0, column=0)
        self._salary_lbl.grid(row=1, column=0, sticky='E')
        self._salary_etr.grid(row=1, column=1)
        self._rate_lbl.grid(row=2, column=0, sticky='E')
        self._rate_etr.grid(row=2, column=1)
        self._years_lbl.grid(row=3, column=0, sticky='E')
        self._years_etr.grid(row=3, column=1)


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
        self._lbl.grid(row=0, column=0, sticky='W')
        self._btn.grid(row=0, column=1)

        self._activate()

    def _activate(self):
        print(f'activate: self._open is {self._open.get()}')
        if not self._open.get():
            self.frame.grid_forget()
            self._btn.configure(text=self._collapsed_text)
        elif self._open.get():
            self.frame.grid(row=1, column=0, columnspan=2)
            self._btn.configure(text=self._expanded_text)


# main application window
root = tk.Tk()
root.title('Outlook')
StartupWindow(root)
root.mainloop()
