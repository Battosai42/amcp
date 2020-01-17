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

from platform import platform
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog
import pyqtgraph as pg
import logging
import sys
import python3.gui.amcpg as amcp_gui
import serial
import serial.tools.list_ports
import subprocess
import json
import os

#import VNA wrapper
from python3.methods.phaseshift_method import PhaseShiftMethod
from python3.methods.threedb_method import ThreedbMethod
from python3.vnaj_wrapper import vnajWrapper
import python3.support.data_management as dm

class AmcpGui(QtWidgets.QMainWindow, amcp_gui.Ui_MainWindow, dm.DataManagement):
    logger = logging.getLogger(__name__)

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
    method = 0      # 0: phaseshift method 1: -3dB Method

    export_loc = '../../vnaJ/export'
    export_data = 'scan_data'
    test_data = 'example_data'

    def __init__(self, parent=None):
        super(AmcpGui, self).__init__(parent)
        self.setupUi(self)

        # graph initialisation
        self.pen2 = pg.mkPen(color=(0, 0, 200), width=2)
        self.pen1 = pg.mkPen(color=(200, 0, 0), width=2)
        self.graphWidget.setBackground('w')
        self.graphWidget.showGrid(x=True, y=True, alpha=1)

        # OS specific setup
        self.os_specific_init()

        # COM ports
        self.update_comports()
        self.update_baud()

        # select VNA
        self.update_vna()

        # measurement methods
        self.export_file = '{}/{}.csv'.format(self.export_loc, self.export_data)
        self.data = self.loadData(self.export_file)
        self.psm = PhaseShiftMethod()
        self.db3 = ThreedbMethod()

        # menu
        self.actionClose.triggered.connect(self.close)
        self.actionSave.triggered.connect(self.save_setup)
        self.actionLoad.triggered.connect(self.load_setup)
        self.actionas_SPICE_model.triggered.connect(self.save_spice_model)
        self.actionas_Spectre_model.triggered.connect(self.save_spectre_model)
        self.actionDocumentation.triggered.connect(self.open_documentation)
        self.actionAbout.triggered.connect(self.load_about)
        self.actionHelp.triggered.connect(self.help)

    def os_specific_init(self):
        os = platform()
        if 'windows' in os.lower():
            self.java_loc.setText('C:/Program Files (x86)/Java/jre1.8.0_231/bin/java.exe')
        if 'linux' in os.lower():
            self.java_loc.setText('../../oracle_java/jre1.8.0_221/bin/java')

    def refresh_comports(self):
        devs = sorted(set(['-']+[i[0] for i in list(serial.tools.list_ports.comports())]))
        tmp = [item for item in set(self.devs) if not item in devs]  # list of changed ports
        self.logger.info('COM port list changes: {}'.format(tmp))
        for dev in tmp:
            if dev in self.devs:
                self.update_log(text='COM port removed: {}'.format(dev))

        tmp = [item for item in devs if not item in set(self.devs)]  # list of changed ports
        self.logger.info('COM port list changes: {}'.format(tmp))
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
        self.logger.debug('miniVNA PORT:{}\nnanoVNA PORT:{}'.format(self.minivna_port, self.nanovna_port))
        self.update()

    def update_baud(self):
        self.nanovna_port = int(self.sel_nanovna_baud.currentText())

    def update_vna(self):
        self.vna_type = self.select_vna.currentText()

    def connect_vna(self):
        if self.vna_type == 'MiniVNA':
            self.logger.info('connecting to miniVNA')
            self.vna = vnajWrapper(java_loc=self.java_loc.text(),
                                   vnaJ_loc=self.vnajhl_loc.text(),
                                   home='../../vnaJ',
                                   export_loc=self.export_loc,
                                   PORT=self.minivna_port,
                                   data=self.export_data,
                                   cal_file=self.minivna_calfile_loc.text())
            self.logger.info('Connected to MiniVNA')
            self.update_log('Connected to miniVNA')
        elif self.vna_type == 'NanoVNA':
            self.logger.info('not implemented')

    def disconnect_vna(self):
        try:
            del self.vna
            self.update_log('Disconnecting from {}'.format(self.vna_type))
        except Exception as e:
            self.logger.debug('disconnect failed:\n{}'.format(e))


    def run_measurement(self):
        self.logger.debug('running measurement')

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
                e = self.vna.run_vnaJ(fstart=int(float(self.f_min.text())),
                                      fstop=int(float(self.f_max.text())),
                                      average=self.minivna_averaging.currentText(),
                                      exports='csv')

                # update progressbar 50%
                self.progressBar.setValue(50)

                self.loadData(file=self.export_file)
                self.plot_spectrum(frequency=self.data['Frequency(Hz)'],
                                   power=self.data['Transmission Loss(dB)'],
                                   phase=self.data['Phase(deg)'])

            except Exception as e:
                self.logger.debug('error: measurement not completed:\n{}'.format(e))
                self.update_log('could not run vnaJ, loading example data')
                self.update_log('{}'.format(e))
                self.loadData('{}/{}.csv'.format(self.export_loc, self.test_data))
                self.plot_spectrum(frequency=self.data['Frequency(Hz)'],
                                   power=self.data['Transmission Loss(dB)'],
                                   phase=self.data['Phase(deg)'])

        #calculate results from data
        self.method = self.sel_method.currentText()
        if self.method == 'Phase-Shift Method':
            self.psm.updateData(data=self.data)
            self.psm.calcParameters()
            self.C0, self.C1, self.L1, self.R1, self.Q, self.fs, self.fp = self.psm.getResults()
        elif self.method == '-3dB Method':
            self.db3.updateData(data=self.data)
            self.db3.calcParameters()
            self.C0, self.C1, self.L1, self.R1, self.Q, self.fs, self.fp = self.db3.getResults()
        else:
            self.logger.debug('error: invalid calculation method used!')

        # update progressbar 90%
        self.progressBar.setValue(90)
        self.update_results()

        # update progressbar 100%
        self.progressBar.setValue(100)

        # update gui
        self.update()

    def run_estimation(self):
        self.logger.debug('running estimation')
        self.update_log('not implemented yet')
        xlimits = self.graphWidget.getPlotItem().getAxis('bottom')
        self.logger.debug('xlimits: {}'.format(xlimits))
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
        self.C0_res.setText('%.1f' % (self.C0*1e15))
        self.C1_res.setText('%.1f' % (self.C1*1e15))
        self.L1_res.setText('%.1f' % (self.L1*1e3))
        self.R1_res.setText('%.1f' % self.R1)
        self.Q_res.setText('%.1f' % self.Q)
        self.fs_res.setText('%.0f' % (self.fs/1e3))
        self.fp_res.setText('%.0f' % (self.fp/1e3))

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
            self.logger.debug('Could not run vnaj-hl! error: {}'.format(e))

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
        data = {
            'java location': self.java_loc.text(),
            'vnaJ loaction': self.vnaj_loc.text(),
            'vnaJ-hl location': self.vnajhl_loc.text(),
            'vnaJ calibration file': self.minivna_calfile_loc.text(),
            'minivna port': self.sel_minivna_port.currentText(),
            'minivna averaging': self.minivna_averaging.currentText(),
            'nanovna wrapper location': self.nanovna_wrapper_loc.text(),
            'nanovna calibration file:': self.nanovna_calfile_loc.text(),
            'nanovna port': self.sel_nanovna_port.currentText(),
            'nanovna baud': self.sel_nanovna_baud.currentText(),
            'fstart': self.f_min.text(),
            'fstop': self.f_max.text(),
            'method': self.sel_method.currentText()
        }

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", '{}/../../'.format(os.getcwd()),
                                                  "JSON Files (*.json);;All Files (*)",
                                                  options=options)
        if '.json' not in fileName and fileName:
            fileName = '{}.json'.format(fileName)
        with open(fileName, 'w') as outfile:
            json.dump(data, outfile)

    def load_setup(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileNames()", '{}/../../'.format(os.getcwd()),
                                                  "JSON Files (*.json);;All Files (*)",
                                                  options=options)
        try:
            with open(fileName) as json_file:
                data = json.load(json_file)
                self.java_loc.setText(data['java location'])
                self.vnaj_loc.setText(data['vnaJ loaction'])
                self.vnajhl_loc.setText(data['vnaJ-hl location'])
                self.minivna_calfile_loc.setText(data['vnaJ calibration file'])
                self.sel_minivna_port.setCurrentText(data['minivna port'])
                self.minivna_averaging.setCurrentText(data['minivna averaging'])
                self.nanovna_wrapper_loc.setText(data['nanovna wrapper location'])
                self.nanovna_calfile_loc.setText(data['nanovna calibration file:'])
                self.sel_nanovna_port.setCurrentText(data['nanovna port'])
                self.sel_nanovna_baud.setCurrentText(data['nanovna baud'])
                self.f_min.setText(data['fstart'])
                self.f_max.setText(data['fstop'])
                self.sel_method.setCurrentText(data['method'])
        except Exception as e:
            self.update_log('could not load file:\n{}'.format(e))

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
        self.update_log('tbd documentation')

    def load_about(self):
        self.update_log('tbd about')

    def help(self):
        self.update_log('tbd help')

def main():
    app = QApplication(sys.argv)
    form = AmcpGui()
    form.show()
    app.exec_()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()