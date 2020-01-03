#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - GUI Main

This class implements the QT5 GUI. The gui is designed in QT Designer 5 and its design files are included for easy
modification. The gui can be updated using QT designer and then converted to python using:

>> pyuic5 amcp_test.ui -o amcpg.py

For some reason the conversion screws up the import of the resource management. Therefore the last line needs manual
editing (replace "import resource_rc" with "import python3.gui.resource_rc")
if the image resources are changed they too need to be converted:

>> pyrcc5 resources.qrc -o resource_rc.py
"""

__author__ = "S.Blatter"
__maintainer__ = "S.Blatter"
__email__ = "maveric-@gmx.ch"
__copyright__ = "Copyright 2019"
__credits__ = ""
__license__ = "GPL 3.0"
__status__ = "Developement"
__version__ = "0.1"

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QPushButton
import pyqtgraph as pg
import logging
import sys
import python3.gui.amcpg as amcp_gui
import pandas as pd
import serial
import serial.tools.list_ports

#import VNA wrapper
from python3.amcp_main import amcp
from python3.vnaj_wrapper import vnajWrapper

class AmcpGui(QtWidgets.QMainWindow, amcp_gui.Ui_MainWindow):

    C0 = 0
    C1 = 0
    L1 = 0
    R1 = 0
    devs = []
    vna_type = ''
    minivna_port = None
    minivna_baud = 9600
    nanovna_port = None
    nanovna_baud = 9600
    vna = None


    def __init__(self, parent=None):
        super(AmcpGui, self).__init__(parent)
        self.setupUi(self)

        # graph initialisation
        self.pen2 = pg.mkPen(color=(0, 0, 200), width=2)
        self.pen1 = pg.mkPen(color=(200, 0, 0), width=2)
        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y=True, alpha=1)

        # COM ports
        self.update_comports()
        self.update_baud()

        #select VNA
        self.update_vna()

    def update_comports(self):
        devs = set([i[0] for i in list(serial.tools.list_ports.comports())])
        tmp = [item for item in set(self.devs) if not item in devs]  # list of changed ports
        logging.info('COM port list changes: {}'.format(tmp))
        for dev in tmp:
            if dev in self.devs:
                self.update_log(text='COM port removed: {}'.format(dev))

        tmp = [item for item in devs if not item in set(self.devs)]  # list of changed ports
        logging.info('COM port list changes: {}'.format(tmp))
        for dev in tmp:
            if dev in devs:
                self.update_log(text='New COM port found: {}'.format(dev))

        if not devs:
            self.devs = ['-']
        else:
            self.devs = devs

        self.sel_minivna_port.clear()
        self.sel_nanovna_port.clear()
        self.sel_minivna_port.addItems(self.devs)
        self.sel_nanovna_port.addItems(self.devs)
        self.minivna_port = self.sel_minivna_port.currentText()
        self.nanovna_port = self.sel_nanovna_port.currentText()
        self.update()

    def update_baud(self):
        self.minivna_baud = int(self.sel_minivna_baud.currentText())
        self.nanovna_port = int(self.sel_nanovna_baud.currentText())

    def update_vna(self):
        self.vna_type = self.select_vna.currentText()

    def connect_vna(self):
        if self.vna_type == 'MiniVNA':
            logging.info('not implemented')
        elif self.vna_type == 'NanoVNA':
            logging.info('not implemented')

    def disconnect_vna(self):
        if self.vna_type == 'MiniVNA':
            logging.info('not implemented')
        elif self.vna_type == 'NanoVNA':
            logging.info('not implemented')

    def run_measurement(self):
        logging.debug('running measurement')

        # update progressbar 0%
        self.progressBar.setValue(0)

        # Measurement Setup
        fmin = self.f_min.text()
        fmax = self.f_max.text()
        self.update_log('f_min={}\nf_max={}'.format(fmin, fmax))

        self.update_log('starting measurement using {}'.format(self.vna_type))
        self.update_results()

        # run measurement
        if self.select_vna.currentText() == 'MiniVNA':
            amcp.calcParameters(port=self.minivna_port, fstart=self.f_min, fstop=self.f_max)

        # load and update plot
        data = pd.read_csv("../../vnaJ/export/scan_data.csv")
        self.plot_spectrum(frequency=data['Frequency(Hz)'], power=data['Transmission Loss(dB)'], phase=data['Phase(deg)'])


        # update progressbar 100%
        self.progressBar.setValue(100)

        # update gui
        self.update()

    def run_estimation(self):
        logging.debug('running estimation')
        self.update_log('starting frequency range estimation')
        self.update()

    def plot_spectrum(self, frequency, power, phase):
        self.graphWidget.plot(frequency, power, pen=self.pen1, clear=True)
        self.graphWidget.plot(frequency, phase, pen=self.pen2)
        self.graphWidget.setBackground('w')
        self.graphWidget.setLogMode(False, False)
        self.update()

    def update_results(self):
        self.C0_res.setText('%.1f' % self.C0)
        self.C1_res.setText('%.1f' % self.C1)
        self.L1_res.setText('%.1f' % self.L1)
        self.R1_res.setText('%.1f' % self.R1)

    def update_log(self, text='\n'):
        self.logfile.appendPlainText(text)
        self.logfile.update()
        self.logfile_small.append('> '+text)
        self.logfile_small.update()

    def run_vnaj(self):
        self.update_log('launching VnaJ')

    def export_model(self, model='spice'):
        if model == 'spice':
            self.update_log('exporting results as SPICE model')
        elif model == 'spectre':
            self.update_log('exporting results as SPECTRE model')
        else:
            self.update_log('invalid export format [spice, spectre]')

def main():
    app = QApplication(sys.argv)
    form = AmcpGui()
    form.show()
    app.exec_()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()