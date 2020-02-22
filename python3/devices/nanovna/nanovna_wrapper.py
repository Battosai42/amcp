#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - Wrapper for nanovna.py from https://github.com/ttrftech/NanoVNA

"""

__author__ = "S.Blatter"
__maintainer__ = "S.Blatter"
__email__ = "maveric-@gmx.ch"
__copyright__ = "Copyright 2019"
__credits__ = ""
__license__ = "GPL 3.0"
__status__ = "Developement"
__version__ = "0.1"

from devices.nanovna.nanovna import NanoVNA
import logging
import numpy as np
import pandas as pd
import time
logger = logging.getLogger(__name__)

class nanoVnaWrapper():

    def __init__(self):
        self.vna = NanoVNA()

    def setFrequencies(self, start=1e6, stop=900e6, points=101):
        if 0 < points <= 101:
            self.vna.set_frequencies(start=start, stop=stop, points=points)
        else:
            logger.info('"points" has to be: 0 < points <= 101')

    def getTrData(self, averaging=1):
        frequency, tr_loss, phase = self._getTrData()
        if averaging != 1:
            for n in range(averaging):
                f, t, p = self._getTrData()
                tr_loss = np.average([t, tr_loss], axis=0)
                phase = np.average([p, phase], axis=0)
        data = pd.DataFrame({'Frequency(Hz)': frequency, 'Transmission Loss(dB)': tr_loss, 'Phase(deg)': phase})
        logger.debug('created data')
        return data

    def _getTrData(self):
        self.vna.fetch_frequencies()
        #self.vna.scan()
        time.sleep(1.5)
        data = self.vna.data(1)

        frequency = self.vna.frequencies
        tr_loss = 20 * np.log10(np.abs(data))
        phase = np.angle(data)*180/np.pi

        return frequency, tr_loss, phase

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    vna = nanoVnaWrapper()
    frequency, mag, phase = vna.getTrData(averaging=2)
