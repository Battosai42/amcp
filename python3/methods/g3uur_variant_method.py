#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - G3UUR variant Method

This method uses the series and parallel resonance frequencies to calculate the motional parameters
"""

__author__ = "S.Blatter"
__maintainer__ = "S.Blatter"
__email__ = "maveric-@gmx.ch"
__copyright__ = "Copyright 2019"
__credits__ = ""
__license__ = "GPL 3.0"
__status__ = "Developement"
__version__ = "0.1"

import numpy as np
import logging
import python3.support.data_management as dm


# This class is used to analyse the measurement data and calculate the crystal parameters
class ThreedbMethod():
    logger = logging.getLogger(__name__)

    # crystal model data
    Rl = 12.5                 # Source and load resistance seen by the crystal (12.5Ohm)
    C0 = 0.0                # package capacitance
    R1 = None               # Motional Resistance R1
    C1 = None               # Motional Capacitance C1
    L1 = None               # Motional Inductance L1
    Q = None                # Quality factor
    Cstray = None           # shunt capacitance of test fixture
    fs = None               # frequency at minimum transmission loss (series resonacne frequency)
    fp = None               # parallel resonant frequency
    reff = None             # effective resistance
    loss_min = None         # minimum transmission loss
    db3_bandwidth = None    # -3dB bandwidth of series resonance

    def __init__(self, file1=None, file2=None):
        self.data_resonance = dm.DataManagement()
        self.data_resonance.loadData(file=file1)
        self.data_stray = dm.DataManagement()
        self.data_stray.loadData(file=file2)


    def _analyseData(self):
        self.loss_min = max(self.data_resonance.data['Transmission Loss(dB)'])
        self.logger.debug('Finding minimum loss: {}'.format(self.loss_min))
        self.fs = self.data_resonance.data['Frequency(Hz)'][self.data_resonance.data['Transmission Loss(dB)'].idxmax()]
        self.fp = self.data_resonance.data['Frequency(Hz)'][self.data_resonance.data['Transmission Loss(dB)'].idxmin()]

        Xc = self.data_stray.data['Transmission Loss(dB)'][self.data_resonance.data['Transmission Loss(dB)'].idxmax()]
        self.Cstray = -1/(2*np.pi*self.fs*Xc)
        self.Cstray = 600e-15
        print(self.Cstray)

    def _calcR(self):
        self.R1 = 2 * self.Rl * (10 ** (abs(self.loss_min) / 20) - 1)
        self.reff = 2 * self.Rl + self.R1

    def _calcQ(self):
        self.Q = 2*np.pi*self.fs*self.L1/self.reff

    def _calcL1(self):
        self.L1 = 1/(4*np.pi**2*self.fs**2*self.C1)

    def _calcC1(self):
        self.C1 = (self.fp/self.fs-1)*2*(self.C0+self.Cstray)

    def _calcC0(self):
        self.C0 = (self.C1*self.fs**2)/(self.fp**2-self.fs**2)

    def calcParameters(self):
        self._analyseData()
        self._calcR()
        self._calcC1()
        self._calcL1()
        self._calcC0()
        self._calcQ()

        # Results
        self.logger.info('fs = {0:.0f} Hz'.format(self.fs))
        self.logger.info('fp = {0:.0f} Hz'.format(self.fp))
        self.logger.info('R1 = {0:.2f} Ohm'.format(self.R1))
        self.logger.info('L1 = {0:.3f} mH'.format(self.L1 * 1e3))
        self.logger.info('C1 = {0:.2f} fF'.format(self.C1 * 1e15))
        self.logger.info('C0 = {0:.2f} fF'.format(self.C0 * 1e15))
        self.logger.info('Q = {0:.0f}'.format(self.Q))

    def getResults(self):
        return self.C0, self.C1, self.L1, self.R1, self.Q, self.fs, self.fp


def verify():
    file1 = '../../vnaJ/export/example_data.csv'
    file2 = '../../vnaJ/export/example_data.csv'
    test = ThreedbMethod(file1=file1, file2=file2)
    test.calcParameters()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    verify()
