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

class AmcpGui(QtWidgets.QMainWindow, amcp_gui.Ui_MainWindow):

    C0 = 0
    C1 = 0
    L1 = 0
    R1 = 0

    def __init__(self, parent=None):
        super(AmcpGui, self).__init__(parent)
        self.setupUi(self)

        # graph initialisation
        self.pen1 = pg.mkPen(color=(0, 0, 200), width=2)
        self.pen2 = pg.mkPen(color=(0, 200, 0), width=2)
        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y=True, alpha=1)



    def run_measurement(self):
        logging.debug('running measurement')

        # Measurement Setup
        fmin = self.f_min.text()
        fmax = self.f_max.text()
        self.logfile.appendPlainText('f_min={}\nf_max={}'.format(fmin, fmax))

        # VNA setup
        self.vna = self.select_vna.currentText()

        self.update_log('starting measurement using {}'.format(self.vna))
        self.update_results()

        # load and update plot
        data = pd.read_csv("../../vnaJ/export/scan_data.csv")
        self.plot_spectrum(frequency=data['Frequency(Hz)'], power=data['Transmission Loss(dB)'], phase=data['Phase(deg)'])
        self.update()

    def run_estimation(self):
        logging.debug('running estimation')
        self.update_log('starting frequency range estimation')
        self.plot_spectrum()
        self.update()

    def plot_spectrum(self, frequency, power, phase):
        self.graphWidget.plot(frequency, power, pen=self.pen1)
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

def main():
    app = QApplication(sys.argv)
    form = AmcpGui()
    form.show()
    app.exec_()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()