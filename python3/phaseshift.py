#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - Basic Functions

This class implements the analysis of the captured measurement data and calculates the motional parameters of the
crystal that is being tested. The class can be used standalone if the measurement data is already available. This
can be useful if the VNA that is being used is not supported by amcp

"""

__author__ = "S.Blatter"
__maintainer__ = "S.Blatter"
__email__ = "maveric-@gmx.ch"
__copyright__ = "Copyright 2019"
__credits__ = ""
__license__ = "GPL 3.0"
__status__ = "Developement"
__version__ = "0.1"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
from python3.vnaj_wrapper import vnajWrapper

# This class is used to analyse the measurement data and calculate the crystal parameters
class PhaseShiftMethod(vnajWrapper):

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
    
    # analysis variable
    data = None             # measurement data
    loss_min = None         # minimum transmission loss
    deltaF = None           # 45 degree bandwidth
    freq_phase0 = None      # frequency at phase = 0
    loss_phase0 = None      # transmission loss at phase = 0
    fres = None             # frequency resolution
    
    # settings
    PORT = None             # COM port of miniVNA Tiny
    fstart = None           # start frequency of measurement
    fstop = None            # stop frequency of measurement
    average = None          # measurement averaging

    def __init__(self, file=None, port=None, fstart=None, fstop=None, average=None):
        self.logger = logging.getLogger(__name__)
        if file is not None:
            self.loadData(file=file)
        elif port is not None:
            self.PORT = port
            self.fstart = fstart
            self.fstop = fstop
            self.average = average
            super().__init__(PORT=self.PORT)
            self.run_vnaJ(fstart=self.fstart, fstop=self.fstop, average=self.average)
            self.loadData(file='{}/{}.csv'.format(self.export_loc, self.data))

    def loadData(self, file=None):
        self.data = pd.read_csv(file)

    def printTransmission(self):
        fig = plt.figure()
        plt.plot(self.data['Frequency(Hz)'], self.data['Transmission Loss(dB)'])
        plt.show()

    def printAll(self):
        fig, ax1 = plt.subplots()

        ax1.plot(self.data['Frequency(Hz)'], self.data['Transmission Loss(dB)'], 'b-')
        ax1.set_xlabel('Frequency [f]')
        ax1.set_ylabel('Transmission Loss [dB]', color='b')
        ax1.tick_params('y', colors='b')

        ax2 = ax1.twinx()
        ax2.plot(self.data['Frequency(Hz)'], self.data['Phase(deg)'], 'r-')
        ax2.set_ylabel('Phase [deg]', color='r')
        ax2.tick_params('y', colors='r')

        fig.tight_layout()
        plt.show()

    def analyseData(self):      # calculating required values from measurement data
        # calculate frequency resolution
        tmp = list(self.data['Frequency(Hz)'])
        self.fres = tmp[1]-tmp[0]
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

        for m in range(len(self.data['Phase(deg)'])):
            if (self.data['Phase(deg)'][m] <= 45) and (self.data['Phase(deg)'][m-1] >= 45):
                freq[0] = (self.data['Frequency(Hz)'][m] + self.data['Frequency(Hz)'][m - 1]) / 2
                ampl[0] = (self.data['Phase(deg)'][m] + self.data['Phase(deg)'][m - 1]) / 2
                self.logger.debug('+45deg: {}'.format(self.data['Phase(deg)'][m]))

            elif (self.data['Phase(deg)'][m] <= -45) and (self.data['Phase(deg)'][m-1] >= -45):
                freq[1] = (self.data['Frequency(Hz)'][m] + self.data['Frequency(Hz)'][m - 1]) / 2
                ampl[1] = (self.data['Phase(deg)'][m] + self.data['Phase(deg)'][m - 1]) / 2
                self.logger.debug('-45deg: {}'.format(self.data['Phase(deg)'][m]))
                break


        # calculate 45 degree bandwidth
        self.deltaF = max(freq)-min(freq)
        self.logger.debug('freq1 = {}'.format(freq))
        self.logger.debug('amp1 = {}'.format(ampl))
        self.logger.debug('deltaF = {}'.format(self.deltaF))

        # get phase = 0 loss and frequency
        tmp = self.data.iloc[(self.data['Phase(deg)']).abs().argsort()[0:1]]
        self.freq_phase0 = list(tmp['Frequency(Hz)'])[0]
        self.loss_phase0 = list(tmp['Transmission Loss(dB)'])[0]

    def calcParameters(self):       # calculating crystal parameters

        # analyse Data
        self.analyseData()

        # Calculating R1
        self.calcR1()
        
        # Calculating C1
        self.calcC1()

        # Calculating L1
        self.L1 = self.reff/(2*np.pi*self.deltaF)

        # Calculating Q-factor
        self.Q = 2*np.pi*self.fs*self.L1/self.R1

        # Estimate C0
        self.C0 = (self.C1*self.fs**2)/(self.fp**2-self.fs**2)

        # Results
        self.logger.info('fs = {0:.0f} Hz'.format(self.fs))
        self.logger.info('fp = {0:.0f} Hz'.format(self.fp))
        self.logger.info('R1 = {0:.2f} Ohm'.format(self.R1))
        self.logger.info('L1 = {0:.3f} mH'.format(self.L1*1e3))
        self.logger.info('C1 = {0:.2f} fF'.format(self.C1*1e15))
        self.logger.info('C0 = {0:.2f} fF'.format(self.C0*1e15))
        self.logger.info('Q = {0:.0f}'.format(self.Q))

    def getResults(self):
        return self.C0, self.C1, self.L1, self.R1, self.Q, self.fs, self.fp, self.fres

# cleanup
    def calcR1(self):       # Calculating R1
        self.logger.debug('loss={}'.format(self.loss_min))
        self.R1 = 2 * self.Rl * (10 ** (abs(self.loss_min) / 20) - 1)
        self.reff = 2 * self.Rl + self.R1

    def calcC1(self):
        self.C1 = self.deltaF / (2 * np.pi * self.fs ** 2 * self.reff)


def example():
    port = 'ttyUSB0'
    zoom = [25994500, 26004290]
    full = [25990000, 26049719]
    #xtal = PhaseShiftMethod(file='../vnaJ/export/scan_data.csv')
    xtal = PhaseShiftMethod(port=port, fstart=full[0], fstop=full[1])
    #xtal.printAll()
    #xtal.analyseData()
    xtal.calcParameters()

def verify():
    file = '../vnaJ/export/example_data.csv'
    test = PhaseShiftMethod(file=file)
    test.calcParameters()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    verify()
