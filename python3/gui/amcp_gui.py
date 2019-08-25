#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - Graphical User Interface

"""

__author__ = "S.Blatter"
__maintainer__ = "S.Blatter"
__email__ = "maveric-@gmx.ch"
__copyright__ = "Copyright 2019"
__credits__ = ""
__license__ = "GPL 3.0"
__status__ = "Developement"
__version__ = "0.1"

import logging
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from python3.amcp_basic import PhaseShiftMethod

logger = logging.getLogger(__name__)


class amcpGUI(PhaseShiftMethod):

    # Variables
    loc_config = '../vnaJ/calibration/'
    loc_java = None
    loc_vnaj = '../vnaJ/vnaJ-hl.3.2.10.jar'
    loc_res = None

    def __init__(self):
        #super.__init__()
        self.run()

    def openFile(self):
        file = askopenfilename(initialdir="/home/battosai/vnaJ.3.3/export",
                               filetypes=(("Comma-Separated Values", "*.csv"), ("All Files", "*.*")),
                               title="Choose a file.")
        logging.debug(file)

        try:
            # with open(name, 'r') as UseFile:
            #     print(UseFile.read())
            self.loc_res = file
            self.loadData(file=file)
            self.calcParameters()
        except OSError:
            print("File not found!")

    def openCalibration(self):
        name = askopenfilename(initialdir="/home/battosai/vnaJ.3.3/export",
                               filetypes=(("VNA Calibration Files", "*.cal"), ("All Files", "*.*")),
                               title="Choose a file.")
        print(name)
        #Using try in case user types in unknown file or closes without choosing a file.
        try:
            with open(name, 'r') as UseFile:
                print(UseFile.read())
        except OSError:
            print("File not found!")

    def plot(self, data=None):
        fig, ax1 = Figure(figsize=(6, 6))

        ax1.plot(data['Frequency(Hz)'], data['Transmission Loss(dB)'], 'b-')
        ax1.set_xlabel('Frequency [f]')
        ax1.set_ylabel('Transmission Loss [dB]', color='b')
        ax1.tick_params('y', colors='b')

        ax2 = ax1.twinx()
        ax2.plot(data['Frequency(Hz)'], data['Phase(deg)'], 'r-')
        ax2.set_ylabel('Phase [deg]', color='r')
        ax2.tick_params('y', colors='r')

        #fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.get_tk_widget().pack()
        canvas.draw()

    def exitProgram(self):
        exit()

    def tabResults(self, nb, R1, C1, L1, C0, Q):

        def getResults(*args):
            self.loadData(file='/home/battosai/vnaJ.3.3/export/step1.csv')
            self.calcParameters()

            R1.set(round(self.Rm, 1))
            C1.set(round(self.Cm * 1e15, 1))
            L1.set(round(self.Lm * 1e3, 1))
            C0.set(round(self.C0 * 1e12, 1))
            Q.set(round(self.Q))

        tab = ttk.Frame(nb, padding="10 10 10 10")
        nb.add(tab, text='Results')

        #left frame
        #leftFrame = tk.Frame(tab, width=400, height=600).grid(row=0, column=0, padx=10, pady=10)
        tk.Label(tab, text='XTAL Model').grid(column=0, row=0, sticky=tk.N)

        try:

            self.img_xtal = tk.PhotoImage(file='images/fixture1.gif')
            tk.Label(tab, image=self.img_xtal).grid(column=0, row=1, rowspan=6, padx=10, pady=10)

        except:
            print("Image not found")

        # #right frame
        #rightFrame = tk.Frame(tab, width=400, height=600).grid(row=0, column=0, padx=10, pady=2)


        tk.Label(tab, text='Measurement Results:').grid(column=1, columnspan=2, row=0, sticky=tk.N)
        tk.Label(tab, text='R1 [Ohm] =').grid(column=1, row=1, sticky=tk.E)
        tk.Label(tab, text='C1 [fF] =').grid(column=1, row=2, sticky=tk.E)
        tk.Label(tab, text='L1 [mH] =').grid(column=1, row=3, sticky=tk.E)
        tk.Label(tab, text='C0 [pF] =').grid(column=1, row=4, sticky=tk.E)
        tk.Label(tab, text='Q =').grid(column=1, row=5, sticky=tk.E)
        tk.Label(tab, textvariable=R1).grid(column=2, row=1, sticky=tk.E)
        tk.Label(tab, textvariable=C1).grid(column=2, row=2, sticky=tk.E)
        tk.Label(tab, textvariable=L1).grid(column=2, row=3, sticky=tk.E)
        tk.Label(tab, textvariable=C0).grid(column=2, row=4, sticky=tk.E)
        tk.Label(tab, textvariable=Q).grid(column=2, row=5, sticky=tk.E)

        ttk.Button(tab, text="Start Measurement", command=getResults).grid(column=1, columnspan=2, row=6, sticky=tk.S)



    def tabSetup(self, nb):
        tab = ttk.Frame(nb, padding="3 3 12 12")
        nb.add(tab, text='Setup')

        ttk.Label(tab, text='miniVNA Calibration file: ').grid(column=0, row=0, sticky=tk.E)
        ttk.Label(tab, textvariable=self.loc_config).grid(column=1, row=0, sticky=tk.W)

    def tabPlot(self, nb):
        tab = ttk.Frame(nb, padding="3 3 12 12")
        nb.add(tab, text='Plot')

        lbl1 = tk.Label(tab, text='label3')
        lbl1.grid(column=1, row=0)

    # run gui
    def run(self):

        def getResults(*args):
            self.loadData(file='/home/battosai/vnaJ.3.3/export/step1.csv')
            self.calcParameters()

        self.master = tk.Tk()
        self.master.title("ampc - v0.1")
        self.master.geometry('800x600')

        #define Menu items
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        # File Items
        fileMenu = tk.Menu(menu)
        fileMenu.add_command(label="Open File", command=self.openFile)
        fileMenu.add_command(label="Exit", command=self.exitProgram)
        menu.add_cascade(label="File", menu=fileMenu)

        #VNA Items
        vnaMenu = tk.Menu(menu)
        vnaMenu.add_command(label="Connect VNA")
        vnaMenu.add_command(label="Load Calibration File", command=self.openCalibration)
        vnaMenu.add_command(label="Close VNA")
        menu.add_cascade(label="VNA", menu=vnaMenu)

        # variables
        R1 = tk.StringVar()
        C1 = tk.StringVar()
        L1 = tk.StringVar()
        C0 = tk.StringVar()
        Q = tk.StringVar()

        #getResults()
        R1.set(0.00)
        C1.set(0.00)
        L1.set(0.00)
        C0.set(0.00)
        Q.set(0.00)

        # frame
        nb = ttk.Notebook(self.master)

        self.tabResults(nb=nb, R1=R1, C1=C1, L1=L1, C0=C0, Q=Q)
        self.tabSetup(nb=nb)
        self.tabPlot(nb=nb)

        nb.pack(expand=1, fill='both')

        self.master.mainloop()




if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    gui = amcpGUI()
    #gui.run()



