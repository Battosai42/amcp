import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)


# This class is used to analyse the measurement data and calculate the crystal parameters
class PhaseShiftMethod:

    data= None
    Rl = 50                 # Source and load resistance seen by the crystal (12.5Ohm)
    Rm = None               # Motional Resistance R1
    Cm = None               # Motional Capacitance C1
    Lm = None               # Motional Inductance L1
    fs = None               # frequency at minimum transmission loss (series resonace frequency)
    loss_min = None         # minimum transmission loss
    deltaF = None           # 45 degree bandwidth
    freq_phase0 = None      # frequency at phase = 0
    loss_phase0 = None      # transmission loss at phase = 0
    fres = None             # frequency resolution

    def __init__(self, file=None):
        self.loadData(file=file)

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
        logging.debug('Frequency Resolution = {0:.2f} Hz'.format(self.fres))

        # get minimum loss
        self.loss_min = max(self.data['Transmission Loss(dB)'])
        self.fs = max(self.data['Frequency(Hz)'])

        # calculate the 45deg bandwidth
        phase = 15  # 45 degree
        freq = [0, 0]
        ampl = [0, 0]

        for i in range(2):
            if i == 0:
                tmp = self.data.iloc[(self.data['Phase(deg)'] + phase).abs().argsort()[0:2]]
            else:
                tmp = self.data.iloc[(self.data['Phase(deg)'] - phase).abs().argsort()[0:2]]
            f = list(tmp['Frequency(Hz)'])
            amp = list(tmp['Transmission Loss(dB)'])
            freq[i] = (max(f)+min(f))/2
            ampl[i] = (max(amp)+min(amp))/2

        # calculate 45 degree bandwidth
        self.deltaF = max(freq)-min(freq)
        logging.debug('freq1 = {}'.format(freq))
        logging.debug('amp1 = {}'.format(ampl))
        logging.debug('deltaF = {}'.format(self.deltaF))

        # get phase = 0 loss and frequency
        tmp = self.data.iloc[(self.data['Phase(deg)']).abs().argsort()[0:1]]
        self.freq_phase0 = list(tmp['Frequency(Hz)'])[0]
        self.loss_phase0 = list(tmp['Transmission Loss(dB)'])[0]

    def calcParameters(self):       # calculating crystal parameters

        # analyse Data
        self.analyseData()

        # Calculating Rm
        self.Rm = 2*self.Rl*(10**(-self.loss_min/20)-1)
        Reff = 2*self.Rl+self.Rm
        
        # Calculating Cm
        self.Cm = self.deltaF/(2*np.pi*self.fs**2*Reff)

        # Calculating Lm
        self.Lm = Reff/(2*np.pi*self.deltaF)

        # Results
        logging.info('Rm = {0:.2f} Ohm'.format(self.Rm))
        logging.info('fs = {0:.0f} Hz'.format(self.fs))
        logging.info('Lm = {0:.3f} mH'.format(self.Lm*1e3))
        logging.info('Cm = {0:.2f} fF'.format(self.Cm*1e15))
        return 0

def example():
    xtal = PhaseShiftMethod(file='/home/battosai/vnaJ.3.3/export/step1.csv')
    #xtal.printAll()
    #xtal.analyseData()
    xtal.calcParameters()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    example()
