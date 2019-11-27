#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - Advanced Functions

This class contains advanced functions for amcp_basic and expands on its capabilities

"""

__author__ = "S.Blatter"
__maintainer__ = "S.Blatter"
__email__ = "maveric-@gmx.ch"
__copyright__ = "Copyright 2019"
__credits__ = ""
__license__ = "GPL 3.0"
__status__ = "Developement"
__version__ = "0.1"

import logging
from python3.amcp_basic import PhaseShiftMethod

logger = logging.getLogger(__name__)


# This class is used to analyse the measurement data and calculate the crystal parameters
class AmcpAdv(PhaseShiftMethod):

    dev = None      # 0 = miniVNA tiny, 1 = nanoVNA

    def __init__(self, dev=None, file=None, port=None, fstart=None, fstop=None, average=1):
        """
        AmcpAdv contain advanced functions to improve usability of amcp.

        :param dev: 0=miniVNA, tiny 1=nanoVNA
        :param file:
        :param port:
        :param fstart:
        :param fstop:
        :param average:
        """
        self.dev = dev
        super().__init__(file=file, port=port, fstart=fstart, fstop=fstop, average=average)


    def find_resonnance_frequency(self):
        """
        This function searches for the resonance frequency of an unknown crystal

        :return:
        """
        logging.info('not implemented yet')

    def find_band(self, fs=None):
        """
        This function calculates the ideal fmin and fmax to maximise the frequency resolution of a measurement

        :param fs: series resonance frequency
        :return:
        """
        logging.info('not implemented yet')

    def average_data(self):
        """
        This function averages multiple measurements to reduce noise in the captured data

        :return:
        """
        logging.info('not implemented yet')

    def get_full_data(self):
        """
        This function makes 2 measurements. one spanning both the series and parallel resonance frequencies to calculate
        the Capacitive and Inductive components of the xtal model. the second zoomed in around the resonance frequency
        to improve the measurement of the motional Resistance R1

        :return:
        """
        logging.info('not implemented yet')


def example():
    port = 'ttyUSB0'
    zoom = [25994500, 26004290]
    full = [25990000, 26049719]
    # xtal = PhaseShiftMethod(file='../vnaJ/export/scan_data.csv')
    xtal = AmcpAdv(port=port, fstart=full[0], fstop=full[1])
    # xtal.printAll()
    # xtal.analyseData()
    xtal.calcParameters()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    example()
