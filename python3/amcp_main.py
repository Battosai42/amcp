#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - Main

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
from python3.vnaj_wrapper import vnajWrapper
from python3.nanovna import NanoVNA
from python3.amcp_basic import PhaseShiftMethod
from python3.amcp_advanced import AmcpAdv


import logging
logger = logging.getLogger(__name__)


# This class is used to analyse the measurement data and calculate the crystal parameters
class amcp(PhaseShiftMethod):

    data = None     # measurement data
    data_loc = None # location of data
    vna = None      # VNA device
    dev = None      # 0 = miniVNA tiny, 1 = nanoVNA


    def __init__(self):
        super().__init__()

    def loadData(self, file=None):
        logging.info('loading data: {}'.format(file))
        self.data = pd.read_csv(file)

    def getData(self, dev=None, fstart=None, fstop=None):
        if dev == 'miniVNA Tiny':
            logging.info('Running vnaJ-hl')
            self.vna.run_vnaJ(fstart=fstart, fstop=fstop, average=1)
            self.loadData(file=self.data_loc)
        if dev == 'nanoVNA':
            logging.info('not implemented yet')

    def runGui(self):
        logging.info('not implemented yet')

    def setDev(self, dev=None):
        if dev == 'miniVNA Tiny':
            self.vna = vnajWrapper()
        elif dev == 'nanoVNA':
            logging.info('not implemented yet')

def example():
    port = 'ttyUSB0'
    zoom = [25994500, 26004290]
    full = [25990000, 26049719]
    xtal = amcp()
    # xtal = PhaseShiftMethod(port=port, fstart=full[0], fstop=full[1])
    # xtal.printAll()
    # xtal.analyseData()
    xtal.calcParameters()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    example()