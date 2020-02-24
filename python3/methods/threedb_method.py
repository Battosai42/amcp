#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - -3dB Method

The -3dB method measures the -3dB bandwidth of the series resonance and derives the motional parameters from the
definition of the Q factor.
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
import support.data_management as dm

# This class is used to analyse the measurement data and calculate the crystal parameters
class ThreedbMethod:
    """
    This method uses the -3dB points below and above the series resonance frequency as well as the minimum transmission
    loss to calculate the motional elements, Q-factor and C0 of the crystal.
    """
    logger = logging.getLogger(__name__)

    # crystal model data
    Rl = 12.5                 # Source and load resistance seen by the crystal (12.5Ohm)
    C0 = 0.0                # package capacitance
    R1 = None               # Motional Resistance R1
    C1 = None               # Motional Capacitance C1
    L1 = None               # Motional Inductance L1
    Q = None                # Quality factor
    fs = None               # frequency at minimum transmission loss (series resonacne frequency)
    fp = None               # parallel resonant frequency
    ESR = None              # ESR of crystal
    Cl = None               # Load Capacitance
    reff = None             # effective resistance
    loss_min = None         # minimum transmission loss
    db3_bandwidth = None    # -3dB bandwidth of series resonance

    def __init__(self):
        super().__init__()
        self.data = None

    def _analyseData(self):
        self.loss_min = max(self.data['Transmission Loss(dB)'])
        self.logger.debug('Finding minimum loss: {}'.format(self.loss_min))
        self.fs = self.data['Frequency(Hz)'][self.data['Transmission Loss(dB)'].idxmax()]
        self.fp = self.data['Frequency(Hz)'][self.data['Transmission Loss(dB)'].idxmin()]

        db3_point = self.loss_min-3
        db3_freq = [None, None]
        try:
            for m in range(len(self.data['Transmission Loss(dB)'])):
                if (self.data['Transmission Loss(dB)'][m] <= db3_point) and (self.data['Transmission Loss(dB)'][m+1] >= db3_point):
                    db3_freq[0] = self.data['Frequency(Hz)'].iloc[m]
                    self.logger.debug('first -3dB point is at frequency: {}'.format(db3_freq[0]))
                elif (self.data['Transmission Loss(dB)'][m] >= db3_point) and (self.data['Transmission Loss(dB)'][m+1] <= db3_point):
                    db3_freq[1] = self.data['Frequency(Hz)'].iloc[m]
                    self.logger.debug('second -3dB point is at frequency: {}'.format(db3_freq[1]))
                    self.db3_bandwidth = db3_freq[1]-db3_freq[0]
                    break
        except Exception as e:
            self.logger.debug('Could not find the -3dB points in dataframe')

    def _calcR(self):
        self.R1 = 2 * self.Rl * (10 ** (abs(self.loss_min) / 20) - 1)
        self.reff = 2 * self.Rl + self.R1

    def _calcQ(self):
        self.Q = self.fs/self.db3_bandwidth

    def _calcL1(self):
        self.L1 = self.Q*self.reff/(2*np.pi*self.fs)

    def _calcC1(self):
        self.C1 = 1/(4*np.pi**2*self.fs**2*self.L1)

    def _calcC0(self):
        self.C0 = (self.C1*self.fs**2)/(self.fp**2-self.fs**2)

    def _calcESR(self):
        if self.Cl == 0:
            self.ESR = -1
        else:
            self.ESR = self.R1*(1+self.C0/self.Cl)**2

    def calcParameters(self, r_setup=12.5, cl=0):
        """
        Calculate the crystal parameters from the data given in self.data
        The results are stored in the variables self.R1, self.C1, self.L1, self.C0, self.Q, self.fs and self.fp
        :return: int:0 = no errors; str: error string is returned
        """

        self.Rl = r_setup
        self.Cl = cl*1e-12

        try:
            self._analyseData()
            self._calcR()
            self._calcQ()
            self._calcL1()
            self._calcC1()
            self._calcC0()
            self._calcESR()

            # Results
            self.logger.info('fs = {0:.0f} Hz'.format(self.fs))
            self.logger.info('fp = {0:.0f} Hz'.format(self.fp))
            self.logger.info('R1 = {0:.2f} Ohm'.format(self.R1))
            self.logger.info('L1 = {0:.3f} mH'.format(self.L1 * 1e3))
            self.logger.info('C1 = {0:.2f} fF'.format(self.C1 * 1e15))
            self.logger.info('C0 = {0:.2f} fF'.format(self.C0 * 1e15))
            self.logger.info('ESR = {0:.2f} Ohm'.format(self.ESR))
            self.logger.info('Q = {0:.0f}'.format(self.Q))
        except Exception as e:
            self.logger.debug('could not calculate parameters!')
            return 'error: could not calculate parameters'
        return 0

    def updateData(self, data=None):
        """
        The data needs to have 3 columns using the headers "Frequency(Hz)", "Transmission Loss(dB)" and "Phase(deg)"
        :param data: pandas dadaframe
        :return:
        """
        self.data = data

    def getResults(self):
        """
        Returns the crystal parameters C0, C1, L1, R1, Q, fs, fp
        :return: float: C0, C1, L1, R1, Q, fs, fp
        """
        return self.C0, self.C1, self.L1, self.R1, self.Q, self.fs, self.fp, self.ESR


def verify():
    file = '../../vnaJ/export/example_data.csv'
    data = dm.DataManagement()
    data.loadData(file=file)
    test = ThreedbMethod()
    test.updateData(data=data.data)
    test.calcParameters()

    #show(test.data)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    verify()
