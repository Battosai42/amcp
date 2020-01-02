from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QPushButton
import pyqtgraph as pg
import logging
import sys
import python3.gui.amcpg as amcp_gui
import csv

class AmcpGui(QtWidgets.QMainWindow, amcp_gui.Ui_MainWindow):

    C0 = 0
    C1 = 0
    L1 = 0
    R1 = 0

    def __init__(self, parent=None):
        super(AmcpGui, self).__init__(parent)
        self.setupUi(self)

        # graph initialisation
        self.pen = pg.mkPen(color=(255, 0, 0), width=2)
        self.graphWidget.setBackground('w')



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
        self.update()

    def run_estimation(self):
        logging.debug('running estimation')
        self.update_log('starting frequency range estimation')
        self.plot_spectrum()
        self.update()

    def plot_spectrum(self, frequency=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], power=[30, 32, 34, 32, 33, 31, 29, 32, 35, 45]):
        self.graphWidget.plot(frequency, power, pen=self.pen)
        self.graphWidget.setBackground('w')
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