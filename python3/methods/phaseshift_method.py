#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - Phaseshift Method
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
class PhaseShiftMethod(dm.DataManagement):
    """
    This methods uses the minimum transmission loss at the series resonance frequency and the +/- 45° phase points
    around the series resonance frequency to calculate the motional elements, Q-factor and C0 of the crystal.
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
    reff = None             # effective resistance
    loss_min = None         # minimum transmission loss
    db3_bandwidth = None    # -3dB bandwidth of series resonance

    def __init__(self):
        super().__init__()
        self.data = None

    def _analyseData(self):
        # calculate frequency resolution
        tmp = list(self.data['Frequency(Hz)'])
        self.fres = tmp[1] - tmp[0]
        self.logger.debug('Frequency Resolution = {0:.2f} Hz'.format(self.fres))

        # get minimum loss
        self.loss_min = max(self.data['Transmission Loss(dB)'])

        # get resonance frequencies
        self.fs = self.data['Frequency(Hz)'][self.data['Transmission Loss(dB)'].idxmax()]
        self.fp = self.data['Frequency(Hz)'][self.data['Transmission Loss(dB)'].idxmin()]
        self.logger.debug('fs = {}'.format(self.fs))
        self.logger.debug('fp = {}'.format(self.fp))

        # calculate the 45deg bandwidth
        phase = 45  # 45 degree
        freq = [0, 0]
        ampl = [0, 0]

        try:
            for m in range(len(self.data['Phase(deg)'])):
                if (self.data['Phase(deg)'][m] <= 45) and (self.data['Phase(deg)'][m - 1] >= 45):
                    freq[0] = (self.data['Frequency(Hz)'][m] + self.data['Frequency(Hz)'][m - 1]) / 2
                    ampl[0] = (self.data['Phase(deg)'][m] + self.data['Phase(deg)'][m - 1]) / 2
                    self.logger.debug('+45deg: {}'.format(self.data['Phase(deg)'][m]))

                elif (self.data['Phase(deg)'][m] <= -45) and (self.data['Phase(deg)'][m - 1] >= -45):
                    freq[1] = (self.data['Frequency(Hz)'][m] + self.data['Frequency(Hz)'][m - 1]) / 2
                    ampl[1] = (self.data['Phase(deg)'][m] + self.data['Phase(deg)'][m - 1]) / 2
                    self.logger.debug('-45deg: {}'.format(self.data['Phase(deg)'][m]))
                    break
        except Exception as e:
            self.logger.debug('could not find +/-45° points')

        # calculate 45 degree bandwidth
        self.deltaF = max(freq)-min(freq)
        self.logger.debug('freq1 = {}'.format(freq))
        self.logger.debug('amp1 = {}'.format(ampl))
        self.logger.debug('deltaF = {}'.format(self.deltaF))

        # get phase = 0 loss and frequency
        tmp = self.data.iloc[(self.data['Phase(deg)']).abs().argsort()[0:1]]
        self.freq_phase0 = list(tmp['Frequency(Hz)'])[0]
        self.loss_phase0 = list(tmp['Transmission Loss(dB)'])[0]

    def _calcR(self):
        self.R1 = 2 * self.Rl * (10 ** (abs(self.loss_min) / 20) - 1)
        self.reff = 2 * self.Rl + self.R1

    def _calcQ(self):
        self.Q = 2 * np.pi * self.fs * self.L1 / self.reff

    def _calcL1(self):
        self.L1 = self.reff / (2 * np.pi * self.deltaF)

    def _calcC1(self):
        self.C1 = self.deltaF / (2 * np.pi * self.fs ** 2 * self.reff)

    def _calcC0(self):
        self.C0 = (self.C1 * self.fs ** 2) / (self.fp ** 2 - self.fs ** 2)

    def calcParameters(self):
        """
        Calculate the crystal parameters from the data given in self.data
        The results are stored in the variables self.R1, self.C1, self.L1, self.C0, self.Q, self.fs and self.fp
        :return: int:0 = no errors; str: error string is returned
        """
        try:
            self._analyseData()
            self._calcR()
            self._calcC1()
            self._calcL1()
            self._calcQ()
            self._calcC0()

            # Results
            self.logger.info('fs = {0:.0f} Hz'.format(self.fs))
            self.logger.info('fp = {0:.0f} Hz'.format(self.fp))
            self.logger.info('R1 = {0:.2f} Ohm'.format(self.R1))
            self.logger.info('L1 = {0:.3f} mH'.format(self.L1 * 1e3))
            self.logger.info('C1 = {0:.2f} fF'.format(self.C1 * 1e15))
            self.logger.info('C0 = {0:.2f} fF'.format(self.C0 * 1e15))
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
        return self.C0, self.C1, self.L1, self.R1, self.Q, self.fs, self.fp


def verify():
    file = '../../vnaJ/export/example_data.csv'
    data = dm.DataManagement()
    data.loadData(file=file)
    test = PhaseShiftMethod()
    test.updateData(data=data.data)
    test.calcParameters()

    #show(test.data)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    verify()
