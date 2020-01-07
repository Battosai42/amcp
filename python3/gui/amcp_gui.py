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
from PyQt5.QtWidgets import QApplication, QPushButton, QFileDialog
import pyqtgraph as pg
import logging
import sys
import python3.gui.amcpg as amcp_gui
import pandas as pd
import serial
import serial.tools.list_ports
import subprocess

#import VNA wrapper
from python3.phaseshift import PhaseShiftMethod
from python3.vnaj_wrapper import vnajWrapper

class AmcpGui(QtWidgets.QMainWindow, amcp_gui.Ui_MainWindow):

    fres = 0.0
    fs = 0.0
    fp = 0.0
    Q = 0.0
    C0 = 0.0
    C1 = 0.0
    L1 = 0.0
    R1 = 0.0
    devs = []
    vna_type = ''
    minivna_port = None
    minivna_baud = 9600
    nanovna_port = None
    nanovna_baud = 9600
    vna = None
    graph = None

    export_loc = '../../vnaJ/export'
    export_data = 'scan_data'

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
        self.psm = PhaseShiftMethod(file='{}/{}.csv'.format(self.export_loc, self.export_data))

        # menu
        self.actionClose.triggered.connect(self.close)
        self.actionSave.triggered.connect(self.save_setup)
        self.actionLoad.triggered.connect(self.load_setup)
        self.actionas_SPICE_model.triggered.connect(self.save_spice_model)
        self.actionas_Spectre_model.triggered.connect(self.save_spectre_model)
        self.actionDocumentation.triggered.connect(self.open_documentation)
        self.actionAbout.triggered.connect(self.load_about)
        self.actionHelp.triggered.connect(self.help)

    def refresh_comports(self):
        devs = set(['-']+[i[0] for i in list(serial.tools.list_ports.comports())])
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
        self.update()

    def update_comports(self):
        self.minivna_port = self.sel_minivna_port.currentText().split('/')[-1]
        self.nanovna_port = self.sel_nanovna_port.currentText()
        logging.debug('miniVNA PORT:{}\nnanoVNA PORT:{}'.format(self.minivna_port, self.nanovna_port))
        self.update()

    def update_baud(self):
        self.nanovna_port = int(self.sel_nanovna_baud.currentText())

    def update_vna(self):
        self.vna_type = self.select_vna.currentText()

    def connect_vna(self):
        if self.vna_type == 'MiniVNA':
            logging.info('connecting to miniVNA')
            self.vna = vnajWrapper(java_loc=self.java_loc.text(),
                                   vnaJ_loc=self.vnajhl_loc.text(),
                                   home='../../vnaJ',
                                   export_loc=self.export_loc,
                                   PORT=self.minivna_port,
                                   data=self.export_data,
                                   cal_file=self.minivna_calfile_loc.text())
            logging.info('Connected to MiniVNA')
            self.update_log('Connected to miniVNA')
        elif self.vna_type == 'NanoVNA':
            logging.info('not implemented')

    def disconnect_vna(self):
        try:
            del self.vna
            self.update_log('Disconnecting from {}'.format(self.vna_type))
        except:
            logging.debug('disconnect failed')


    def run_measurement(self):
        logging.debug('running measurement')

        # update progressbar 0%
        self.progressBar.setValue(0)

        # Measurement Setup
        fmin = self.f_min.text()
        fmax = self.f_max.text()

        self.update_log('starting measurement using {}'.format(self.vna_type))
        self.update_log('f_min={}'.format(fmin))
        self.update_log('f_max={}'.format(fmax))

        # update progressbar 100%
        self.progressBar.setValue(10)

        # make sure the com ports are updated
        self.update_comports()

        # run measurement
        if self.select_vna.currentText() == 'MiniVNA':
            try:
                self.vna.run_vnaJ(fstart=int(float(self.f_min.text())),
                                  fstop=int(float(self.f_max.text())),
                                  average=self.minivna_averaging.currentText(),
                                  exports='csv')

                # update progressbar 50%
                self.progressBar.setValue(50)
                # load and update plot
                data = pd.read_csv("../../vnaJ/export/scan_data.csv")
                self.plot_spectrum(frequency=data['Frequency(Hz)'],
                                   power=data['Transmission Loss(dB)'],
                                   phase=data['Phase(deg)'])
            except:
                self.update_log('could not run vnaJ')

        #calculate results from data
        self.psm.calcParameters()
        self.C0, self.C1, self.L1, self.R1, self.Q, self.fs, self.fp, self.fres = self.psm.getResults()
        self.update_log('Frequerncy resolution: {}Hz'.format(self.fres))

        # update progressbar 90%
        self.progressBar.setValue(90)
        self.update_results()

        # update progressbar 100%
        self.progressBar.setValue(100)

        # update gui
        self.update()

    def run_estimation(self):
        logging.debug('running estimation')
        self.update_log('not implemented yet')
        xlimits = self.graphWidget.getPlotItem().getAxis('bottom')
        logging.debug('xlimits: {}'.format(xlimits))
        self.f_min.setText(xlimits[0])
        self.f_max.setText(xlimits[1])
        self.update()

    def plot_spectrum(self, frequency, power, phase):
        self.graphWidget.plot(frequency, power, pen=self.pen1, clear=True)
        self.graphWidget.plot(frequency, phase, pen=self.pen2)
        self.graphWidget.setBackground('w')
        self.graphWidget.setLogMode(False, False)
        self.update()

    def update_results(self):
        self.C0_res.setText('%.1f' % (self.C0*1e12))
        self.C1_res.setText('%.1f' % (self.C1*1e15))
        self.L1_res.setText('%.1f' % (self.L1*1e6))
        self.R1_res.setText('%.1f' % self.R1)
        self.Q_res.setText('%.1f' % self.Q)
        self.fs_res.setText('%.0f' % self.fs)
        self.fp_res.setText('%.0f' % self.fp)

    def update_log(self, text='\n'):
        self.logfile.appendPlainText(text)
        self.logfile.update()
        self.logfile_small.append('> '+text)
        self.logfile_small.update()

    def run_vnaj(self):
        self.update_log('launching VnaJ')
        try:
            tmp = subprocess.check_output([self.java_loc.text(), '-jar', self.vnaj_loc.text()])
        except subprocess.CalledProcessError as e:
            logging.debug('Could not run vnaj-hl! error: {}'.format(e))


    # setup page

    def open_javaloc(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        self.java_loc.setText(filename)

    def open_vnaj_loc(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        self.vnaj_loc.setText(filename)

    def open_vnajhl_loc(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        self.vnajhl_loc.setText(filename)

    def open_minivna_cal_loc(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        self.minivna_calfile_loc.setText(filename)

    def open_nanovna_wrapper_loc(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        self.nanovna_wrapper_loc.setText(filename)

    def open_nanovna_cal_loc(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        self.nanovna_calfile_loc.setText(filename)

    # menu items
    def save_setup(self):
        print('tbd save')

    def load_setup(self):
        print('tbd load')

    def save_model(self, model='spice', C0=0, C1=0, R1=0, L1=0):
        xtal_model = None
        if model == 'spice':
            self.update_log('exporting results as SPICE model')
            xtal_model = '* XTAL Model\n' \
                         '* Description: equivalent cirquit model of a crystal resonator\n' \
                         '* Generated by AMCP\n' \
                         '*\n' \
                         '* Node Assignments:\n' \
                         '*            input\n' \
                         '*            |  output\n'\
                         '*            |  |\n' \
                         '.SUBCKT xtal xi xo\n' \
                         'R1 net0 xi {}\n' \
                         'C1 net1 net0 {}\n' \
                         'C0 xo xi {}\n' \
                         'L1 xo net1 {}\n' \
                         '.ENDS'.format(R1, C1, C0, L1)
            model = ['SPICE', 'cir']
        elif model == 'spectre':
            self.update_log('exporting results as SPECTRE model')
            xtal_model = 'simulator lang=spectre\n' \
                         '#\n' \
                         '# XTAL Model\n' \
                         '# Description: equivalent cirquit model of a crystal resonator\n' \
                         '# Generated by AMCP\n' \
                         '#\n' \
                         '# Node Assignments:\n' \
                         '#           input\n' \
                         '#           |  output\n' \
                         '#           |  |\n' \
                         'subckt xtal xi xo\n' \
                         'R1 (net0 xi) r={}\n' \
                         'C1 (net1 net0) c={}\n' \
                         'C0 (xo xi) c={}\n' \
                         'L1 (xo net1) l={}\n' \
                         'ends'.format(R1, C1, C0, L1)
            model = ['Spectre', 'spectre']
        else:
            self.update_log('invalid export format [spice, spectre]')

        if xtal_model:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                      "{} Files (*.{});;All Files (*)".format(model[0],
                                                                                              model[1]),
                                                      options=options)
            if '.{}'.format(model[1]) not in fileName and fileName:
                fileName = '{}.{}'.format(fileName, model[1])

                with open(fileName, 'w', newline='') as modelwriter:
                    modelwriter.write(xtal_model)

    def save_spice_model(self):
        self.save_model(model='spice', C0=self.C0, C1=self.C1, R1=self.R1, L1=self.L1)

    def save_spectre_model(self):
        self.save_model(model='spectre', C0=self.C0, C1=self.C1, R1=self.R1, L1=self.L1)

    def open_documentation(self):
        print('tbd documentation')

    def load_about(self):
        print('tbd about')

    def help(self):
        print('tbd help')

def main():
    app = QApplication(sys.argv)
    form = AmcpGui()
    form.show()
    app.exec_()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()