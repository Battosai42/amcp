#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - Wrapper for nanoVNA

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
import time
import serial
import serial.tools.list_ports
import numpy as np

logger = logging.getLogger(__name__)

class nanoVNA_wrapper():

    _frequencies = None
    _gain = None
    _offset = None
    _power = None

    def __init__(self, dev=None):

        self.__dev = dev
        self.__resource = None
        self.__chamber = None
        self.connected = False

    def connect(self, dev=None, chamber=None, timeout=1):
        try:
            # If no device address is given, we will scan the serial bus.
            if not dev:
                logger.info("Searching for NanoVNA...")
                devs = [i[0] for i in list(serial.tools.list_ports.comports())]
                logger.debug(devs)
            else:
                # create a list with just the given device.
                devs = [dev]

            # Go through the list of device candidates.
            for dev in devs:
                try:
                    # Try to connect to the instrument...
                    logger.info("trying %s" % dev)
                    self.__resource = serial.Serial(dev)
                    self.__resource.baudrate = 9600
                    self.__resource.bytesize = 8
                    self.__resource.parity = 'N'
                    self.__resource.stopbits = 1
                    self.__resource.timeout = 1

                except serial.SerialException:
                    # if it fails, continue with the next candidate.
                    self.__resource = None
                    logger.debug("unable to connect to %s" % dev)
                    continue

                logger.info('Connection succeeded')

                try:
                    # Try to communicate with the device.
                    id_str = self._get_id()

                except:
                    # if it fails, continue with the next candidate.
                    self.__resource.close()
                    self.__resource = None
                    logger.debug("failed to read ID code from this resource")
                    continue

                if 'nanovna' in id_str.lower():
                    self.__dev = dev
                    self.connected = True
                    break
                    # If the device string is correct, we have found our device!
                else:
                    self.__resource.close()
                    self.__resource = None
                    logger.info("found wrong ID code")
                    # raise("Wrong instrument.")
                    continue
        except:
            raise Exception("Something went wrong")

        if not isinstance(self.__resource, serial.Serial):
            print("NanoVNA not found on any resource.  Is it connected and switched on?")
            raise Exception("NanoVNA not found")

# Interface Functions
# ==============================

    def _get_id(self):
        out = self._ask('info'.format())
        logging.debug('info: {}'.format(out))
        return out

    def _read(self):
        try:
            out = self.__resource.readall().decode("ascii").rstrip()
            return out
        except serial.SerialException:
            raise Exception("Can't read from NanoVNA. Device may not be connected.")

    def _write(self, string=None):
        if string:
            try:
                self.__resource.write('{}\r'.format(string).encode("ascii"))
                time.sleep(0.2)
                return
            except serial.SerialException:
                raise Exception("Can't write to NanoVNA. Device may not be connected.")
        else:
            raise Exception('Invalid Input: _write()')

    def _ask(self, string=None):
        self._write(string=string)
        out = self._read()
        return out
    
# Device Functions
# ==============================

    # functions:
    # help exit info echo systime threads reset freq offset time dac saveconfig clearconfig data dump
    # frequencies port stat sweep test touchcal touchtest pause resume cal save recall trace marker edelay

    def set_frequencies(self, center=None, span=None, start=None, stop=None):
        if isinstance(center, float) and isinstance(span, float):
            self._frequencies = np.linspace(start=center - span / 2, stop=center + span / 2, num=101)
        elif isinstance(start, float) and isinstance(stop, float):
            self._frequencies = np.linspace(start=start, stop=stop, num=101)
        else:
            raise Exception('Invalid Input: set_freq_sweep(float)')

        if self._frequencies is not None:
            logger.info('writing frequencies to device')
            freq = self._frequencies
            self._write('freq '+'Hz '.join([str(int(x)) for x in self._frequencies]))
        else:
            raise Exception("Couldn't write frequencies to device")

    def get_frequencies(self):
        if self._frequencies is not None:
            return self._frequencies
        else:
            raise Exception('Frequencies are not set!')

    def fetch_frequencies(self):
        data = self._ask('frequencies')
        self._frequencies = data
        logger.debug(data)
        return data

    def set_gain(self, gain=None):
        if isinstance(gain, float):
            self._gain = gain
            logger.info('writing gain to device')
            self._write("gain %d %d" % (gain, gain))
        else:
            raise Exception('Invalid Input: set_gain(float)')

    def get_gain(self):
        if self._gain is not None:
            return self._gain
        else:
            raise Exception('Gain is not set!')

    def set_offset(self, offset):
        if isinstance(offset, float):
            self._offset = offset
            logger.info('writing offset to device')
            self._write("offset %d" % offset)
        else:
            raise Exception('Invalid Input: set_offset(float)')

    def get_offset(self):
        if self._offset is not None:
            return self._offset
        else:
            raise Exception('Offset is not set!')

    def set_strength(self, power):
        if isinstance(power, float):
            self._power = power
            logger.info('writing power to device')
            self._write("power %d" % power)
        else:
            raise Exception('Invalid Input: set_strength(float)')

    def get_power(self):
        if self._power is not None:
            return self._power
        else:
            raise Exception('Power is not set!')


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    vna = nanoVNA_wrapper()
    vna.connect()
    vna.set_frequencies(center=50.2e6, span=2e6)
    print('frequencies '+'Hz '.join([str(int(x)) for x in vna._frequencies]))

