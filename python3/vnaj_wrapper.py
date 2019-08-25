#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Automated Crystal Parameter Measurement - Wrapper for vnaJ-hl

This class runs the vnaJ-hl.jar java program and saves the results of the measurement in csv format for further
processing. For this to work vnaJ requires the proper setup scripts set up in advance and placed in the vnaJ
working directory

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
import subprocess

logger = logging.getLogger(__name__)


class vnajWrapper():

    java_loc = '/home/battosai/vnaJ/oracle_java/jre1.8.0_221/bin/java'
    vnaj_loc = '../vnaJ/vnaJ-hl.3.2.10.jar'

    def run_vnaJ(self):
        # run vnaJ-hl using the setup previously done
        try:
            tmp = subprocess.check_output([self.java_loc, '-jar', self.vnaj_loc])
            logging.info(tmp)
        except subprocess.CalledProcessError as e:
            logging.debug('Could not run vnaj-hl! error: {}'.format(e))


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)

    minivna = vnajWrapper()
    minivna.run_vnaJ()
